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
import struct
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import scrolledtext, ttk

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

LIVE_DOWNSAMPLE_THRESHOLD = 2000  # downsample live plot when points exceed this
ADAPTIVE_MEM_HIGH_MB = 800        # slow analysis redraws above this RSS
ADAPTIVE_MEM_CRITICAL_MB = 1400   # force-trim log + maximum slowdown above this

from ati_ft_testbench import ATI_PRODUCT_CODE, ATI_VENDOR_ID

UI_TICK_MS = 120
MIN_DRAW_INTERVAL_S = 0.01
ANALYSIS_UPDATE_INTERVAL_S = 2.0
MIN_PERIOD_MS = 1.0
LOG_EVERY_N_SAMPLES = 20
MAX_LOG_MESSAGES_PER_TICK = 120
MAX_LOG_LINES = 6000
LOG_TRIM_TO_LINES = 4000
STATE_FILE = Path(__file__).with_name(".launchpad_loadcell_live_gui_adapter.txt")
DEFAULT_ADAPTER_HINT = "Realtek Gaming USB 2.5GbE"
DEFAULT_PERIOD_MS = 10.0
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
        self.worker_thread: threading.Thread | None = None
        self.history_lock = threading.Lock()

        self.master: pysoem.Master | None = None
        self.target_slave: pysoem.CdefSlave | None = None

        self.adapter_var = tk.StringVar(value="")
        self.period_var = tk.StringVar(value=str(DEFAULT_PERIOD_MS))
        self.profile_var = tk.StringVar(value=PROFILE_LOADCELL)
        self.slave_hint_var = tk.StringVar(value="")

        self.capture_path_var = tk.StringVar(
            value=str((Path(__file__).resolve().parent.parent / "reports" / "host_master" / "eea_capture.csv").resolve())
        )
        self.capture_enabled_var = tk.BooleanVar(value=False)
        self.analysis_window_var = tk.StringVar(value="256")
        self.baseline_status_var = tk.StringVar(value="Baseline: not captured")

        period_override = os.getenv("LC_GUI_PERIOD_MS", "").strip()
        if period_override:
            self.period_var.set(period_override)

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

        self.x_history: deque[int] = deque(maxlen=GRAPH_HISTORY)
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

        self._build_ui()
        self.refresh_adapters()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(150, self.auto_connect_on_startup)
        self.root.after(UI_TICK_MS, self.ui_tick)

        auto_close_s = os.getenv("LC_GUI_AUTO_CLOSE_S", "").strip()
        if auto_close_s:
            try:
                auto_s = max(1.0, float(auto_close_s))
                self.enqueue("info", f"Debug auto-close active: {auto_s:.1f}s")
                self.root.after(int(auto_s * 1000), self.on_close)
            except Exception:
                pass

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

        # ── main tabs — right under adapter strip for maximum content area ──
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.live_tab = ttk.Frame(self.tabs)
        self.analysis_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.live_tab, text="  Live  ")
        self.tabs.add(self.analysis_tab, text="  Analysis  ")

        # ── Live tab ───────────────────────────────────────────────────────────
        status = ttk.LabelFrame(self.live_tab, text="Live Status", padding=8)
        status.pack(fill="x", padx=0, pady=(4, 4))

        ttk.Label(status, textvariable=self.status_var).grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.wkc_var).grid(row=0, column=1, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.count_var).grid(row=1, column=0, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.raw_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=2)
        ttk.Label(status, textvariable=self.last_line_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=2)

        cap = ttk.LabelFrame(self.live_tab, text="EEA Reverse-Engineering Capture", padding=8)
        cap.pack(fill="x", padx=0, pady=(0, 4))
        ttk.Checkbutton(cap, text="Enable CSV capture", variable=self.capture_enabled_var).grid(row=0, column=0, sticky="w", padx=6)
        ttk.Label(cap, text="CSV path:").grid(row=0, column=1, sticky="e", padx=6)
        ttk.Entry(cap, textvariable=self.capture_path_var, width=98).grid(row=0, column=2, sticky="we", padx=6)
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

        graph_frame = ttk.LabelFrame(self.live_tab, text="Live Graph (Force 1-3, Torque 4-6)", padding=8)
        graph_frame.pack(fill="both", expand=False, padx=0, pady=(0, 4))

        self.figure = Figure(figsize=(11, 3.8), dpi=100)
        self.top_ax = self.figure.add_subplot(211)
        self.bot_ax = self.figure.add_subplot(212)

        self.top_ax.set_title("Force (Ch 1-3: Fx Fy Fz)")
        self.bot_ax.set_title("Torque (Ch 4-6: Tx Ty Tz)")
        self.bot_ax.set_xlabel("sample")

        (self.c1_line,) = self.top_ax.plot([], [], label="F1")
        (self.c2_line,) = self.top_ax.plot([], [], label="F2")
        (self.c3_line,) = self.top_ax.plot([], [], label="F3")
        (self.c4_line,) = self.bot_ax.plot([], [], label="T4")
        (self.c5_line,) = self.bot_ax.plot([], [], label="T5")
        (self.c6_line,) = self.bot_ax.plot([], [], label="T6")

        self.top_ax.legend(loc="upper left", ncols=3, fontsize=8)
        self.bot_ax.legend(loc="upper left", ncols=3, fontsize=8)
        self.top_ax.grid(True, alpha=0.3)
        self.bot_ax.grid(True, alpha=0.3)
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

        self.analysis_fig = Figure(figsize=(13, 9), dpi=96)
        self.analysis_fig.patch.set_facecolor("#1e1e2e")
        gs = self.analysis_fig.add_gridspec(
            5, 3, hspace=0.70, wspace=0.38,
            left=0.07, right=0.97, top=0.96, bottom=0.04
        )
        _ax_kw = dict(facecolor="#2a2a3e")
        self.ax_fft_force  = self.analysis_fig.add_subplot(gs[0, 0], **_ax_kw)
        self.ax_fft_torque = self.analysis_fig.add_subplot(gs[0, 1], **_ax_kw)
        self.ax_psd        = self.analysis_fig.add_subplot(gs[0, 2], **_ax_kw)
        self.ax_hist       = self.analysis_fig.add_subplot(gs[1, 0], **_ax_kw)
        self.ax_stats      = self.analysis_fig.add_subplot(gs[1, 1], **_ax_kw)
        self.ax_noise      = self.analysis_fig.add_subplot(gs[1, 2], **_ax_kw)
        self.ax_sr         = self.analysis_fig.add_subplot(gs[2, 0:3], **_ax_kw)
        self.ax_ch1        = self.analysis_fig.add_subplot(gs[3, 0], **_ax_kw)
        self.ax_ch2        = self.analysis_fig.add_subplot(gs[3, 1], **_ax_kw)
        self.ax_ch3        = self.analysis_fig.add_subplot(gs[3, 2], **_ax_kw)
        self.ax_ch4        = self.analysis_fig.add_subplot(gs[4, 0], **_ax_kw)
        self.ax_ch5        = self.analysis_fig.add_subplot(gs[4, 1], **_ax_kw)
        self.ax_ch6        = self.analysis_fig.add_subplot(gs[4, 2], **_ax_kw)

        _title_kw = dict(color="#cdd6f4", fontsize=9, pad=3)
        for ax, title in [
            (self.ax_fft_force,  "FFT — Force (F1 F2 F3)"),
            (self.ax_fft_torque, "FFT — Torque (T4 T5 T6)"),
            (self.ax_psd,        "Welch PSD — all channels"),
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
        ]:
            ax.set_title(title, **_title_kw)
            ax.tick_params(colors="#a6adc8", labelsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor("#45475a")

        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, master=analysis_plot_frame)
        self.analysis_canvas.get_tk_widget().pack(fill="both", expand=True)

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

            self.master = master
            self.target_slave = target_slave
            self.metrics = Metrics(connected=True, status=f"Connected ({adapter_name})")
            self.save_selected_adapter_label()

            self.worker_stop_evt = threading.Event()
            self.worker_thread = threading.Thread(target=self.reader_loop, args=(period_ms / 1000.0,), daemon=True)
            self.worker_thread.start()

            self.enqueue(
                "info",
                f"Connected: profile={self.profile_var.get()} slave='{target_slave.name}' man=0x{target_slave.man:08X} prod=0x{target_slave.id:08X}",
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

    def decode_loadcell(self, raw: bytes, wkc: int) -> DecodeResult:
        if len(raw) < 24:
            return DecodeResult(False, {}, f"decode_failed len={len(raw)}")
        try:
            fx, fy, fz, tx, ty, tz = struct.unpack_from("<6i", raw, 0)
        except struct.error:
            return DecodeResult(False, {}, "decode_failed struct")

        fields = {
            "Fx": float(fx),
            "Fy": float(fy),
            "Fz": float(fz),
            "Tx": float(tx),
            "Ty": float(ty),
            "Tz": float(tz),
        }
        line = (
            f"LOADCELL n={self.metrics.lines_total + 1:04d} ts={time.time():.3f} wkc={wkc} "
            f"Fx={fx} Fy={fy} Fz={fz} Tx={tx} Ty={ty} Tz={tz}"
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

    def _capture_sample(self, wkc: int, raw: bytes, decoded: DecodeResult) -> None:
        if not self.capture_enabled_var.get():
            return
        try:
            path = Path(self.capture_path_var.get().strip())
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

                    with self.history_lock:
                        self.x_history.append(self.sample_index)
                        self.c1_history.append(float(c1))
                        self.c2_history.append(float(c2))
                        self.c3_history.append(float(c3))
                        self.c4_history.append(float(c4))
                        self.c5_history.append(float(c5))
                        self.c6_history.append(float(c6))
                        now_ts = time.time()
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
            self.ax_fft_force, self.ax_fft_torque, self.ax_psd,
            self.ax_hist, self.ax_stats, self.ax_noise,
            self.ax_sr,
            self.ax_ch1, self.ax_ch2, self.ax_ch3,
            self.ax_ch4, self.ax_ch5, self.ax_ch6,
        ]:
            ax.cla()

        _title_kw = dict(color="#cdd6f4", fontsize=9, pad=3)
        x_idx = np.arange(len(t_vals), dtype=float)

        # 1 — FFT magnitude (force)
        ax = self.ax_fft_force
        for k, col in zip(force_keys, force_colors):
            a = arrs[k] - arrs[k].mean()
            mags = np.abs(np.fft.rfft(a, n=len(a)))
            freqs = np.fft.rfftfreq(len(a), d=1.0 / fs)
            ax.semilogy(freqs[1:], mags[1:], color=col, lw=0.9, label=k)
        ax.set_title("FFT — Force (F1 F2 F3)", **_title_kw)
        ax.legend(fontsize=6, loc="upper right", framealpha=0.3)
        self._style_ax(ax, "Hz", "mag")

        # 2 — FFT magnitude (torque)
        ax = self.ax_fft_torque
        for k, col in zip(torque_keys, torque_colors):
            a = arrs[k] - arrs[k].mean()
            mags = np.abs(np.fft.rfft(a, n=len(a)))
            freqs = np.fft.rfftfreq(len(a), d=1.0 / fs)
            ax.semilogy(freqs[1:], mags[1:], color=col, lw=0.9, label=k)
        ax.set_title("FFT — Torque (T4 T5 T6)", **_title_kw)
        ax.legend(fontsize=6, loc="upper right", framealpha=0.3)
        self._style_ax(ax, "Hz", "mag")

        # 3 — Welch PSD all channels
        ax = self.ax_psd
        if scipy_signal is not None:
            for k, col in zip(all_keys, all_colors):
                a = arrs[k] - arrs[k].mean()
                nperseg = min(len(a), 256)
                f_w, pxx = scipy_signal.welch(a, fs=fs, nperseg=nperseg)
                ax.semilogy(f_w[1:], pxx[1:], color=col, lw=0.8, label=k)
        ax.set_title("Welch PSD — all channels", **_title_kw)
        ax.legend(fontsize=5, loc="upper right", ncols=2, framealpha=0.3)
        self._style_ax(ax, "Hz", "PSD")

        # 4 — Amplitude histogram — skip constant channels (density=True fails on zero variance)
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
        self._style_ax(ax, "sample step", "Hz")

        # 8–13 — Individual channel traces with inline stats box
        for k, col, ax, title in zip(all_keys, all_colors, ch_axes, ch_titles):
            a = np.array(arrs_raw[k], dtype=float)
            ax.plot(x_idx, a, color=col, lw=0.8)
            ax.set_title(title, **_title_kw)
            self._style_ax(ax, "sample in window", "")
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
            and self.metrics.connected
            and self.sample_index != self.last_draw_sample
            and (now - self.last_draw_ts) >= MIN_DRAW_INTERVAL_S
        )
        if should_draw:
            # Downsample live plot when more points than display threshold.
            if _TSDS is not None and np is not None and len(x_vals) > LIVE_DOWNSAMPLE_THRESHOLD:
                x_np = np.array(x_vals, dtype=np.float64)
                idx = _TSDS.downsample(x_np, np.array(c1_vals, dtype=np.float64), n_out=LIVE_DOWNSAMPLE_THRESHOLD)
                x_vals  = [x_vals[i]  for i in idx]
                c1_vals = [c1_vals[i] for i in idx]
                c2_vals = [c2_vals[i] for i in idx]
                c3_vals = [c3_vals[i] for i in idx]
                c4_vals = [c4_vals[i] for i in idx]
                c5_vals = [c5_vals[i] for i in idx]
                c6_vals = [c6_vals[i] for i in idx]

            self.c1_line.set_data(x_vals, c1_vals)
            self.c2_line.set_data(x_vals, c2_vals)
            self.c3_line.set_data(x_vals, c3_vals)
            self.c4_line.set_data(x_vals, c4_vals)
            self.c5_line.set_data(x_vals, c5_vals)
            self.c6_line.set_data(x_vals, c6_vals)

            if x_vals:
                self._set_axis_limits(self.top_ax, x_vals, c1_vals + c2_vals + c3_vals)
                self._set_axis_limits(self.bot_ax, x_vals, c4_vals + c5_vals + c6_vals)
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

    def on_close(self) -> None:
        self.stop_evt.set()
        self.disconnect("Window closed")
        self.root.destroy()


def main() -> None:
    try:
        root = tk.Tk()
        app = EthercatLiveGui(root)
        # Keep a strong reference for the lifetime of mainloop.
        root._app = app  # type: ignore[attr-defined]
        root.mainloop()
    except KeyboardInterrupt:
        print("[launchpad_loadcell_live_gui] Interrupted by user")
        return
    except Exception as exc:
        import traceback

        print(f"[launchpad_loadcell_live_gui] Startup failed: {exc}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
