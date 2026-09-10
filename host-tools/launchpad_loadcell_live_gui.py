#!/usr/bin/env python3
"""
Unified EtherCAT live GUI for load-cell and EEA reverse-engineering.

What this does:
- Reuses the known-good ATI load-cell lane.
- Adds an EEA reverse-engineering lane in the same GUI.
- Adds direct control hooks: PDO output write and SDO read/write.
"""

from __future__ import annotations

from collections import deque
import csv
import json
import math
import os
import queue
import re
import struct
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk
from typing import Any

import pysoem
try:
    import numpy as np
    from scipy import signal as scipy_signal
except Exception:
    np = None
    scipy_signal = None
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    import orjson as _orjson
    def _json_dumps(obj: dict) -> str:
        return _orjson.dumps(obj).decode()
except ImportError:
    _orjson = None  # type: ignore[assignment]
    def _json_dumps(obj: dict) -> str:
        return json.dumps(obj, separators=(",", ":"))

try:
    import psutil as _psutil
    _PSUTIL_PROC = _psutil.Process()
except ImportError:
    _psutil = None  # type: ignore[assignment]
    _PSUTIL_PROC = None  # type: ignore[assignment]

try:
    from tsdownsample import MinMaxLTTBDownsampler as _TsDownsampler
    _TSDS = _TsDownsampler()
except ImportError:
    _TSDS = None  # type: ignore[assignment]

try:
    import serial
    import serial.tools.list_ports as _serial_list_ports
    _SERIAL_AVAILABLE = True
except ImportError:
    serial = None  # type: ignore[assignment]
    _serial_list_ports = None  # type: ignore[assignment]
    _SERIAL_AVAILABLE = False

LIVE_DOWNSAMPLE_THRESHOLD = 2000  # downsample live plot when points exceed this
ADAPTIVE_MEM_HIGH_MB = 800        # slow analysis redraws above this RSS
ADAPTIVE_MEM_CRITICAL_MB = 1400   # force-trim log + maximum slowdown above this

from ati_ft_testbench import ATI_PRODUCT_CODE, ATI_VENDOR_ID

# ATI F/T raw integer counts → engineering units (N / N·mm)
LOADCELL_SCALE = 1e-6

UI_TICK_MS = 120
MIN_DRAW_INTERVAL_S = 0.01
ANALYSIS_UPDATE_INTERVAL_S = 2.0
MIN_PERIOD_MS = 1.0
LOG_EVERY_N_SAMPLES = 20
MAX_LOG_MESSAGES_PER_TICK = 120
MAX_LOG_LINES = 6000
LOG_TRIM_TO_LINES = 4000
STATE_FILE = Path(__file__).with_name(".launchpad_loadcell_live_gui_adapter.txt")
DEFAULT_ADAPTER_HINT = "Realtek USB 2.5GbE Family Controller"
DEFAULT_PERIOD_MS = 1000.0
TIMEOUT_US = 50000
# Approximate in-memory ring buffer budget (all history deques together).
BUFFER_BUDGET_MB = 50
# 14 numeric values are stored per sample across live+analysis deques.
# Python object + deque overhead is significant; this is a practical estimate.
EST_BYTES_PER_SAMPLE_ALL_DEQUES = 384
MAX_HISTORY_SAMPLES = max(
    20000,
    int((BUFFER_BUDGET_MB * 1024 * 1024) / EST_BYTES_PER_SAMPLE_ALL_DEQUES),
)
GRAPH_HISTORY = MAX_HISTORY_SAMPLES
ANALYSIS_HISTORY = MAX_HISTORY_SAMPLES

PROFILE_LOADCELL = "ATI Load Cell"
PROFILE_EEA_RE = "EEA Reverse Engineering"


@dataclass
class DecodeResult:
    ok: bool
    fields: dict[str, float]
    line: str


@dataclass
class Metrics:
    connected: bool = False
    status: str = "Disconnected"
    lines_total: int = 0
    errors_total: int = 0
    dropouts_total: int = 0
    last_wkc: int | None = None
    last_raw_hex: str = "-"
    last_line: str = "-"


class EthercatLiveGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("LaunchPad EtherCAT Live GUI (Load Cell + EEA)")
        self.root.geometry("1260x860")

        self.q: queue.Queue[tuple[str, str]] = queue.Queue()
        self.stop_evt = threading.Event()
        self.worker_stop_evt = threading.Event()

        # Serial monitor state
        self._serial_port: Any = None
        self._serial_stop_evt = threading.Event()
        self._serial_thread: threading.Thread | None = None
        self._serial_q: queue.Queue[str] = queue.Queue(maxsize=4096)
        self._serial_log_fh = None  # open file handle for serial CSV log
        self._ser_text: "scrolledtext.ScrolledText | None" = None  # built lazily in _build_serial_tab
        self.worker_thread: threading.Thread | None = None
        self.history_lock = threading.Lock()

        self.master: pysoem.Master | None = None
        self.target_slave: pysoem.CdefSlave | None = None
        self.secondary_slave: pysoem.CdefSlave | None = None  # second ATI slave for dual capture

        self.adapter_var = tk.StringVar(value="")
        self.period_var = tk.StringVar(value=str(DEFAULT_PERIOD_MS))
        self.profile_var = tk.StringVar(value=PROFILE_LOADCELL)
        self.slave_hint_var = tk.StringVar(value="")

        _default_cap = Path(__file__).resolve().parent.parent / "reports" / "host_master"
        _run_ts = time.strftime("%Y%m%d_%H%M%S")
        self.capture_path_var = tk.StringVar(
            value=str((_default_cap / f"loadcell_slave1_{_run_ts}.csv").resolve())
        )
        self.capture2_path_var = tk.StringVar(
            value=str((_default_cap / f"loadcell_slave2_{_run_ts}.csv").resolve())
        )
        self.secondary_wkc_var = tk.StringVar(value="WKC2: -")
        self.capture_enabled_var = tk.BooleanVar(value=False)
        self._capture_enabled: bool = False  # thread-safe mirror
        self.analysis_window_var = tk.StringVar(value="256")
        self.baseline_status_var = tk.StringVar(value="Baseline: not captured")

        period_override = os.getenv("LC_GUI_PERIOD_MS", "").strip()
        if period_override:
            self.period_var.set(period_override)

        slave_hint_override = os.getenv("LC_GUI_SLAVE_HINT", "").strip()
        if slave_hint_override:
            self.slave_hint_var.set(slave_hint_override)

        capture_override = os.getenv("LC_GUI_CAPTURE", "").strip().lower()
        if capture_override in ("1", "true", "yes"):
            self.capture_enabled_var.set(True)
            self._capture_enabled = True

        self.status_var = tk.StringVar(value="Status: Disconnected")
        self.wkc_var = tk.StringVar(value="WKC: -")
        self.count_var = tk.StringVar(value="Samples: 0 | Errors: 0")
        self.raw_var = tk.StringVar(value="Raw: -")
        self.last_line_var = tk.StringVar(value="Decoded: -")

        self.pdo_hex_var = tk.StringVar(value="")
        self.sdo_idx_var = tk.StringVar(value="0x2000")
        self.sdo_sub_var = tk.StringVar(value="0x00")
        self.sdo_type_var = tk.StringVar(value="u32")
        self.sdo_value_var = tk.StringVar(value="0")

        self.adapter_name_by_label: dict[str, str] = {}
        self.metrics = Metrics()
        self.sample_index = 0
        self.last_draw_ts = 0.0
        self.last_draw_sample = -1
        self.last_analysis_ts = 0.0
        self.analysis_baseline: dict[str, tuple[float, float]] = {}
        self._mem_mb: float = 0.0
        self._last_mem_check_ts: float = 0.0

        self.debug_stdout = os.getenv("LC_GUI_DEBUG_STDOUT", "0").strip() == "1"
        self.debug_prev_ts: float | None = None
        self.debug_last_report_ts = time.time()
        self.debug_cycle_samples = 0
        self.debug_cycle_drops = 0
        self.debug_cycle_dt_min_ms = float("inf")
        self.debug_cycle_dt_max_ms = 0.0
        self.debug_cycle_dt_sum_ms = 0.0
        self._loaded_from_csv = False

        self.x_history: deque[float] = deque(maxlen=GRAPH_HISTORY)  # wall-clock timestamps
        self.c1_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self.c2_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self.c3_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self.c4_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self.c5_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self.c6_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self.analysis_t_history: deque[float] = deque(maxlen=ANALYSIS_HISTORY)
        self.analysis_c1_history: deque[float] = deque(maxlen=ANALYSIS_HISTORY)
        self.analysis_c2_history: deque[float] = deque(maxlen=ANALYSIS_HISTORY)
        self.analysis_c3_history: deque[float] = deque(maxlen=ANALYSIS_HISTORY)
        self.analysis_c4_history: deque[float] = deque(maxlen=ANALYSIS_HISTORY)
        self.analysis_c5_history: deque[float] = deque(maxlen=ANALYSIS_HISTORY)
        self.analysis_c6_history: deque[float] = deque(maxlen=ANALYSIS_HISTORY)
        # Thermal / environmental sensor history (from serial monitor)
        self._ser_ts_history:  deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._ser_T_history:   deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._ser_co2_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._ser_H_history:   deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._ser_aqi_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._ser_tvoc_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._ser_tdelta_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._ser_motion_history: deque[float] = deque(maxlen=GRAPH_HISTORY)
        self._esp32_t4c_last = math.nan
        self._esp32_t4f_last = math.nan
        self._connect_ts: float = 0.0  # wall time of last connect, for relative x-axis

        self._build_ui()
        self.refresh_adapters()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(150, self.auto_connect_on_startup)
        self.root.after(600, self._serial_autostart_on_startup)  # Auto-connect serial after brief delay
        self.root.after(UI_TICK_MS, self.ui_tick)

        auto_close_s = os.getenv("LC_GUI_AUTO_CLOSE_S", "").strip()
        if auto_close_s:
            try:
                auto_s = max(1.0, float(auto_close_s))
                self.enqueue("info", f"Debug auto-close active: {auto_s:.1f}s")
                self.root.after(int(auto_s * 1000), self.on_close)
            except Exception:
                pass

        # Serial auto-connect via env vars (LC_GUI_SERIAL_PORT / LC_GUI_SERIAL_LOG)
        _ser_port_env = os.getenv("LC_GUI_SERIAL_PORT", "").strip()
        _ser_log_env  = os.getenv("LC_GUI_SERIAL_LOG", "").strip().lower()
        if _ser_port_env and _SERIAL_AVAILABLE:
            self.root.after(600, lambda: self._serial_autostart(_ser_port_env, _ser_log_env in ("1", "true", "yes")))
        if os.getenv("LC_GUI_SERIAL_TAB", "").strip().lower() in ("1", "true", "yes"):
            self.root.after(900, lambda: self.tabs.select(self.serial_tab))

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")

        ttk.Label(top, text="Adapter:").pack(side="left")
        self.adapter_combo = ttk.Combobox(top, textvariable=self.adapter_var, width=54, state="readonly")
        self.adapter_combo.pack(side="left", padx=(6, 8), fill="x", expand=True)
        self.adapter_combo.bind("<<ComboboxSelected>>", self.on_adapter_selected)

        ttk.Button(top, text="Refresh", command=self.refresh_adapters).pack(side="left", padx=(0, 8))

        ttk.Label(top, text="Profile:").pack(side="left")
        self.profile_combo = ttk.Combobox(
            top,
            textvariable=self.profile_var,
            values=[PROFILE_LOADCELL, PROFILE_EEA_RE],
            width=24,
            state="readonly",
        )
        self.profile_combo.pack(side="left", padx=(6, 8))

        ttk.Label(top, text="Period ms:").pack(side="left")
        ttk.Entry(top, textvariable=self.period_var, width=8).pack(side="left", padx=(6, 10))

        self.connect_btn = ttk.Button(top, text="Connect", command=self.toggle_connect)
        self.connect_btn.pack(side="left", padx=(0, 8))
        ttk.Button(top, text="Clear", command=self.clear_log).pack(side="left")
        ttk.Button(top, text="Load Saved CSV", command=self.load_saved_csv).pack(side="left", padx=(8, 0))

        # ── main tabs — right under adapter strip for maximum content area ──
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.live_tab = ttk.Frame(self.tabs)
        self.analysis_tab = ttk.Frame(self.tabs)
        self.serial_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.live_tab, text="  Live  ")
        self.tabs.add(self.analysis_tab, text="  Analysis  ")
        self.tabs.add(self.serial_tab, text="  Serial Monitor  ")

        # ── Live tab ───────────────────────────────────────────────────────────
        status = ttk.LabelFrame(self.live_tab, text="Live Status", padding=8)
        status.pack(fill="x", padx=0, pady=(4, 4))

        ttk.Label(status, textvariable=self.status_var).grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.wkc_var).grid(row=0, column=1, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.secondary_wkc_var).grid(row=0, column=2, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.count_var).grid(row=1, column=0, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.raw_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.last_line_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=2)

        cap = ttk.LabelFrame(self.live_tab, text="EEA Reverse-Engineering Capture", padding=8)
        cap.pack(fill="x", padx=0, pady=(0, 4))
        ttk.Checkbutton(cap, text="Enable CSV capture", variable=self.capture_enabled_var).grid(row=0, column=0, sticky="w", padx=6)
        ttk.Label(cap, text="Slave 1 CSV:").grid(row=0, column=1, sticky="e", padx=6)
        ttk.Entry(cap, textvariable=self.capture_path_var, width=80).grid(row=0, column=2, sticky="we", padx=6)
        ttk.Label(cap, text="Slave 2 CSV:").grid(row=1, column=1, sticky="e", padx=6)
        ttk.Entry(cap, textvariable=self.capture2_path_var, width=80).grid(row=1, column=2, sticky="we", padx=6)
        cap.columnconfigure(2, weight=1)

        ctrl = ttk.LabelFrame(self.live_tab, text="Control Hooks (PDO + SDO)", padding=8)
        ctrl.pack(fill="x", padx=0, pady=(0, 4))

        ttk.Label(ctrl, text="Slave name contains (optional):").grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ttk.Entry(ctrl, textvariable=self.slave_hint_var, width=34).grid(row=0, column=1, sticky="w", padx=6, pady=2)

        ttk.Label(ctrl, text="PDO output hex:").grid(row=0, column=2, sticky="e", padx=6, pady=2)
        ttk.Entry(ctrl, textvariable=self.pdo_hex_var, width=54).grid(row=0, column=3, sticky="we", padx=6, pady=2)
        ttk.Button(ctrl, text="Send PDO", command=self.send_pdo_hex).grid(row=0, column=4, sticky="w", padx=6, pady=2)

        ttk.Label(ctrl, text="SDO idx:").grid(row=1, column=0, sticky="e", padx=6, pady=2)
        ttk.Entry(ctrl, textvariable=self.sdo_idx_var, width=10).grid(row=1, column=1, sticky="w", padx=6, pady=2)
        ttk.Label(ctrl, text="sub:").grid(row=1, column=2, sticky="e", padx=6, pady=2)
        ttk.Entry(ctrl, textvariable=self.sdo_sub_var, width=8).grid(row=1, column=3, sticky="w", padx=6, pady=2)

        ttk.Label(ctrl, text="type:").grid(row=1, column=4, sticky="e", padx=6, pady=2)
        ttk.Combobox(ctrl, textvariable=self.sdo_type_var, values=["u8", "u16", "u32", "i32", "f32"], width=8, state="readonly").grid(
            row=1, column=5, sticky="w", padx=6, pady=2
        )
        ttk.Label(ctrl, text="value:").grid(row=1, column=6, sticky="e", padx=6, pady=2)
        ttk.Entry(ctrl, textvariable=self.sdo_value_var, width=20).grid(row=1, column=7, sticky="w", padx=6, pady=2)

        ttk.Button(ctrl, text="SDO Read", command=self.sdo_read).grid(row=1, column=8, sticky="w", padx=6, pady=2)
        ttk.Button(ctrl, text="SDO Write", command=self.sdo_write).grid(row=1, column=9, sticky="w", padx=6, pady=2)
        ctrl.columnconfigure(3, weight=1)

        graph_frame = ttk.LabelFrame(self.live_tab, text="Live Graph (Force / Torque / Thermal)", padding=8)
        graph_frame.pack(fill="both", expand=False, padx=0, pady=(0, 4))

        self.figure = Figure(figsize=(11, 7.0), dpi=100)
        _live_gs = self.figure.add_gridspec(4, 1, hspace=0.58)
        self.top_ax      = self.figure.add_subplot(_live_gs[0])
        self.bot_ax      = self.figure.add_subplot(_live_gs[1])
        self.thermal_4c_ax = self.figure.add_subplot(_live_gs[2])
        self.thermal_4f_ax = self.figure.add_subplot(_live_gs[3])
        self.thermal_ax_co2 = self.thermal_4c_ax.twinx()  # disturbance on 4C right axis

        self.top_ax.set_title("Force (Fx Fy Fz)")
        self.bot_ax.set_title("Torque (Tx Ty Tz)")
        self.thermal_4c_ax.set_title("Temp 4C (LTC2990 @ 0x4C)")
        self.thermal_4f_ax.set_title("Temp 4F (LTC2990 @ 0x4F)")
        self.thermal_4f_ax.set_xlabel("time (s)")

        (self.c1_line,) = self.top_ax.plot([], [], label="F1")
        (self.c2_line,) = self.top_ax.plot([], [], label="F2")
        (self.c3_line,) = self.top_ax.plot([], [], label="F3")
        (self.c4_line,) = self.bot_ax.plot([], [], label="T4")
        (self.c5_line,) = self.bot_ax.plot([], [], label="T5")
        (self.c6_line,) = self.bot_ax.plot([], [], label="T6")
        (self.thermal_T4C_line,)    = self.thermal_4c_ax.plot([], [], color="#f38ba8", label="Temp 4C")
        (self.thermal_T4F_line,)    = self.thermal_4f_ax.plot([], [], color="#89b4fa", label="Temp 4F")
        (self.thermal_motion_line,) = self.thermal_ax_co2.plot([], [], color="#f9e2af", linestyle="--", label="Disturbance")

        self.top_ax.legend(loc="upper left", ncols=3, fontsize=8)
        self.bot_ax.legend(loc="upper left", ncols=3, fontsize=8)
        self.thermal_4c_ax.legend(handles=[self.thermal_T4C_line, self.thermal_motion_line], loc="upper left", ncols=2, fontsize=8)
        self.thermal_4c_ax.set_ylabel("Temp (°C)", fontsize=8)
        self.thermal_ax_co2.set_ylabel("Disturbance", fontsize=8)
        self.thermal_4f_ax.legend(handles=[self.thermal_T4F_line], loc="upper left", fontsize=8)
        self.thermal_4f_ax.set_ylabel("Temp (°C)", fontsize=8)
        for ax in (self.top_ax, self.bot_ax, self.thermal_4c_ax, self.thermal_4f_ax):
            ax.grid(True, alpha=0.3)
        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        log_frame = ttk.LabelFrame(self.live_tab, text="Live Stream", padding=8)
        log_frame.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self.log = scrolledtext.ScrolledText(log_frame, wrap="none", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)

        # ── Analysis tab ───────────────────────────────────────────────────────
        analysis_ctrl = ttk.LabelFrame(self.analysis_tab, text="Analysis Controls", padding=8)
        analysis_ctrl.pack(fill="x", padx=0, pady=(4, 4))
        ttk.Label(analysis_ctrl, text="Window samples:").grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ttk.Entry(analysis_ctrl, textvariable=self.analysis_window_var, width=10).grid(row=0, column=1, sticky="w", padx=6, pady=2)
        ttk.Button(analysis_ctrl, text="Capture Baseline (No Load)", command=self.capture_noise_baseline).grid(
            row=0, column=2, sticky="w", padx=6, pady=2
        )
        ttk.Button(analysis_ctrl, text="Clear Baseline", command=self.clear_noise_baseline).grid(row=0, column=3, sticky="w", padx=6, pady=2)
        ttk.Label(analysis_ctrl, textvariable=self.baseline_status_var).grid(row=1, column=0, columnspan=4, sticky="w", padx=6, pady=2)

        analysis_plot_frame = ttk.Frame(self.analysis_tab)
        analysis_plot_frame.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self.analysis_fig = Figure(figsize=(13, 11), dpi=96)
        self.analysis_fig.patch.set_facecolor("#1e1e2e")
        gs = self.analysis_fig.add_gridspec(
            6, 3, hspace=0.72, wspace=0.38,
            left=0.07, right=0.97, top=0.96, bottom=0.04
        )
        _ax_kw = dict(facecolor="#2a2a3e")
        self.ax_hist       = self.analysis_fig.add_subplot(gs[0, 0], **_ax_kw)
        self.ax_stats      = self.analysis_fig.add_subplot(gs[0, 1], **_ax_kw)
        self.ax_noise      = self.analysis_fig.add_subplot(gs[0, 2], **_ax_kw)
        self.ax_sr         = self.analysis_fig.add_subplot(gs[1, 0:3], **_ax_kw)
        self.ax_ch1        = self.analysis_fig.add_subplot(gs[2, 0], **_ax_kw)
        self.ax_ch2        = self.analysis_fig.add_subplot(gs[2, 1], **_ax_kw)
        self.ax_ch3        = self.analysis_fig.add_subplot(gs[2, 2], **_ax_kw)
        self.ax_ch4        = self.analysis_fig.add_subplot(gs[3, 0], **_ax_kw)
        self.ax_ch5        = self.analysis_fig.add_subplot(gs[3, 1], **_ax_kw)
        self.ax_ch6        = self.analysis_fig.add_subplot(gs[3, 2], **_ax_kw)
        self.ax_thermal    = self.analysis_fig.add_subplot(gs[4, 0:3], **_ax_kw)
        self.ax_thermal_4f = self.analysis_fig.add_subplot(gs[5, 0:3], **_ax_kw)

        _title_kw = dict(color="#cdd6f4", fontsize=9, pad=3)
        for ax, title in [
            (self.ax_hist,       "Amplitude histogram"),
            (self.ax_stats,      "Stats: mean / std / rms"),
            (self.ax_noise,      "Noise vs baseline (σ ratio)"),
            (self.ax_sr,         "Sample rate (Hz)"),
            (self.ax_ch1,        "F1 — Fx"),
            (self.ax_ch2,        "F2 — Fy"),
            (self.ax_ch3,        "F3 — Fz"),
            (self.ax_ch4,        "T4 — Tx"),
            (self.ax_ch5,        "T5 — Ty"),
            (self.ax_ch6,        "T6 — Tz"),
            (self.ax_thermal,    "Thermal 4C + disturbance — same time window"),
            (self.ax_thermal_4f, "Thermal 4F — same time window"),
        ]:
            ax.set_title(title, **_title_kw)
            ax.tick_params(colors="#a6adc8", labelsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor("#45475a")

        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, master=analysis_plot_frame)
        self.analysis_canvas.get_tk_widget().pack(fill="both", expand=True)

        # ── Serial Monitor tab ─────────────────────────────────────────────────
        self._build_serial_tab()

    def _build_serial_tab(self) -> None:
        tab = self.serial_tab
        if not _SERIAL_AVAILABLE:
            ttk.Label(tab, text="pyserial not installed. Run: pip install pyserial").pack(padx=20, pady=20)
            return

        # ── Connection row ────────────────────────────────────────────────────
        conn_fr = ttk.LabelFrame(tab, text="Connection", padding=8)
        conn_fr.pack(fill="x", padx=4, pady=(4, 2))

        ttk.Label(conn_fr, text="Port:").grid(row=0, column=0, sticky="e", padx=4)
        self._ser_port_var = tk.StringVar(value="COM12")
        self._ser_port_combo = ttk.Combobox(conn_fr, textvariable=self._ser_port_var, width=18, state="readonly")
        self._ser_port_combo.grid(row=0, column=1, sticky="w", padx=4)

        ttk.Button(conn_fr, text="Refresh", command=self._serial_refresh_ports).grid(row=0, column=2, padx=4)

        ttk.Label(conn_fr, text="Baud:").grid(row=0, column=3, sticky="e", padx=4)
        self._ser_baud_var = tk.StringVar(value="115200")
        ttk.Combobox(
            conn_fr, textvariable=self._ser_baud_var,
            values=["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"],
            width=10, state="readonly"
        ).grid(row=0, column=4, sticky="w", padx=4)

        ttk.Label(conn_fr, text="Line ending:").grid(row=0, column=5, sticky="e", padx=4)
        self._ser_eol_var = tk.StringVar(value="CRLF")
        ttk.Combobox(
            conn_fr, textvariable=self._ser_eol_var,
            values=["CRLF", "LF", "CR", "None"],
            width=6, state="readonly"
        ).grid(row=0, column=6, sticky="w", padx=4)

        self._ser_connect_btn = ttk.Button(conn_fr, text="Connect", command=self._serial_toggle_connect)
        self._ser_connect_btn.grid(row=0, column=7, padx=8)

        self._ser_status_var = tk.StringVar(value="Disconnected")
        ttk.Label(conn_fr, textvariable=self._ser_status_var, foreground="gray").grid(row=0, column=8, sticky="w", padx=4)
        conn_fr.columnconfigure(8, weight=1)

        # ── Log to file row ───────────────────────────────────────────────────
        log_fr = ttk.LabelFrame(tab, text="Log to file", padding=8)
        log_fr.pack(fill="x", padx=4, pady=(0, 2))

        _ser_log_dir = Path(__file__).resolve().parent.parent / "reports" / "host_master"
        _ser_ts = time.strftime("%Y%m%d_%H%M%S")
        self._ser_log_enabled_var = tk.BooleanVar(value=False)
        self._ser_log_path_var = tk.StringVar(value=str(_ser_log_dir / f"serial_log_{_ser_ts}.csv"))
        ttk.Checkbutton(log_fr, text="Enable log", variable=self._ser_log_enabled_var,
                        command=self._serial_toggle_log).grid(row=0, column=0, sticky="w", padx=4)
        ttk.Label(log_fr, text="File:").grid(row=0, column=1, sticky="e", padx=4)
        ttk.Entry(log_fr, textvariable=self._ser_log_path_var, width=90).grid(row=0, column=2, sticky="we", padx=4)
        log_fr.columnconfigure(2, weight=1)

        # ── Send row ──────────────────────────────────────────────────────────
        send_fr = ttk.Frame(tab)
        send_fr.pack(fill="x", padx=4, pady=(0, 2))

        ttk.Label(send_fr, text="Send:").grid(row=0, column=0, sticky="e", padx=4)
        self._ser_send_var = tk.StringVar()
        send_entry = ttk.Entry(send_fr, textvariable=self._ser_send_var, width=80)
        send_entry.grid(row=0, column=1, sticky="we", padx=4)
        send_entry.bind("<Return>", lambda _e: self._serial_send())
        ttk.Button(send_fr, text="Send", command=self._serial_send).grid(row=0, column=2, padx=4)
        ttk.Button(send_fr, text="Clear", command=self._serial_clear).grid(row=0, column=3, padx=4)
        send_fr.columnconfigure(1, weight=1)

        # ── Heater control row ────────────────────────────────────────────────
        heat_fr = ttk.LabelFrame(tab, text="Heater Relay (Pin 13) & Cycle Control", padding=8)
        heat_fr.pack(fill="x", padx=4, pady=(0, 2))

        self._heater_state_var = tk.StringVar(value="Unknown")
        ttk.Label(heat_fr, text="State:").grid(row=0, column=0, sticky="e", padx=4)
        self._heater_state_lbl = ttk.Label(heat_fr, textvariable=self._heater_state_var, width=10, foreground="gray")
        self._heater_state_lbl.grid(row=0, column=1, sticky="w", padx=4)

        self._heater_on_btn = ttk.Button(
            heat_fr, text="Heater ON",
            command=lambda: self._heater_set(True),
            style="Accent.TButton" if "Accent.TButton" in ttk.Style().theme_names() else "TButton",
        )
        self._heater_on_btn.grid(row=0, column=2, padx=8)
        self._heater_off_btn = ttk.Button(heat_fr, text="Heater OFF", command=lambda: self._heater_set(False))
        self._heater_off_btn.grid(row=0, column=3, padx=4)
        ttk.Label(heat_fr, text="Hold at (C):", foreground="#a6adc8", font=("Consolas", 8)).grid(
            row=0, column=4, sticky="e", padx=(10, 4)
        )
        self._heater_hold_temp_var = tk.StringVar(value="55")
        ttk.Entry(heat_fr, textvariable=self._heater_hold_temp_var, width=8, font=("Consolas", 9)).grid(
            row=0, column=5, sticky="w", padx=4
        )
        self._heater_hold_btn = ttk.Button(heat_fr, text="Start Hold", command=self._heater_hold_toggle)
        self._heater_hold_btn.grid(row=0, column=6, padx=8)
        self._heater_hold_active = False

        # Cycle control row
        ttk.Label(heat_fr, text="Cycle ON (sec):", foreground="#a6adc8", font=("Consolas", 8)).grid(row=1, column=0, sticky="e", padx=4, pady=(8, 0))
        self._heater_on_duration_var = tk.StringVar(value="5000")
        ttk.Entry(heat_fr, textvariable=self._heater_on_duration_var, width=10, font=("Consolas", 9)).grid(row=1, column=1, sticky="w", padx=4, pady=(8, 0))

        ttk.Label(heat_fr, text="Cycle OFF (sec):", foreground="#a6adc8", font=("Consolas", 8)).grid(row=1, column=2, sticky="e", padx=4, pady=(8, 0))
        self._heater_off_duration_var = tk.StringVar(value="10000")
        ttk.Entry(heat_fr, textvariable=self._heater_off_duration_var, width=10, font=("Consolas", 9)).grid(row=1, column=3, sticky="w", padx=4, pady=(8, 0))

        self._heater_cycle_btn = ttk.Button(heat_fr, text="Start Cycle", command=self._heater_start_cycle)
        self._heater_cycle_btn.grid(row=1, column=4, padx=8, pady=(8, 0))
        self._heater_cycle_running = False
        self._heater_cycle_stop_evt = threading.Event()

        ttk.Label(heat_fr, text="Sends 'HEATER ON' / 'HEATER OFF' over serial", foreground="#888888", font=("Consolas", 7)).grid(
            row=2, column=0, columnspan=5, sticky="w", padx=4, pady=(4, 0)
        )

        # ── Terminal display ──────────────────────────────────────────────────
        self._ser_text = scrolledtext.ScrolledText(tab, wrap="none", font=("Consolas", 10), background="#1e1e1e", foreground="#d4d4d4", maxundo=0)
        self._ser_text.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self._ser_text.configure(state="disabled")
        self._ser_text.tag_configure("ts", foreground="#888888")
        self._ser_text.tag_configure("rx", foreground="#9cdcfe")
        self._ser_text.tag_configure("tx", foreground="#ce9178")
        self._ser_text.tag_configure("err", foreground="#f44747")

        self._serial_refresh_ports()

    # ── Serial helpers ─────────────────────────────────────────────────────────

    def _serial_autostart(self, port: str, enable_log: bool) -> None:
        """Called after startup delay to auto-connect serial port from env var."""
        self._ser_port_var.set(port)
        self._serial_connect()
        if enable_log and self._serial_port is not None:
            self._ser_log_enabled_var.set(True)
            self._serial_toggle_log()

    def _serial_autostart_on_startup(self) -> None:
        """Auto-connect to default serial port (COM12) on startup."""
        if not _SERIAL_AVAILABLE or self._ser_port_var.get().strip():
            return
        port = self._ser_port_var.get().strip() or "COM12"
        if port:
            self._serial_connect()

    def _serial_refresh_ports(self) -> None:
        if not _SERIAL_AVAILABLE:
            return
        ports = [p.device for p in _serial_list_ports.comports()]
        self._ser_port_combo["values"] = ports
        current = self._ser_port_var.get()
        if current in ports:
            return
        if "COM12" in ports:
            self._ser_port_var.set("COM12")
            return
        if ports:
            self._ser_port_var.set(ports[0])

    def _serial_toggle_connect(self) -> None:
        if self._serial_port is not None and self._serial_port.is_open:
            self._serial_disconnect("Manual disconnect")
        else:
            self._serial_connect()

    def _serial_connect(self) -> None:
        if not _SERIAL_AVAILABLE:
            return
        port = self._ser_port_var.get().strip()
        baud = int(self._ser_baud_var.get())
        if not port:
            self._ser_append("err", "No port selected\n")
            return
        try:
            sp = serial.Serial(port, baudrate=baud, timeout=0.05)
            self._serial_port = sp
            self._serial_stop_evt.clear()
            self._serial_thread = threading.Thread(target=self._serial_reader, daemon=True)
            self._serial_thread.start()
            self._ser_status_var.set(f"Connected  {port}  {baud} baud")
            self._ser_connect_btn.configure(text="Disconnect")
            self._ser_append("rx", f"[connected: {port} @ {baud}]\n")
        except Exception as exc:
            self._ser_append("err", f"[connect failed: {exc}]\n")
            self._ser_status_var.set(f"Error: {exc}")

    def _serial_disconnect(self, reason: str = "Disconnect") -> None:
        self._serial_stop_evt.set()
        sp = self._serial_port
        self._serial_port = None
        if sp:
            try:
                sp.close()
            except Exception:
                pass
        self._serial_toggle_log_off()
        self._ser_status_var.set("Disconnected")
        self._ser_connect_btn.configure(text="Connect")
        self._ser_append("err", f"[{reason}]\n")

    def _serial_reader(self) -> None:
        sp = self._serial_port
        while not self._serial_stop_evt.is_set() and sp and sp.is_open:
            try:
                raw_line = sp.readline()
                if not raw_line:
                    continue
                text = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                try:
                    self._serial_q.put_nowait(text)
                except queue.Full:
                    pass  # drop line rather than crash reader
            except Exception as exc:
                try:
                    self._serial_q.put_nowait(f"[read error: {exc}]")
                except queue.Full:
                    pass
                break

    def _serial_send(self) -> None:
        sp = self._serial_port
        if sp is None or not sp.is_open:
            return
        text = self._ser_send_var.get()
        eol_map = {"CRLF": "\r\n", "LF": "\n", "CR": "\r", "None": ""}
        eol = eol_map.get(self._ser_eol_var.get(), "\r\n")
        try:
            sp.write((text + eol).encode("utf-8", errors="replace"))
            ts = time.strftime("%H:%M:%S")
            self._ser_append("tx", f"[{ts}] TX> {text}\n")
            self._ser_send_var.set("")
        except Exception as exc:
            self._ser_append("err", f"[send error: {exc}]\n")

    def _serial_send_raw(self, text: str) -> None:
        """Send a command string without touching the send-entry field."""
        sp = self._serial_port
        if sp is None or not sp.is_open:
            self._ser_append("err", "[not connected — cannot send command]\n")
            return
        try:
            sp.write((text + "\r\n").encode("utf-8", errors="replace"))
            ts = time.strftime("%H:%M:%S")
            self._ser_append("tx", f"[{ts}] TX> {text}\n")
        except Exception as exc:
            self._ser_append("err", f"[send error: {exc}]\n")

    def _heater_set(self, on: bool) -> None:
        cmd = "HEATER ON" if on else "HEATER OFF"
        self._serial_send_raw(cmd)
        self._heater_state_var.set("ON" if on else "OFF")
        self._heater_state_lbl.configure(foreground="#f38ba8" if on else "#89dceb")

    def _heater_hold_toggle(self) -> None:
        """Toggle firmware-side heater hold control at a target temperature."""
        if self._heater_hold_active:
            self._serial_send_raw("HEATER HOLD OFF")
            self._heater_hold_active = False
            self._heater_hold_btn.configure(text="Start Hold")
            self._heater_state_var.set("OFF")
            self._heater_state_lbl.configure(foreground="#89dceb")
            return

        try:
            hold_c = float(self._heater_hold_temp_var.get().strip())
            if hold_c < 0.0 or hold_c > 100.0:
                self._ser_append("err", "[hold temp must be between 0 and 100 C]\n")
                return
        except ValueError:
            self._ser_append("err", "[invalid hold temperature]\n")
            return

        # Hold control supersedes cycle control.
        if self._heater_cycle_running:
            self._heater_cycle_stop_evt.set()
            self._heater_cycle_running = False
            self._heater_cycle_btn.configure(text="Start Cycle")

        self._serial_send_raw(f"HEATER HOLD {hold_c:.1f}")
        self._heater_hold_active = True
        self._heater_hold_btn.configure(text="Stop Hold")
        self._heater_state_var.set(f"HOLD {hold_c:.1f}C")
        self._heater_state_lbl.configure(foreground="#f9e2af")

    def _heater_start_cycle(self) -> None:
        """Start heater on/off cycle with user-specified durations."""
        if self._heater_cycle_running:
            self._heater_cycle_stop_evt.set()
            self._heater_cycle_running = False
            self._heater_cycle_btn.configure(text="Start Cycle")
            self._ser_append("info", "[heater cycle stopped]\n")
            return
        try:
            on_dur = float(self._heater_on_duration_var.get())
            off_dur = float(self._heater_off_duration_var.get())
            if on_dur <= 0 or off_dur <= 0:
                self._ser_append("err", "[invalid durations: must be > 0]\n")
                return
        except ValueError:
            self._ser_append("err", "[invalid heater cycle durations]\n")
            return

        # Cycle control supersedes hold control.
        if self._heater_hold_active:
            self._serial_send_raw("HEATER HOLD OFF")
            self._heater_hold_active = False
            self._heater_hold_btn.configure(text="Start Hold")

        self._heater_cycle_stop_evt.clear()
        self._heater_cycle_running = True
        self._heater_cycle_btn.configure(text="Stop Cycle")
        threading.Thread(target=self._heater_cycle_thread, args=(on_dur, off_dur), daemon=True).start()

    def _heater_cycle_thread(self, on_dur: float, off_dur: float) -> None:
        """Background thread for heater on/off cycling."""
        self._ser_append("info", f"[heater cycle: ON {on_dur}s, OFF {off_dur}s]\n")
        try:
            while not self._heater_cycle_stop_evt.is_set():
                self._heater_set(True)
                for _ in range(int(on_dur * 10)):
                    if self._heater_cycle_stop_evt.is_set():
                        return
                    time.sleep(0.1)
                self._heater_set(False)
                for _ in range(int(off_dur * 10)):
                    if self._heater_cycle_stop_evt.is_set():
                        return
                    time.sleep(0.1)
        finally:
            self._heater_cycle_running = False
            self._heater_cycle_btn.configure(text="Start Cycle")

    def _serial_clear(self) -> None:
        if self._ser_text is None:
            return
        self._ser_text.configure(state="normal")
        self._ser_text.delete("1.0", "end")
        self._ser_text.configure(state="disabled")

    def _ser_append(self, tag: str, text: str) -> None:
        if self._ser_text is None:
            return
        self._ser_text.configure(state="normal")
        self._ser_text.insert("end", text, (tag,))
        self._ser_text.see("end")
        self._ser_text.configure(state="disabled")

    def _serial_toggle_log(self) -> None:
        if self._ser_log_enabled_var.get():
            path = Path(self._ser_log_path_var.get().strip())
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                self._serial_log_fh = path.open("a", newline="", encoding="utf-8")
                # Write CSV header if new file.
                if path.stat().st_size == 0:
                    self._serial_log_fh.write("timestamp,line\n")
                self._ser_append("rx", f"[logging to: {path}]\n")
            except Exception as exc:
                self._ser_log_enabled_var.set(False)
                self._ser_append("err", f"[log open failed: {exc}]\n")
        else:
            self._serial_toggle_log_off()

    def _serial_toggle_log_off(self) -> None:
        if self._serial_log_fh is not None:
            try:
                self._serial_log_fh.close()
            except Exception:
                pass
            self._serial_log_fh = None
        self._ser_log_enabled_var.set(False)

    def profile_is_loadcell(self) -> bool:
        return self.profile_var.get() == PROFILE_LOADCELL

    def load_saved_adapter_label(self) -> str:
        try:
            return STATE_FILE.read_text(encoding="utf-8").strip()
        except Exception:
            return ""

    def save_selected_adapter_label(self) -> None:
        label = self.adapter_var.get().strip()
        if not label:
            return
        try:
            STATE_FILE.write_text(label + "\n", encoding="utf-8")
        except Exception:
            pass

    def on_adapter_selected(self, _event: object | None = None) -> None:
        self.save_selected_adapter_label()

    def refresh_adapters(self) -> None:
        self.adapter_name_by_label.clear()
        labels: list[str] = []

        for adapter in pysoem.find_adapters():
            name = str(adapter.name)
            desc = str(adapter.desc)
            label = f"{desc} | {name}"
            labels.append(label)
            self.adapter_name_by_label[label] = name

        self.adapter_combo["values"] = labels

        if not labels:
            self.adapter_var.set("")
            return

        saved = self.load_saved_adapter_label()
        current = self.adapter_var.get()
        if current in labels:
            return
        if saved in labels:
            self.adapter_var.set(saved)
            return

        for label in labels:
            if DEFAULT_ADAPTER_HINT.lower() in label.lower():
                self.adapter_var.set(label)
                return

        self.adapter_var.set(labels[0])

    def auto_connect_on_startup(self) -> None:
        if self.metrics.connected:
            return
        if not self.adapter_var.get().strip():
            self.enqueue("warn", "No adapter available for auto-connect")
            return
        self.connect()

    def toggle_connect(self) -> None:
        if self.metrics.connected:
            self.disconnect("Manual disconnect")
        else:
            self.connect()

    def _find_target_slave(self, master: pysoem.Master) -> pysoem.CdefSlave:
        hint = self.slave_hint_var.get().strip().lower()
        slaves = list(master.slaves)
        if not slaves:
            raise RuntimeError("No EtherCAT slaves discovered")

        if self.profile_is_loadcell():
            ati_slaves = [
                s
                for s in slaves
                if (s.man == ATI_VENDOR_ID and s.id == ATI_PRODUCT_CODE)
                or ("ati ethercat f/t sensor" in str(s.name).lower())
            ]
            if not ati_slaves:
                raise RuntimeError("ATI load-cell slave not found")

            # hint can be 1-based index (e.g., "2") or part of device name.
            if hint:
                if hint.isdigit():
                    idx = int(hint) - 1
                    if 0 <= idx < len(ati_slaves):
                        return ati_slaves[idx]
                    raise RuntimeError(f"ATI load-cell index out of range: {hint} (found {len(ati_slaves)})")
                by_name = [s for s in ati_slaves if hint in str(s.name).lower()]
                if by_name:
                    return by_name[0]
                raise RuntimeError(f"ATI load-cell hint not matched: {hint}")

            if len(ati_slaves) > 1:
                self.enqueue("warn", f"Multiple ATI slaves found ({len(ati_slaves)}); using first. Set 'Slave name contains' to 1/2/... to select.")
            return ati_slaves[0]

        # EEA reverse-engineering profile:
        if hint:
            for s in slaves:
                if hint in str(s.name).lower():
                    return s

        # Default EEA heuristic: prefer first non-ATI slave, else first slave.
        for s in slaves:
            if not (s.man == ATI_VENDOR_ID and s.id == ATI_PRODUCT_CODE):
                return s
        return slaves[0]

    def connect(self) -> None:
        adapter_label = self.adapter_var.get().strip()
        adapter_name = self.adapter_name_by_label.get(adapter_label, "")
        if not adapter_name:
            self.enqueue("warn", "No adapter selected")
            return

        try:
            period_ms = float(self.period_var.get().strip())
            if period_ms < MIN_PERIOD_MS:
                self.enqueue("warn", f"Period too small ({period_ms} ms). Clamped to {MIN_PERIOD_MS} ms for stable sampling.")
                period_ms = MIN_PERIOD_MS
                self.period_var.set(f"{MIN_PERIOD_MS:.3f}")
        except Exception as exc:
            self.enqueue("error", f"Invalid period ms: {exc}")
            return

        self.disconnect("Reconnect")

        try:
            master = pysoem.Master()
            master.open(adapter_name)
            slave_count = master.config_init()
            if slave_count <= 0:
                raise RuntimeError(f"No EtherCAT slaves detected (config_init={slave_count})")

            target_slave = self._find_target_slave(master)

            master.config_map()
            master.state = pysoem.SAFEOP_STATE
            master.write_state()
            master.state_check(pysoem.SAFEOP_STATE, TIMEOUT_US)
            master.send_processdata()
            master.receive_processdata(TIMEOUT_US)
            master.state = pysoem.OP_STATE
            master.write_state()
            master.state_check(pysoem.OP_STATE, TIMEOUT_US)

            # Find optional secondary ATI slave for dual-capture.
            secondary_slave: pysoem.CdefSlave | None = None
            if self.profile_is_loadcell():
                all_ati = [
                    s for s in master.slaves
                    if (s.man == ATI_VENDOR_ID and s.id == ATI_PRODUCT_CODE)
                    or ("ati ethercat f/t sensor" in str(s.name).lower())
                ]
                for s in all_ati:
                    if s is not target_slave:
                        secondary_slave = s
                        break

            self.master = master
            self.target_slave = target_slave
            self.secondary_slave = secondary_slave
            self.metrics = Metrics(connected=True, status=f"Connected ({adapter_name})")
            self._connect_ts = time.time()
            self.save_selected_adapter_label()

            self.worker_stop_evt = threading.Event()
            self.worker_thread = threading.Thread(target=self.reader_loop, args=(period_ms / 1000.0,), daemon=True)
            self.worker_thread.start()

            sec_msg = f" + secondary='{secondary_slave.name}'" if secondary_slave else " (no secondary slave)"
            self.enqueue(
                "info",
                f"Connected: profile={self.profile_var.get()} slave='{target_slave.name}' man=0x{target_slave.man:08X} prod=0x{target_slave.id:08X}{sec_msg}",
            )
        except Exception as exc:
            self.metrics.errors_total += 1
            self.enqueue("error", f"Connect failed: {exc}")
            self.disconnect("Connect failed")

    def disconnect(self, reason: str) -> None:
        self.worker_stop_evt.set()

        master = self.master
        self.master = None
        self.target_slave = None
        self.secondary_slave = None

        if master is not None:
            try:
                master.state = pysoem.INIT_STATE
                master.write_state()
            except Exception:
                pass
            try:
                master.close()
            except Exception:
                pass

        self.metrics.connected = False
        self.metrics.status = f"Disconnected ({reason})"
        self.metrics.last_wkc = None
        self.metrics.last_raw_hex = "-"
        self.metrics.last_line = "-"
        self.sample_index = 0
        with self.history_lock:
            self.x_history.clear()
            self.c1_history.clear()
            self.c2_history.clear()
            self.c3_history.clear()
            self.c4_history.clear()
            self.c5_history.clear()
            self.c6_history.clear()
            self.analysis_t_history.clear()
            self.analysis_c1_history.clear()
            self.analysis_c2_history.clear()
            self.analysis_c3_history.clear()
            self.analysis_c4_history.clear()
            self.analysis_c5_history.clear()
            self.analysis_c6_history.clear()
            self._ser_ts_history.clear()
            self._ser_T_history.clear()
            self._ser_co2_history.clear()
            self._ser_H_history.clear()
            self._ser_aqi_history.clear()
            self._ser_tvoc_history.clear()
            self._ser_tdelta_history.clear()
            self._ser_motion_history.clear()
            self._esp32_t4c_last = math.nan
            self._esp32_t4f_last = math.nan

    @staticmethod
    def _parse_sensor_line(line: str) -> dict[str, float]:
        vals: dict[str, float] = {}
        # Supports compact token stream like:
        # T:30.4/28.735 H:42.1/41.9 AQI:1/1.2 CO2:458/468.8 TVOC:120/118.0 N:279
        for m in re.finditer(r"([A-Z0-9]+):([-\d.]+)/(?:[-\d.]+)", line):
            key = m.group(1)
            try:
                vals[key] = float(m.group(2))
            except Exception:
                continue
        return vals

    def _extract_serial_values(self, line: str) -> dict[str, float]:
        vals: dict[str, float] = {}

        # ESP32S3 diode sensor line examples:
        # [4C_DIODE] D1=689.12mV D2=712.55mV TINT=31.72C
        # [4F_DIODE] D1=690.40mV D2=713.81mV TINT=32.04C
        d = re.match(r"\[(4[CF])_DIODE\].*?D1=([-\d.]+)mV\s+D2=([-\d.]+)mV\s+TINT=([-\d.]+)C", line)
        if d:
            tag = d.group(1)
            t_int = float(d.group(4))
            # Ignore clearly implausible temperature noise, but allow hot operation.
            if 10.0 <= t_int <= 100.0:
                if tag == "4C":
                    self._esp32_t4c_last = t_int
                elif tag == "4F":
                    self._esp32_t4f_last = t_int

        # Disturbance events from touch callback and accel availability heartbeat.
        if re.match(r"\[TOUCH\]", line):
            vals["MOTION"] = 1.0
        _s = re.match(r"\[SENSOR\].*ACC=([^\s]+)", line)
        if _s:
            vals["MOTION"] = 1.0 if _s.group(1) != "NONE" else 0.0

        # Sync heater state label from firmware echo.
        _h = re.match(r"\[HEATER\]\s+(ON|OFF)", line)
        if _h and hasattr(self, "_heater_state_var"):
            _state = _h.group(1)
            self._heater_state_var.set(_state)
            self._heater_state_lbl.configure(foreground="#f38ba8" if _state == "ON" else "#89dceb")

        if math.isfinite(self._esp32_t4c_last):
            vals["T4C"] = self._esp32_t4c_last
        if math.isfinite(self._esp32_t4f_last):
            vals["T4F"] = self._esp32_t4f_last

        return vals

    def decode_loadcell(self, raw: bytes, wkc: int) -> DecodeResult:
        if len(raw) < 24:
            return DecodeResult(False, {}, f"decode_failed len={len(raw)}")
        try:
            fx, fy, fz, tx, ty, tz = struct.unpack_from("<6i", raw, 0)
        except struct.error:
            return DecodeResult(False, {}, "decode_failed struct")

        s = LOADCELL_SCALE
        fields = {
            "Fx": float(fx) * s,
            "Fy": float(fy) * s,
            "Fz": float(fz) * s,
            "Tx": float(tx) * s,
            "Ty": float(ty) * s,
            "Tz": float(tz) * s,
        }
        line = (
            f"LOADCELL n={self.metrics.lines_total + 1:04d} ts={time.time():.3f} wkc={wkc} "
            f"Fx={fields['Fx']:.6f} Fy={fields['Fy']:.6f} Fz={fields['Fz']:.6f} "
            f"Tx={fields['Tx']:.6f} Ty={fields['Ty']:.6f} Tz={fields['Tz']:.6f}"
        )
        return DecodeResult(True, fields, line)

    def decode_eea_reverse(self, raw: bytes, wkc: int) -> DecodeResult:
        # Reverse-engineering decoder: extract several structured views from same payload.
        if len(raw) < 12:
            return DecodeResult(False, {}, f"decode_failed len={len(raw)}")

        fields: dict[str, float] = {}
        line_parts = [f"EEA_RE n={self.metrics.lines_total + 1:04d} ts={time.time():.3f} wkc={wkc} len={len(raw)}"]

        if len(raw) >= 24:
            vals32 = struct.unpack_from("<6i", raw, 0)
            for i, v in enumerate(vals32, start=1):
                fields[f"C{i}"] = float(v)
                line_parts.append(f"C{i}={v}")
        elif len(raw) >= 12:
            vals16 = struct.unpack_from("<6h", raw, 0)
            for i, v in enumerate(vals16, start=1):
                fields[f"C{i}"] = float(v)
                line_parts.append(f"C{i}={v}")

        line_parts.append(f"raw0={raw[:16].hex()}")
        return DecodeResult(True, fields, " ".join(line_parts))

    def _write_capture_row(self, path_str: str, wkc: int, raw: bytes, decoded: DecodeResult) -> None:
        try:
            path = Path(path_str)
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            write_header = not path.exists()
            with path.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["timestamp", "profile", "wkc", "raw_hex", "decoded_json"])
                writer.writerow(
                    [
                        f"{time.time():.6f}",
                        self.profile_var.get(),
                        wkc,
                        raw.hex(),
                        _json_dumps(decoded.fields),
                    ]
                )
        except Exception as exc:
            self.enqueue("warn", f"Capture write failed: {exc}")

    def _capture_sample(self, wkc: int, raw: bytes, decoded: DecodeResult) -> None:
        if not self._capture_enabled:
            return
        self._write_capture_row(self.capture_path_var.get().strip(), wkc, raw, decoded)

    def reader_loop(self, period_s: float) -> None:
        # Use monotonic scheduling to avoid burst/catch-up artifacts in the stream.
        next_cycle = time.perf_counter()
        cycle_timeout_us = max(1000, min(TIMEOUT_US, int(period_s * 1_000_000 * 1.5)))
        while not self.stop_evt.is_set() and not self.worker_stop_evt.is_set():
            master = self.master
            target_slave = self.target_slave
            if master is None or target_slave is None:
                return

            try:
                now = time.perf_counter()
                if now < next_cycle:
                    time.sleep(next_cycle - now)
                elif now - next_cycle > period_s:
                    # If we're late by more than one cycle, realign instead of bursting.
                    next_cycle = now

                master.send_processdata()
                wkc = int(master.receive_processdata(cycle_timeout_us))
                raw = bytes(target_slave.input)

                # WKC <= 0 means this cycle did not complete correctly; skip decode/plot.
                if wkc <= 0:
                    self.metrics.errors_total += 1
                    self.metrics.dropouts_total += 1
                    self.debug_cycle_drops += 1
                    self.metrics.last_wkc = wkc
                    self.metrics.last_raw_hex = "-"
                    self.metrics.last_line = f"DROP n={self.metrics.lines_total + 1:04d} ts={time.time():.3f} wkc={wkc}"
                    if self.metrics.dropouts_total % 20 == 1:
                        self.enqueue("warn", f"Intermittent link dropout: wkc={wkc} (drops={self.metrics.dropouts_total})")
                    next_cycle += period_s
                    continue

                if self.profile_is_loadcell():
                    decoded = self.decode_loadcell(raw, wkc)
                else:
                    decoded = self.decode_eea_reverse(raw, wkc)

                self.metrics.last_wkc = wkc
                self.metrics.last_raw_hex = raw[:32].hex(" ") if raw else ""

                if not decoded.ok:
                    self.metrics.errors_total += 1
                    self.enqueue("warn", decoded.line)
                else:
                    self.metrics.lines_total += 1
                    self.sample_index += 1
                    self.metrics.last_line = decoded.line
                    if (self.sample_index % LOG_EVERY_N_SAMPLES) == 0:
                        self.enqueue("line", decoded.line)
                    self.debug_cycle_samples += 1

                    c1 = decoded.fields.get("Fx", decoded.fields.get("C1", 0.0))
                    c2 = decoded.fields.get("Fy", decoded.fields.get("C2", 0.0))
                    c3 = decoded.fields.get("Fz", decoded.fields.get("C3", 0.0))
                    c4 = decoded.fields.get("Tx", decoded.fields.get("C4", 0.0))
                    c5 = decoded.fields.get("Ty", decoded.fields.get("C5", 0.0))
                    c6 = decoded.fields.get("Tz", decoded.fields.get("C6", 0.0))

                    now_ts = time.time()
                    with self.history_lock:
                        self.x_history.append(now_ts)  # wall-clock time
                        self.c1_history.append(float(c1))
                        self.c2_history.append(float(c2))
                        self.c3_history.append(float(c3))
                        self.c4_history.append(float(c4))
                        self.c5_history.append(float(c5))
                        self.c6_history.append(float(c6))
                        self.analysis_t_history.append(now_ts)
                        self.analysis_c1_history.append(float(c1))
                        self.analysis_c2_history.append(float(c2))
                        self.analysis_c3_history.append(float(c3))
                        self.analysis_c4_history.append(float(c4))
                        self.analysis_c5_history.append(float(c5))
                        self.analysis_c6_history.append(float(c6))

                        if self.debug_prev_ts is not None:
                            dt_ms = (now_ts - self.debug_prev_ts) * 1000.0
                            self.debug_cycle_dt_sum_ms += dt_ms
                            self.debug_cycle_dt_min_ms = min(self.debug_cycle_dt_min_ms, dt_ms)
                            self.debug_cycle_dt_max_ms = max(self.debug_cycle_dt_max_ms, dt_ms)
                        self.debug_prev_ts = now_ts

                    self._capture_sample(wkc, raw, decoded)

                # Dual-slave secondary capture (same EtherCAT cycle, separate CSV).
                secondary = self.secondary_slave
                if secondary is not None and self.profile_is_loadcell() and self._capture_enabled:
                    raw2 = bytes(secondary.input)
                    dec2 = self.decode_loadcell(raw2, wkc)
                    if dec2.ok:
                        self._write_capture_row(self.capture2_path_var.get().strip(), wkc, raw2, dec2)

                if self.debug_stdout:
                    now_wall = time.time()
                    elapsed = now_wall - self.debug_last_report_ts
                    if elapsed >= 1.0:
                        mean_dt = (
                            self.debug_cycle_dt_sum_ms / max(1, self.debug_cycle_samples - 1)
                            if self.debug_cycle_samples > 1
                            else 0.0
                        )
                        min_dt = self.debug_cycle_dt_min_ms if self.debug_cycle_dt_min_ms != float("inf") else 0.0
                        rate_hz = self.debug_cycle_samples / elapsed
                        print(
                            "[dbg] "
                            f"period_ms={period_s * 1000.0:.3f} "
                            f"timeout_us={cycle_timeout_us} "
                            f"samples={self.debug_cycle_samples} "
                            f"drops={self.debug_cycle_drops} "
                            f"rate_hz={rate_hz:.1f} "
                            f"dt_ms(min/mean/max)={min_dt:.3f}/{mean_dt:.3f}/{self.debug_cycle_dt_max_ms:.3f}",
                            flush=True,
                        )
                        self.debug_last_report_ts = now_wall
                        self.debug_cycle_samples = 0
                        self.debug_cycle_drops = 0
                        self.debug_cycle_dt_min_ms = float("inf")
                        self.debug_cycle_dt_max_ms = 0.0
                        self.debug_cycle_dt_sum_ms = 0.0

                next_cycle += period_s
            except Exception as exc:
                self.metrics.errors_total += 1
                self.enqueue("error", f"Read failed: {exc}")
                self.disconnect("Read failed")
                return

    def _require_slave(self) -> pysoem.CdefSlave:
        if self.target_slave is None:
            raise RuntimeError("No connected slave")
        return self.target_slave

    def send_pdo_hex(self) -> None:
        try:
            slave = self._require_slave()
            master = self.master
            if master is None:
                raise RuntimeError("Master not connected")

            text = self.pdo_hex_var.get().strip().replace(" ", "")
            if not text:
                raise RuntimeError("Provide hex bytes first")
            payload = bytes.fromhex(text)

            out_len = len(bytes(slave.output))
            if out_len <= 0:
                raise RuntimeError("Slave output PDO length is zero")

            if len(payload) < out_len:
                payload = payload + bytes(out_len - len(payload))
            elif len(payload) > out_len:
                payload = payload[:out_len]

            slave.output = payload
            master.send_processdata()
            wkc = master.receive_processdata(TIMEOUT_US)
            self.enqueue("info", f"PDO write sent ({len(payload)} bytes), wkc={wkc}")
        except Exception as exc:
            self.enqueue("error", f"PDO write failed: {exc}")

    def _parse_index_sub(self) -> tuple[int, int]:
        idx = int(self.sdo_idx_var.get().strip(), 0)
        sub = int(self.sdo_sub_var.get().strip(), 0)
        if idx < 0 or idx > 0xFFFF:
            raise ValueError("index out of range")
        if sub < 0 or sub > 0xFF:
            raise ValueError("subindex out of range")
        return idx, sub

    def sdo_read(self) -> None:
        try:
            slave = self._require_slave()
            idx, sub = self._parse_index_sub()
            data = bytes(slave.sdo_read(idx, sub))
            hex_s = data.hex(" ")
            self.enqueue("info", f"SDO READ 0x{idx:04X}:{sub} -> {hex_s} (len={len(data)})")
        except Exception as exc:
            self.enqueue("error", f"SDO read failed: {exc}")

    def sdo_write(self) -> None:
        try:
            slave = self._require_slave()
            idx, sub = self._parse_index_sub()
            t = self.sdo_type_var.get().strip()
            v = self.sdo_value_var.get().strip()

            if t == "u8":
                data = int(v, 0).to_bytes(1, "little", signed=False)
            elif t == "u16":
                data = int(v, 0).to_bytes(2, "little", signed=False)
            elif t == "u32":
                data = int(v, 0).to_bytes(4, "little", signed=False)
            elif t == "i32":
                data = int(v, 0).to_bytes(4, "little", signed=True)
            elif t == "f32":
                data = struct.pack("<f", float(v))
            else:
                raise ValueError(f"Unsupported type: {t}")

            slave.sdo_write(idx, sub, data)
            self.enqueue("info", f"SDO WRITE 0x{idx:04X}:{sub} ({t}) = {v}")
        except Exception as exc:
            self.enqueue("error", f"SDO write failed: {exc}")

    def enqueue(self, kind: str, msg: str) -> None:
        if kind == "line" and self.q.qsize() > 500:
            return
        self.q.put((kind, msg))

    def clear_log(self) -> None:
        self.log.delete("1.0", "end")

    @staticmethod
    def _channels_from_decoded(fields: dict[str, object]) -> tuple[float, float, float, float, float, float] | None:
        def _pick(*keys: str) -> float | None:
            for k in keys:
                if k in fields:
                    try:
                        return float(fields[k])  # type: ignore[arg-type]
                    except Exception:
                        return None
            return None

        c1 = _pick("Fx", "C1")
        c2 = _pick("Fy", "C2")
        c3 = _pick("Fz", "C3")
        c4 = _pick("Tx", "C4")
        c5 = _pick("Ty", "C5")
        c6 = _pick("Tz", "C6")
        if None in (c1, c2, c3, c4, c5, c6):
            return None
        return float(c1), float(c2), float(c3), float(c4), float(c5), float(c6)

    def _load_matching_serial_log(self, loadcell_csv: Path) -> int:
        m = re.match(r"loadcell_slave\d+_(\d{8}_\d{6})\.csv$", loadcell_csv.name)
        if not m:
            return 0

        serial_csv = loadcell_csv.with_name(f"serial_log_{m.group(1)}.csv")
        if not serial_csv.exists():
            return 0

        loaded = 0
        with serial_csv.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    ts = float((row.get("timestamp") or "").strip())
                    line = (row.get("line") or "").strip()
                    vals = self._extract_serial_values(line)
                    if not vals:
                        continue
                    t4c_val = float(vals.get("T4C", math.nan))
                    t4f_val = float(vals.get("T4F", math.nan))
                    motion_val = float(vals.get("MOTION", 0.0))
                    self._ser_ts_history.append(ts)
                    self._ser_T_history.append(t4c_val)
                    self._ser_co2_history.append(t4f_val)
                    self._ser_H_history.append(math.nan)
                    self._ser_aqi_history.append(math.nan)
                    self._ser_tvoc_history.append(math.nan)
                    self._ser_tdelta_history.append(math.nan)
                    self._ser_motion_history.append(motion_val)
                    loaded += 1
                except Exception:
                    continue
        return loaded

    def load_saved_csv(self) -> None:
        initial_dir = str((Path(__file__).resolve().parent.parent / "reports" / "host_master"))
        path_str = filedialog.askopenfilename(
            title="Load saved capture CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=initial_dir,
        )
        if not path_str:
            return

        csv_path = Path(path_str)
        if not csv_path.exists():
            self.enqueue("error", f"CSV not found: {csv_path}")
            return

        if self.metrics.connected:
            self.disconnect("Load CSV")

        t_vals: list[float] = []
        c1_vals: list[float] = []
        c2_vals: list[float] = []
        c3_vals: list[float] = []
        c4_vals: list[float] = []
        c5_vals: list[float] = []
        c6_vals: list[float] = []
        row_count = 0
        bad_rows = 0

        try:
            with csv_path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_count += 1
                    try:
                        ts = float((row.get("timestamp") or "").strip())
                        decoded_raw = (row.get("decoded_json") or "").strip()
                        if not decoded_raw:
                            bad_rows += 1
                            continue
                        fields = json.loads(decoded_raw)
                        if not isinstance(fields, dict):
                            bad_rows += 1
                            continue
                        ch = self._channels_from_decoded(fields)
                        if ch is None:
                            bad_rows += 1
                            continue

                        t_vals.append(ts)
                        c1_vals.append(ch[0])
                        c2_vals.append(ch[1])
                        c3_vals.append(ch[2])
                        c4_vals.append(ch[3])
                        c5_vals.append(ch[4])
                        c6_vals.append(ch[5])
                    except Exception:
                        bad_rows += 1
        except Exception as exc:
            self.enqueue("error", f"Failed to load CSV: {exc}")
            return

        if len(t_vals) < 2:
            self.enqueue("warn", f"No usable channel data in CSV: {csv_path.name}")
            return

        with self.history_lock:
            self.x_history.clear()
            self.c1_history.clear()
            self.c2_history.clear()
            self.c3_history.clear()
            self.c4_history.clear()
            self.c5_history.clear()
            self.c6_history.clear()
            self.analysis_t_history.clear()
            self.analysis_c1_history.clear()
            self.analysis_c2_history.clear()
            self.analysis_c3_history.clear()
            self.analysis_c4_history.clear()
            self.analysis_c5_history.clear()
            self.analysis_c6_history.clear()
            self._ser_ts_history.clear()
            self._ser_T_history.clear()
            self._ser_co2_history.clear()
            self._ser_H_history.clear()
            self._ser_aqi_history.clear()
            self._ser_tvoc_history.clear()
            self._ser_tdelta_history.clear()
            self._ser_motion_history.clear()

            self.x_history.extend(t_vals)
            self.c1_history.extend(c1_vals)
            self.c2_history.extend(c2_vals)
            self.c3_history.extend(c3_vals)
            self.c4_history.extend(c4_vals)
            self.c5_history.extend(c5_vals)
            self.c6_history.extend(c6_vals)
            self.analysis_t_history.extend(t_vals)
            self.analysis_c1_history.extend(c1_vals)
            self.analysis_c2_history.extend(c2_vals)
            self.analysis_c3_history.extend(c3_vals)
            self.analysis_c4_history.extend(c4_vals)
            self.analysis_c5_history.extend(c5_vals)
            self.analysis_c6_history.extend(c6_vals)
            ser_loaded = self._load_matching_serial_log(csv_path)

        self._loaded_from_csv = True
        self.sample_index = len(t_vals)
        self.last_draw_sample = -1
        self.last_analysis_ts = 0.0
        self._connect_ts = t_vals[0]
        self.metrics.connected = False
        self.metrics.lines_total = len(t_vals)
        self.metrics.last_wkc = None
        self.metrics.last_raw_hex = "-"
        self.metrics.last_line = f"Loaded from {csv_path.name}"
        self.metrics.status = f"Loaded CSV ({csv_path.name})"
        self.analysis_baseline = {}
        self.baseline_status_var.set("Baseline: not captured")

        info = f"Loaded {len(t_vals)} samples from {csv_path.name}"
        if ser_loaded > 0:
            info += f" | thermal points: {ser_loaded}"
        if bad_rows > 0:
            info += f" | skipped rows: {bad_rows}/{row_count}"
        self.enqueue("info", info)

    def _analysis_window(self) -> int:
        try:
            n = int(self.analysis_window_var.get().strip())
        except Exception:
            n = 256
        return max(32, min(ANALYSIS_HISTORY, n))

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _style_ax(ax, xlabel: str = "", ylabel: str = "") -> None:
        ax.set_facecolor("#2a2a3e")
        ax.tick_params(colors="#a6adc8", labelsize=7)
        ax.xaxis.label.set_color("#a6adc8")
        ax.yaxis.label.set_color("#a6adc8")
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=7)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=7)
        for sp in ax.spines.values():
            sp.set_edgecolor("#45475a")

    def update_analysis_panel(self) -> None:
        if np is None:
            return
        window = self._analysis_window()
        with self.history_lock:
            t_vals = list(self.analysis_t_history)[-window:]
            arrs_raw = {
                "F1": list(self.analysis_c1_history)[-window:],
                "F2": list(self.analysis_c2_history)[-window:],
                "F3": list(self.analysis_c3_history)[-window:],
                "T4": list(self.analysis_c4_history)[-window:],
                "T5": list(self.analysis_c5_history)[-window:],
                "T6": list(self.analysis_c6_history)[-window:],
            }

        if len(t_vals) < 32:
            return

        dt = (t_vals[-1] - t_vals[0]) / max(1, len(t_vals) - 1)
        if dt <= 0.0:
            return
        fs = 1.0 / dt

        arrs = {k: np.array(v, dtype=float) for k, v in arrs_raw.items()}
        force_keys  = ["F1", "F2", "F3"]
        torque_keys = ["T4", "T5", "T6"]
        force_colors  = ["#f38ba8", "#a6e3a1", "#89b4fa"]
        torque_colors = ["#fab387", "#cba6f7", "#94e2d5"]
        all_colors = force_colors + torque_colors
        all_keys   = force_keys + torque_keys
        ch_axes    = [self.ax_ch1, self.ax_ch2, self.ax_ch3,
                      self.ax_ch4, self.ax_ch5, self.ax_ch6]
        ch_titles  = ["F1 — Fx", "F2 — Fy", "F3 — Fz",
                      "T4 — Tx", "T5 — Ty", "T6 — Tz"]

        # clear all axes
        for ax in [
            self.ax_hist, self.ax_stats, self.ax_noise,
            self.ax_sr, self.ax_thermal, self.ax_thermal_4f,
            self.ax_ch1, self.ax_ch2, self.ax_ch3,
            self.ax_ch4, self.ax_ch5, self.ax_ch6,
        ]:
            ax.cla()

        _title_kw = dict(color="#cdd6f4", fontsize=9, pad=3)
        # x-axis: elapsed seconds since first sample in window
        t0 = t_vals[0]
        x_idx = np.array(t_vals, dtype=float) - t0
        x_label_time = "elapsed (s)"

        # 1 — Amplitude histogram — skip constant channels (density=True fails on zero variance)
        ax = self.ax_hist
        any_hist = False
        for k, col in zip(all_keys, all_colors):
            a = arrs[k]
            if np.std(a) < 1e-10:
                continue
            ax.hist(a, bins=40, color=col, alpha=0.50, histtype="stepfilled", label=k)
            any_hist = True
        if not any_hist:
            ax.text(0.5, 0.5, "No signal variation\n(all values constant)",
                    ha="center", va="center", color="#a6adc8", fontsize=8,
                    transform=ax.transAxes)
        ax.set_title("Amplitude histogram", **_title_kw)
        if any_hist:
            ax.legend(fontsize=5, loc="upper right", ncols=2, framealpha=0.3)
        self._style_ax(ax, "value", "count")

        # 5 — Stats bar chart (mean / std / rms per channel)
        ax = self.ax_stats
        x = np.arange(len(all_keys))
        bar_w = 0.26
        means = [float(arrs[k].mean()) for k in all_keys]
        stds  = [float(arrs[k].std()) for k in all_keys]
        rmss  = [float(np.sqrt(np.mean(arrs[k] ** 2))) for k in all_keys]
        ax.bar(x - bar_w, means, bar_w, color="#89b4fa", alpha=0.8, label="mean")
        ax.bar(x,         stds,  bar_w, color="#f38ba8", alpha=0.8, label="std")
        ax.bar(x + bar_w, rmss,  bar_w, color="#a6e3a1", alpha=0.8, label="rms")
        ax.set_xticks(x)
        ax.set_xticklabels(all_keys, fontsize=7)
        ax.legend(fontsize=6, framealpha=0.3)
        ax.set_title("Stats: mean / std / rms", **_title_kw)
        self._style_ax(ax, "", "value")

        # 6 — Noise ratio vs baseline
        ax = self.ax_noise
        if self.analysis_baseline:
            ratios = []
            for k in all_keys:
                bstd = self.analysis_baseline.get(k, (0.0, None))[1]
                cur_std = float(arrs[k].std())
                if bstd and bstd > 1e-12:
                    ratios.append(cur_std / bstd)
                else:
                    ratios.append(0.0)
            bars = ax.bar(all_keys, ratios, color=all_colors, alpha=0.85)
            ax.axhline(1.0, color="#f9e2af", lw=1.2, linestyle="--", label="baseline")
            for bar, val in zip(bars, ratios):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                        f"{val:.2f}x", ha="center", va="bottom", fontsize=6, color="#cdd6f4")
            ax.legend(fontsize=6, framealpha=0.3)
        else:
            ax.text(0.5, 0.5, "Capture a baseline\n(no-load) first",
                    ha="center", va="center", color="#a6adc8", fontsize=8,
                    transform=ax.transAxes)
        ax.set_title("Noise vs baseline (σ ratio)", **_title_kw)
        self._style_ax(ax, "", "ratio")

        # 7 — Sample rate over time (derived from inter-sample timestamps)
        ax = self.ax_sr
        if len(t_vals) >= 4:
            dt_arr = np.diff(np.array(t_vals))
            valid = dt_arr > 1e-6
            if np.any(valid):
                sr_vals = np.where(valid, 1.0 / np.where(valid, dt_arr, 1.0), np.nan)
                ax.plot(x_idx[1:], sr_vals, color="#89dceb", lw=0.8)
                avg_sr = float(np.nanmean(sr_vals))
                ax.axhline(avg_sr, color="#f9e2af", lw=1.0, linestyle="--")
                ax.text(0.01, 0.95, f"avg {avg_sr:.1f} Hz", ha="left", va="top",
                        color="#f9e2af", fontsize=7, transform=ax.transAxes)
        ax.set_title("Sample rate (Hz)", **_title_kw)
        self._style_ax(ax, x_label_time, "Hz")

        # 8–13 — Individual channel traces with inline stats box
        for k, col, ax, title in zip(all_keys, all_colors, ch_axes, ch_titles):
            a = np.array(arrs_raw[k], dtype=float)
            ax.plot(x_idx, a, color=col, lw=0.8)
            ax.set_title(title, **_title_kw)
            ax.set_xlabel(x_label_time, color="#a6adc8", fontsize=7)
            self._style_ax(ax, x_label_time, "")
            a_mean = float(a.mean())
            a_std  = float(a.std())
            a_min  = float(a.min())
            a_max  = float(a.max())
            a_rms  = float(np.sqrt(np.mean(a ** 2)))
            bline  = self.analysis_baseline.get(k)
            noise_s = f"σ/base {a_std / bline[1]:.2f}x" if (bline and bline[1] > 1e-12) else "σ/base n/a"
            stats_txt = (
                f"μ={a_mean:.2f}  σ={a_std:.2f}\n"
                f"rms={a_rms:.2f}\n"
                f"min={a_min:.2f}  max={a_max:.2f}\n"
                f"{noise_s}"
            )
            ax.text(
                0.98, 0.97, stats_txt,
                ha="right", va="top", fontsize=6, color="#cdd6f4",
                bbox=dict(facecolor="#1e1e2e", edgecolor="#45475a",
                          boxstyle="round,pad=0.3", alpha=0.9),
                transform=ax.transAxes,
            )

        # — Thermal 4C + disturbance
        ax = self.ax_thermal
        ax.set_title("Thermal 4C + disturbance — same time window", **_title_kw)
        # — Thermal 4F
        ax4f = self.ax_thermal_4f
        ax4f.set_title("Thermal 4F — same time window", **_title_kw)
        with self.history_lock:
            ser_ts  = list(self._ser_ts_history)
            ser_t4c = list(self._ser_T_history)
            ser_t4f = list(self._ser_co2_history)
            ser_motion = list(self._ser_motion_history)
        if ser_ts and t_vals:
            t_win_start = t_vals[0]
            t_win_end   = t_vals[-1]
            s_ts_rel: list[float] = []
            s_t4c: list[float] = []
            s_t4f: list[float] = []
            s_motion: list[float] = []
            for ts, t4c_v, t4f_v, motion_v in zip(ser_ts, ser_t4c, ser_t4f, ser_motion):
                if t_win_start <= ts <= t_win_end:
                    s_ts_rel.append(ts - t0)
                    s_t4c.append(t4c_v)
                    s_t4f.append(t4f_v)
                    s_motion.append(motion_v)

            sx_4c = [x for x, y in zip(s_ts_rel, s_t4c) if math.isfinite(y)]
            sy_4c = [y for y in s_t4c if math.isfinite(y)]
            sx_4f = [x for x, y in zip(s_ts_rel, s_t4f) if math.isfinite(y)]
            sy_4f = [y for y in s_t4f if math.isfinite(y)]
            sx_m = [x for x, y in zip(s_ts_rel, s_motion) if y > 0.5]
            sy_m = [1.0 for _ in sx_m]
            if sx_4c or sx_m:
                ax_co2 = ax.twinx()
                ax_co2.set_facecolor("#2a2a3e")
                if sx_m:
                    ax_co2.scatter(sx_m, sy_m, color="#f9e2af", s=12, label="Disturbance")
                ax_co2.set_ylabel("Disturbance", color="#f9e2af", fontsize=7)
                ax_co2.tick_params(colors="#f9e2af", labelsize=7)
                if sx_4c:
                    ax.plot(sx_4c, sy_4c, color="#f38ba8", lw=1.5, label="Temp 4C")
                ax.set_ylabel("Temp (°C)", color="#f38ba8", fontsize=7)
                ax.tick_params(colors="#f38ba8", labelsize=7)
                lines1, labels1 = ax.get_legend_handles_labels()
                lines2, labels2 = ax_co2.get_legend_handles_labels()
                ax.legend(lines1 + lines2, labels1 + labels2, fontsize=7, framealpha=0.3, loc="upper left")
                for spine in ax_co2.spines.values():
                    spine.set_edgecolor("#45475a")
            else:
                ax.text(0.5, 0.5, "No 4C thermal data in this window",
                        ha="center", va="center", color="#a6adc8", fontsize=8, transform=ax.transAxes)
            if sx_4f:
                ax4f.plot(sx_4f, sy_4f, color="#89b4fa", lw=1.3, label="Temp 4F")
                ax4f.set_ylabel("Temp (°C)", color="#89b4fa", fontsize=7)
                ax4f.tick_params(colors="#89b4fa", labelsize=7)
                ax4f.legend(fontsize=7, framealpha=0.3, loc="upper left")
            else:
                ax4f.text(0.5, 0.5, "No 4F thermal data in this window",
                          ha="center", va="center", color="#a6adc8", fontsize=8, transform=ax4f.transAxes)
        else:
            for _axt in (ax, ax4f):
                _axt.text(0.5, 0.5, "No thermal data yet\n(connect ESP32S3 on Serial Monitor tab)",
                          ha="center", va="center", color="#a6adc8", fontsize=8, transform=_axt.transAxes)
        self._style_ax(ax, x_label_time, "")
        self._style_ax(ax4f, x_label_time, "")

        try:
            self.analysis_canvas.draw()
        except Exception:
            pass

    def capture_noise_baseline(self) -> None:
        if np is None:
            self.enqueue("warn", "numpy not available")
            return
        window = self._analysis_window()
        with self.history_lock:
            arrs_raw = {
                "F1": list(self.analysis_c1_history)[-window:],
                "F2": list(self.analysis_c2_history)[-window:],
                "F3": list(self.analysis_c3_history)[-window:],
                "T4": list(self.analysis_c4_history)[-window:],
                "T5": list(self.analysis_c5_history)[-window:],
                "T6": list(self.analysis_c6_history)[-window:],
            }
        if len(arrs_raw["F1"]) < 16:
            self.enqueue("warn", "Need more samples before baseline capture")
            return
        self.analysis_baseline = {}
        for k, vals in arrs_raw.items():
            a = np.array(vals, dtype=float)
            self.analysis_baseline[k] = (float(a.mean()), float(a.std()))
        self.baseline_status_var.set(f"Baseline: captured from last {window} samples")
        self.enqueue("info", "Noise baseline captured (no-load reference)")

    def clear_noise_baseline(self) -> None:
        self.analysis_baseline = {}
        self.baseline_status_var.set("Baseline: not captured")
        self.enqueue("info", "Noise baseline cleared")

    def _set_axis_limits(self, ax: object, x_vals: list[int], y_vals: list[float]) -> None:
        if not x_vals or not y_vals:
            return
        x_min = x_vals[0]
        x_max = x_vals[-1]
        if x_min == x_max:
            x_max = x_min + 1
        y_min = min(y_vals)
        y_max = max(y_vals)
        if y_min == y_max:
            pad = max(1.0, abs(y_min) * 0.05)
            y_min -= pad
            y_max += pad
        else:
            pad = (y_max - y_min) * 0.08
            y_min -= pad
            y_max += pad

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

    def ui_tick(self) -> None:
        try:
            drained = 0
            while drained < MAX_LOG_MESSAGES_PER_TICK:
                try:
                    kind, msg = self.q.get_nowait()
                except queue.Empty:
                    break

                if kind == "line":
                    self.log.insert("end", msg + "\n")
                elif kind == "error":
                    self.log.insert("end", "[ERROR] " + msg + "\n")
                elif kind == "warn":
                    self.log.insert("end", "[WARN] " + msg + "\n")
                else:
                    self.log.insert("end", "[INFO] " + msg + "\n")
                self.log.see("end")
                drained += 1

            # Prevent unbounded Tk text growth in multi-day runs.
            line_count = int(self.log.index("end-1c").split(".")[0])
            if line_count > MAX_LOG_LINES:
                self.log.delete("1.0", f"{line_count - LOG_TRIM_TO_LINES}.0")
        except KeyboardInterrupt:
            self.enqueue("info", "GUI interrupted by user")
            self.on_close()
            return

        active_tab = str(self.tabs.select()) if hasattr(self, "tabs") else ""
        live_active = active_tab == str(self.live_tab)
        analysis_active = active_tab == str(self.analysis_tab)

        with self.history_lock:
            x_vals = list(self.x_history)
            c1_vals = list(self.c1_history)
            c2_vals = list(self.c2_history)
            c3_vals = list(self.c3_history)
            c4_vals = list(self.c4_history)
            c5_vals = list(self.c5_history)
            c6_vals = list(self.c6_history)

        now = time.time()
        should_draw = (
            live_active
            and (self.metrics.connected or self._loaded_from_csv)
            and self.sample_index != self.last_draw_sample
            and (now - self.last_draw_ts) >= MIN_DRAW_INTERVAL_S
        )
        if should_draw:
            # Convert wall-clock timestamps to elapsed seconds relative to first point.
            if x_vals:
                t0_live = x_vals[0]
                x_rel = [t - t0_live for t in x_vals]
            else:
                x_rel = x_vals

            # Downsample live plot when more points than display threshold.
            if _TSDS is not None and np is not None and len(x_rel) > LIVE_DOWNSAMPLE_THRESHOLD:
                x_np = np.array(x_rel, dtype=np.float64)
                idx = _TSDS.downsample(x_np, np.array(c1_vals, dtype=np.float64), n_out=LIVE_DOWNSAMPLE_THRESHOLD)
                x_rel   = [x_rel[i]  for i in idx]
                c1_vals = [c1_vals[i] for i in idx]
                c2_vals = [c2_vals[i] for i in idx]
                c3_vals = [c3_vals[i] for i in idx]
                c4_vals = [c4_vals[i] for i in idx]
                c5_vals = [c5_vals[i] for i in idx]
                c6_vals = [c6_vals[i] for i in idx]

            self.c1_line.set_data(x_rel, c1_vals)
            self.c2_line.set_data(x_rel, c2_vals)
            self.c3_line.set_data(x_rel, c3_vals)
            self.c4_line.set_data(x_rel, c4_vals)
            self.c5_line.set_data(x_rel, c5_vals)
            self.c6_line.set_data(x_rel, c6_vals)

            # Thermal overlay on live third subplot.
            with self.history_lock:
                ser_ts_live  = list(self._ser_ts_history)
                ser_t4c_live   = list(self._ser_T_history)
                ser_t4f_live = list(self._ser_co2_history)
                ser_motion_live = list(self._ser_motion_history)
            if ser_ts_live and x_vals:
                tx_rel = [t - t0_live for t in ser_ts_live]
                tx_4c = [x for x, y in zip(tx_rel, ser_t4c_live) if math.isfinite(y)]
                ty_4c = [y for y in ser_t4c_live if math.isfinite(y)]
                tx_4f = [x for x, y in zip(tx_rel, ser_t4f_live) if math.isfinite(y)]
                ty_4f = [y for y in ser_t4f_live if math.isfinite(y)]
                tx_m = [x for x, y in zip(tx_rel, ser_motion_live) if y > 0.5]
                ty_m = [1.0 for _ in tx_m]
                self.thermal_T4C_line.set_data(tx_4c, ty_4c)
                self.thermal_T4F_line.set_data(tx_4f, ty_4f)
                self.thermal_motion_line.set_data(tx_m, ty_m)
                self.thermal_ax_co2.set_ylim(-0.05, 1.2)
                self.thermal_ax_co2.set_ylabel("Disturbance", fontsize=8)
                if ty_4c:
                    self._set_axis_limits(self.thermal_4c_ax, tx_4c, ty_4c)
                if ty_4f:
                    self._set_axis_limits(self.thermal_4f_ax, tx_4f, ty_4f)
                if tx_m:
                    self._set_axis_limits(self.thermal_ax_co2, tx_m, ty_m)

            if x_rel:
                self._set_axis_limits(self.top_ax, x_rel, c1_vals + c2_vals + c3_vals)
                self._set_axis_limits(self.bot_ax, x_rel, c4_vals + c5_vals + c6_vals)
            try:
                self.canvas.draw()
                self.last_draw_ts = now
                self.last_draw_sample = self.sample_index
            except KeyboardInterrupt:
                self.enqueue("info", "GUI draw interrupted by user")
                self.on_close()
                return
            except Exception as exc:
                self.metrics.errors_total += 1
                self.enqueue("warn", f"Draw warning: {exc}")

        self.connect_btn.configure(text="Disconnect" if self.metrics.connected else "Connect")

        self.status_var.set(f"Status: {self.metrics.status}")
        self.wkc_var.set(f"WKC: {'-' if self.metrics.last_wkc is None else self.metrics.last_wkc}")
        self.secondary_wkc_var.set(f"Slave2: {'present' if self.secondary_slave else 'none'}")
        self._capture_enabled = bool(self.capture_enabled_var.get())
        self.count_var.set(
            f"Samples: {self.metrics.lines_total} | Errors: {self.metrics.errors_total} | Drops: {self.metrics.dropouts_total}"
        )
        self.raw_var.set(f"Raw: {self.metrics.last_raw_hex}")
        self.last_line_var.set(f"Decoded: {self.metrics.last_line}")

        now = time.time()
        if analysis_active:
            # Adaptive analysis throttle based on process memory pressure.
            if _psutil is not None and (now - self._last_mem_check_ts) >= 5.0:
                self._mem_mb = _PSUTIL_PROC.memory_info().rss / (1024 * 1024)
                self._last_mem_check_ts = now
            effective_interval = ANALYSIS_UPDATE_INTERVAL_S
            if self._mem_mb >= ADAPTIVE_MEM_HIGH_MB:
                effective_interval = ANALYSIS_UPDATE_INTERVAL_S * 3
            if self._mem_mb >= ADAPTIVE_MEM_CRITICAL_MB:
                # Force-trim log text widget to shed memory quickly.
                try:
                    lc = int(self.log.index("end-1c").split(".")[0])
                    if lc > LOG_TRIM_TO_LINES:
                        self.log.delete("1.0", f"{lc - LOG_TRIM_TO_LINES}.0")
                except Exception:
                    pass
                effective_interval = ANALYSIS_UPDATE_INTERVAL_S * 8
            if (now - self.last_analysis_ts) >= effective_interval:
                self.update_analysis_panel()
                self.last_analysis_ts = now

        if not self.stop_evt.is_set():
            self.root.after(UI_TICK_MS, self.ui_tick)

        # Drain serial queue — batch into single Text update to avoid per-line configure() cost.
        _SER_BATCH = 200        # max lines consumed per tick
        _SER_MAX_LINES = 500    # max lines kept in the Text widget
        if _SERIAL_AVAILABLE and hasattr(self, "_ser_text") and self._ser_text is not None:
            lines: list[str] = []
            while len(lines) < _SER_BATCH:
                try:
                    lines.append(self._serial_q.get_nowait())
                except queue.Empty:
                    break
            if lines:
                ts_str = time.strftime("%H:%M:%S")
                st = self._ser_text
                st.configure(state="normal")
                for ln in lines:
                    st.insert("end", f"[{ts_str}] ", ("ts",))
                    st.insert("end", ln + "\n", ("rx",))
                # Trim to max lines (delete from top).
                total = int(st.index("end-1c").split(".")[0])
                if total > _SER_MAX_LINES:
                    st.delete("1.0", f"{total - _SER_MAX_LINES}.0")
                st.see("end")
                st.configure(state="disabled")
                # Log file — write whole batch at once.
                if self._serial_log_fh is not None:
                    try:
                        now_f = time.time()
                        self._serial_log_fh.writelines(f"{now_f:.6f},{ln}\n" for ln in lines)
                        self._serial_log_fh.flush()
                    except Exception:
                        pass
                # Parse sensor values from each line.
                for line in lines:
                    _vals = self._extract_serial_values(line)
                    if not _vals:
                        continue
                    try:
                        _T4C = float(_vals.get("T4C", math.nan))
                        _T4F = float(_vals.get("T4F", math.nan))
                        _motion = float(_vals.get("MOTION", 0.0))
                        _ts  = time.time()
                        with self.history_lock:
                            self._ser_ts_history.append(_ts)
                            self._ser_T_history.append(_T4C)
                            self._ser_co2_history.append(_T4F)
                            self._ser_H_history.append(math.nan)
                            self._ser_aqi_history.append(math.nan)
                            self._ser_tvoc_history.append(math.nan)
                            self._ser_tdelta_history.append(math.nan)
                            self._ser_motion_history.append(_motion)
                    except Exception:
                        pass

    def on_close(self) -> None:
        self.stop_evt.set()
        self.disconnect("Window closed")
        if _SERIAL_AVAILABLE:
            self._serial_disconnect("Window closed")
            self._serial_toggle_log_off()
        self.root.destroy()


def main() -> None:
    import traceback as _tb

    _err_log = Path(__file__).resolve().parent.parent / "reports" / "host_master" / f"gui_errors_{time.strftime('%Y%m%d_%H%M%S')}.log"

    def _tk_report_callback_exception(exc_type, exc_val, exc_tb) -> None:  # type: ignore[override]
        msg = "".join(_tb.format_exception(exc_type, exc_val, exc_tb))
        print(f"[TK ERROR] {msg}", flush=True)
        try:
            _err_log.parent.mkdir(parents=True, exist_ok=True)
            with _err_log.open("a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n{msg}\n")
        except Exception:
            pass

    try:
        root = tk.Tk()
        root.report_callback_exception = _tk_report_callback_exception
        app = EthercatLiveGui(root)
        # Keep a strong reference for the lifetime of mainloop.
        root._app = app  # type: ignore[attr-defined]
        root.mainloop()
    except KeyboardInterrupt:
        print("[launchpad_loadcell_live_gui] Interrupted by user")
        return
    except Exception as exc:
        print(f"[launchpad_loadcell_live_gui] Startup failed: {exc}")
        _tb.print_exc()
        raise


if __name__ == "__main__":
    main()
