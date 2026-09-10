#!/usr/bin/env python3
"""
EEA Gateway Command Panel  —  eea_gateway_panel.py

Full-featured Tkinter GUI for the EFlexEthercatModbusRTUGateway.

Tabs:
  1. Connect      – adapter select, slave hint, period, connect/disconnect
  2. ToROI        – all S4 output fields + action buttons
  3. ToEEA        – S3 full fields + S2/S1 latency sqn + Additional outputs
  4. Input Status – live decoded view of all 39 input fields (auto-refresh)
  5. Debug Log    – raw hex + tagged event stream + CSV capture

Action buttons cover every named command in scope:
  - Heartbeat toggle / manual step
  - Terminator set
  - LED colour presets (off / red / green / blue / white) + freeform
  - Brightness set (0-15) + blink rate set (0-15)
  - Latency SQN start / stop / reset for each station
  - Additional channel write (S1-S10 / C1-C10)
  - E-STOP (zero all outputs immediately)
  - Safe state (heartbeat=1, everything else off)
"""

from __future__ import annotations

import csv
import queue
import struct
import threading
import time
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk
from typing import Any

import pysoem

from eea_gateway_map import (
    PDO_INPUT_BASE_BIT,
    PDO_OUTPUT_BASE_BIT,
    ProcessVar,
    decode_general_info,
    decode_led_brightness_blink,
    decode_process_image,
    encode_process_image,
    load_gateway_process_map,
)

# ─── Constants ────────────────────────────────────────────────────────────────
UI_TICK_MS        = 100
TIMEOUT_US        = 50_000
DEFAULT_PERIOD_MS = 10.0
DEFAULT_ADAPTER   = "Realtek"
DEFAULT_SLAVE     = "EFlex"
CAPTURE_PATH_DEF  = str(
    Path(__file__).resolve().parent.parent / "reports" / "host_master" / "eea_panel_capture.csv"
)

# Brightness/blink convenience presets
_BRIGHTNESS_FULL  = 0xF0   # brightness=15, blink=0
_BLINK_SLOW       = 0x01   # brightness=0, blink=1
_LED_OFF          = 0x00
_LED_RED          = 0xFF
_LED_GREEN        = 0xFF
_LED_BLUE         = 0xFF

# ─── State ────────────────────────────────────────────────────────────────────
@dataclass
class OutputState:
    """Mirrors all 26 gateway output fields. GUI edits this; worker reads it."""
    # ToROI S4
    roi_heartbeat:        int = 1
    roi_terminator:       int = 0
    roi_brightness_blink: int = 0x11
    roi_led_blue:         int = 0
    roi_led_green:        int = 0
    roi_led_red:          int = 0
    roi_latency_sqn:      int = 1
    # ToEEA S3
    s3_heartbeat:         int = 1
    s3_terminator:        int = 0
    s3_brightness_blink:  int = 0x11
    s3_led_blue:          int = 0
    s3_led_green:         int = 0
    s3_led_red:           int = 0
    s3_latency_sqn:       int = 1
    # ToEEA latency only
    s2_latency_sqn:       int = 1
    s1_latency_sqn:       int = 1
    # Additional outputs (S1-S10)
    additional: list[int] = field(default_factory=lambda: [0] * 10)
    # E-stop flag: when True worker writes all zeros
    estop: bool = False

    def to_field_map(self, pvars: list[ProcessVar]) -> dict[str, int]:
        """Convert to the {var_name: int} dict used by encode_process_image."""
        m: dict[str, int] = {}
        prefix = "EFlexEthercatModbusRTUGateway."

        def _set(name: str, val: int) -> None:
            m[prefix + name] = val

        _set("ToROI.S4Hearbeat",            self.roi_heartbeat)
        _set("ToROI.S4Terminator",          self.roi_terminator)
        _set("ToROI.S4BrightnessBlinkrate", self.roi_brightness_blink)
        _set("ToROI.S4LedBlue",             self.roi_led_blue)
        _set("ToROI.S4LedGreen",            self.roi_led_green)
        _set("ToROI.S4LedRed",              self.roi_led_red)
        _set("ToROI.S4LatencySQNInput",     self.roi_latency_sqn)

        _set("ToEEA.S3Hearbeat",            self.s3_heartbeat)
        _set("ToEEA.S3Terminator",          self.s3_terminator)
        _set("ToEEA.S3BrightnessBlinkrate", self.s3_brightness_blink)
        _set("ToEEA.S3LedBlue",             self.s3_led_blue)
        _set("ToEEA.S3LedGreen",            self.s3_led_green)
        _set("ToEEA.S3LedRed",              self.s3_led_red)
        _set("ToEEA.S3LatencySQNInput",     self.s3_latency_sqn)

        _set("ToEEA.S2LatencySQNInput",     self.s2_latency_sqn)
        _set("ToEEA.S1LatencySQNInput",     self.s1_latency_sqn)

        for i, v in enumerate(self.additional, 1):
            _set(f"ToEEA.AdditionalToS{i}", v)

        return m

    def zero(self) -> None:
        for f in self.__dataclass_fields__:
            if f == "additional":
                self.additional = [0] * 10
            elif f == "estop":
                pass
            else:
                setattr(self, f, 0)

    def safe(self) -> None:
        self.zero()
        self.roi_heartbeat = 1
        self.s3_heartbeat  = 1


# ─── Worker thread ────────────────────────────────────────────────────────────
@dataclass
class WorkerStats:
    samples: int = 0
    errors:  int = 0
    wkc:     int = 0


class EcatWorker:
    def __init__(
        self,
        adapter: str,
        slave_hint: str,
        period_ms: float,
        out_state: OutputState,
        pvars: list[ProcessVar],
        q: queue.Queue,
    ) -> None:
        self._adapter    = adapter
        self._hint       = slave_hint.lower()
        self._period     = max(1.0, period_ms) / 1000.0
        self._out        = out_state
        self._pvars      = pvars
        self._q          = q
        self.stats       = WorkerStats()
        self._stop       = threading.Event()
        self._thread     = threading.Thread(target=self._run, daemon=True, name="ecat-worker")

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def join(self, timeout: float = 3.0) -> None:
        self._thread.join(timeout)

    def _log(self, tag: str, msg: str) -> None:
        self._q.put((tag, msg))

    def _find_slave(self, m: pysoem.Master):
        for s in m.slaves:
            if self._hint and self._hint in (s.name or "").lower():
                return s
        return m.slaves[0] if m.slaves else None

    def _run(self) -> None:
        m = pysoem.Master()
        try:
            m.open(self._adapter)
            n = m.config_init()
            if n <= 0:
                self._log("ERROR", "No EtherCAT slaves found")
                return

            s = self._find_slave(m)
            if s is None:
                self._log("ERROR", "Gateway slave not found on bus")
                return

            m.config_map()
            m.state_check(pysoem.SAFEOP_STATE, TIMEOUT_US)
            m.state = pysoem.OP_STATE
            m.write_state()
            m.state_check(pysoem.OP_STATE, TIMEOUT_US)
            self._log("INFO", f"Connected  slave='{s.name}'  in_sz={len(s.input)}  out_sz={len(s.output)}")

            while not self._stop.is_set():
                # Build output image
                if self._out.estop:
                    out_bytes = bytes(len(s.output))
                else:
                    fmap = self._out.to_field_map(self._pvars)
                    out_bytes = encode_process_image(fmap, self._pvars)
                    # Pad / trim to exact slave buffer size
                    if len(out_bytes) < len(s.output):
                        out_bytes = out_bytes + bytes(len(s.output) - len(out_bytes))
                    else:
                        out_bytes = out_bytes[: len(s.output)]

                s.output = out_bytes
                wkc = m.send_processdata()
                m.receive_processdata(TIMEOUT_US)

                self.stats.samples += 1
                self.stats.wkc      = int(wkc)

                raw_in = bytes(s.input)
                decoded = decode_process_image(raw_in, self._pvars, "inputs")
                self._q.put(("PDO", decoded))

                time.sleep(self._period)

        except Exception as exc:
            self.stats.errors += 1
            self._log("ERROR", str(exc))
        finally:
            try:
                m.state = pysoem.PREOP_STATE
                m.write_state()
                m.close()
            except Exception:
                pass
            self._log("INFO", "Disconnected")


# ─── GUI ──────────────────────────────────────────────────────────────────────
class EeaGatewayPanel:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("EEA Gateway Command Panel")
        self.root.geometry("1280x900")
        self.root.minsize(960, 700)

        self.pvars     = load_gateway_process_map()
        self.out_state = OutputState()
        self.q: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.worker: EcatWorker | None = None
        self._last_decoded: dict[str, int] = {}
        self._latency_running = False
        self._latency_sqn     = 0
        self._csv_writer      = None
        self._csv_file        = None

        self._adapter_map: dict[str, str] = {}

        # status bar vars
        self.sv_status  = tk.StringVar(value="Disconnected")
        self.sv_stats   = tk.StringVar(value="samples=0  errors=0  wkc=0")
        self.sv_estop   = tk.StringVar(value="")

        self._build_ui()
        self._refresh_adapters()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(UI_TICK_MS, self._ui_tick)

    # ── UI construction ───────────────────────────────────────────────
    def _build_ui(self) -> None:
        # Top status bar
        sbar = ttk.Frame(self.root)
        sbar.pack(fill="x", side="bottom", padx=8, pady=2)
        ttk.Label(sbar, textvariable=self.sv_status, anchor="w").pack(side="left", padx=8)
        ttk.Label(sbar, textvariable=self.sv_stats, anchor="w").pack(side="left", padx=8)
        ttk.Label(sbar, textvariable=self.sv_estop, foreground="red", font=("", 10, "bold")).pack(side="right", padx=8)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_tab_connect()
        self._build_tab_roi()
        self._build_tab_eea()
        self._build_tab_inputs()
        self._build_tab_log()

    # ── Tab 1: Connect ────────────────────────────────────────────────
    def _build_tab_connect(self) -> None:
        f = ttk.Frame(self.nb, padding=16)
        self.nb.add(f, text="1  Connect")

        # Adapter
        row = ttk.Frame(f)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Ethernet adapter:", width=18).pack(side="left")
        self.sv_adapter = tk.StringVar()
        self.combo_adapter = ttk.Combobox(row, textvariable=self.sv_adapter, state="readonly", width=70)
        self.combo_adapter.pack(side="left", padx=6, fill="x", expand=True)
        ttk.Button(row, text="Refresh", command=self._refresh_adapters).pack(side="left", padx=4)

        # Slave hint
        row2 = ttk.Frame(f)
        row2.pack(fill="x", pady=4)
        ttk.Label(row2, text="Slave name hint:", width=18).pack(side="left")
        self.sv_slave = tk.StringVar(value=DEFAULT_SLAVE)
        ttk.Entry(row2, textvariable=self.sv_slave, width=34).pack(side="left", padx=6)

        # Period
        ttk.Label(row2, text="Period ms:", width=12).pack(side="left")
        self.sv_period = tk.StringVar(value=str(DEFAULT_PERIOD_MS))
        ttk.Entry(row2, textvariable=self.sv_period, width=8).pack(side="left", padx=6)

        # Connect / Disconnect / E-STOP
        btns = ttk.Frame(f)
        btns.pack(fill="x", pady=12)
        self.btn_connect = ttk.Button(btns, text="Connect", command=self._toggle_connect, width=18)
        self.btn_connect.pack(side="left", padx=6)
        ttk.Button(btns, text="E-STOP  (zero all)", command=self._cmd_estop,
                   style="Estop.TButton", width=22).pack(side="left", padx=6)
        ttk.Button(btns, text="Safe State", command=self._cmd_safe, width=16).pack(side="left", padx=6)

        style = ttk.Style()
        style.configure("Estop.TButton", foreground="red", font=("", 10, "bold"))

        # CSV capture
        capf = ttk.LabelFrame(f, text="CSV Capture", padding=8)
        capf.pack(fill="x", pady=8)
        self.sv_csv_path   = tk.StringVar(value=CAPTURE_PATH_DEF)
        self.bv_csv_enable = tk.BooleanVar(value=False)
        ttk.Checkbutton(capf, text="Enable capture", variable=self.bv_csv_enable,
                        command=self._toggle_csv).pack(side="left")
        ttk.Entry(capf, textvariable=self.sv_csv_path, width=80).pack(side="left", padx=6, fill="x", expand=True)
        ttk.Button(capf, text="Browse", command=self._browse_csv).pack(side="left")

        # Quick-action summary
        info = ttk.LabelFrame(f, text="Quick Reference — Output Commands", padding=8)
        info.pack(fill="x", pady=4)
        lines = [
            "Tab 2 ToROI  → controls for ROI station S4 (heartbeat, LED, brightness, blink, latency)",
            "Tab 3 ToEEA  → controls for EEA stations S3 full / S2+S1 latency only / Additional S1-S10",
            "Tab 4 Inputs → live decoded view of all 39 input fields (auto-refreshes every UI tick)",
            "Tab 5 Log    → raw hex PDO stream + timestamped events",
            "E-STOP        → zeros all output bytes immediately (stays zeroed until cleared)",
            "Safe State    → heartbeat=1, all LEDs off, all others zero",
        ]
        for ln in lines:
            ttk.Label(info, text=ln, anchor="w").pack(fill="x")

    # ── Tab 2: ToROI ──────────────────────────────────────────────────
    def _build_tab_roi(self) -> None:
        f = ttk.Frame(self.nb, padding=12)
        self.nb.add(f, text="2  ToROI (S4)")

        self._roi_vars = self._make_field_block(
            f,
            title="ToROI — S4 (ROI station) Output Fields",
            fields=[
                ("S4 Heartbeat",        "roi_heartbeat",        "0-255"),
                ("S4 Terminator",       "roi_terminator",       "0-255"),
                ("S4 BrightnessBlinkrate", "roi_brightness_blink", "high-nibble=bright 0-15, low-nibble=blink 0-15"),
                ("S4 LED Blue",         "roi_led_blue",         "0-255"),
                ("S4 LED Green",        "roi_led_green",        "0-255"),
                ("S4 LED Red",          "roi_led_red",          "0-255"),
                ("S4 Latency SQN",      "roi_latency_sqn",      "uint16"),
            ],
        )

        btns = ttk.LabelFrame(f, text="S4 Quick Commands", padding=8)
        btns.pack(fill="x", pady=6)

        rows = [
            # (label, callback)
            ("LED Off",           lambda: self._roi_led(0, 0, 0)),
            ("LED Red",           lambda: self._roi_led(0, 0, 255)),
            ("LED Green",         lambda: self._roi_led(0, 255, 0)),
            ("LED Blue",          lambda: self._roi_led(255, 0, 0)),
            ("LED White",         lambda: self._roi_led(255, 255, 255)),
            ("Brightness Max",    lambda: self._roi_bb(0xF0)),
            ("Brightness Off",    lambda: self._roi_bb(0x00)),
            ("Blink Slow (0x01)", lambda: self._roi_bb(0x01)),
            ("Blink Fast (0x0F)", lambda: self._roi_bb(0x0F)),
            ("HB Step +1",        self._roi_hb_step),
            ("Latency SQN +1",    self._roi_lat_step),
            ("Reset All S4",      self._roi_reset),
        ]
        for i, (lbl, cb) in enumerate(rows):
            ttk.Button(btns, text=lbl, command=cb, width=18).grid(
                row=i // 4, column=i % 4, padx=4, pady=3, sticky="w"
            )

    # ── Tab 3: ToEEA ─────────────────────────────────────────────────
    def _build_tab_eea(self) -> None:
        f = ttk.Frame(self.nb, padding=12)
        self.nb.add(f, text="3  ToEEA (S3/S2/S1)")

        self._eea_vars = self._make_field_block(
            f,
            title="ToEEA — S3 Full Fields",
            fields=[
                ("S3 Heartbeat",         "s3_heartbeat",        "0-255"),
                ("S3 Terminator",        "s3_terminator",       "0-255"),
                ("S3 BrightnessBlinkrate","s3_brightness_blink","high-nibble=bright, low-nibble=blink"),
                ("S3 LED Blue",          "s3_led_blue",         "0-255"),
                ("S3 LED Green",         "s3_led_green",        "0-255"),
                ("S3 LED Red",           "s3_led_red",          "0-255"),
                ("S3 Latency SQN",       "s3_latency_sqn",      "uint16"),
                ("S2 Latency SQN",       "s2_latency_sqn",      "uint16"),
                ("S1 Latency SQN",       "s1_latency_sqn",      "uint16"),
            ],
        )

        btns = ttk.LabelFrame(f, text="S3 Quick Commands", padding=8)
        btns.pack(fill="x", pady=4)
        rows = [
            ("LED Off",           lambda: self._eea_led(0, 0, 0)),
            ("LED Red",           lambda: self._eea_led(0, 0, 255)),
            ("LED Green",         lambda: self._eea_led(0, 255, 0)),
            ("LED Blue",          lambda: self._eea_led(255, 0, 0)),
            ("LED White",         lambda: self._eea_led(255, 255, 255)),
            ("Brightness Max",    lambda: self._eea_bb(0xF0)),
            ("Brightness Off",    lambda: self._eea_bb(0x00)),
            ("Blink Slow (0x01)", lambda: self._eea_bb(0x01)),
            ("Blink Fast (0x0F)", lambda: self._eea_bb(0x0F)),
            ("HB Step +1",        self._eea_hb_step),
            ("S3 Lat SQN +1",     self._eea_s3_lat_step),
            ("S2 Lat SQN +1",     self._eea_s2_lat_step),
            ("S1 Lat SQN +1",     self._eea_s1_lat_step),
            ("Start Auto-Lat",    self._lat_start),
            ("Stop Auto-Lat",     self._lat_stop),
            ("Reset All S3",      self._eea_reset),
        ]
        for i, (lbl, cb) in enumerate(rows):
            ttk.Button(btns, text=lbl, command=cb, width=18).grid(
                row=i // 4, column=i % 4, padx=4, pady=3, sticky="w"
            )

        # Additional channels
        addlf = ttk.LabelFrame(f, text="Additional Output Channels  (ToEEA.AdditionalToS1-S10)", padding=8)
        addlf.pack(fill="x", pady=6)
        self._add_vars: list[tk.StringVar] = []
        for i in range(10):
            ttk.Label(addlf, text=f"S{i+1}:").grid(row=i // 5, column=(i % 5) * 2, padx=4, pady=2)
            sv = tk.StringVar(value="0")
            ttk.Entry(addlf, textvariable=sv, width=8).grid(row=i // 5, column=(i % 5) * 2 + 1, padx=4, pady=2)
            self._add_vars.append(sv)
        ttk.Button(addlf, text="Apply Additional", command=self._apply_additional).grid(
            row=2, column=0, columnspan=10, pady=4
        )

    # ── Tab 4: Input Status ───────────────────────────────────────────
    def _build_tab_inputs(self) -> None:
        f = ttk.Frame(self.nb, padding=8)
        self.nb.add(f, text="4  Input Status")

        cols = ("field", "value", "decoded")
        self.tv_inputs = ttk.Treeview(f, columns=cols, show="headings", height=30)
        self.tv_inputs.heading("field",   text="Variable")
        self.tv_inputs.heading("value",   text="Raw (dec / hex)")
        self.tv_inputs.heading("decoded", text="Decoded")
        self.tv_inputs.column("field",   width=500)
        self.tv_inputs.column("value",   width=140)
        self.tv_inputs.column("decoded", width=360)

        vsb = ttk.Scrollbar(f, orient="vertical", command=self.tv_inputs.yview)
        self.tv_inputs.configure(yscrollcommand=vsb.set)
        self.tv_inputs.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Pre-populate rows
        input_vars = [v for v in self.pvars if v.direction == "inputs"]
        for var in input_vars:
            short = var.name.replace("EFlexEthercatModbusRTUGateway.", "")
            self.tv_inputs.insert("", "end", iid=var.name, values=(short, "-", "-"))

    # ── Tab 5: Log ────────────────────────────────────────────────────
    def _build_tab_log(self) -> None:
        f = ttk.Frame(self.nb, padding=8)
        self.nb.add(f, text="5  Debug Log")

        bar = ttk.Frame(f)
        bar.pack(fill="x")
        ttk.Button(bar, text="Clear", command=self._clear_log).pack(side="left", padx=4)
        self.bv_raw_hex = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Show raw hex every cycle", variable=self.bv_raw_hex).pack(side="left", padx=8)

        self.log = scrolledtext.ScrolledText(f, wrap="none", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True)

    # ── Field block helper ────────────────────────────────────────────
    def _make_field_block(
        self,
        parent: ttk.Frame,
        title: str,
        fields: list[tuple[str, str, str]],
    ) -> dict[str, tk.StringVar]:
        """Render labelled entries for a set of output fields.

        Returns dict of {attr_name: StringVar}.
        """
        lf = ttk.LabelFrame(parent, text=title, padding=10)
        lf.pack(fill="x", pady=6)
        svars: dict[str, tk.StringVar] = {}
        for i, (label, attr, hint) in enumerate(fields):
            ttk.Label(lf, text=label, anchor="e", width=26).grid(row=i, column=0, padx=4, pady=3, sticky="e")
            cur = getattr(self.out_state, attr)
            sv = tk.StringVar(value=str(cur))
            ttk.Entry(lf, textvariable=sv, width=10).grid(row=i, column=1, padx=4, pady=3, sticky="w")
            ttk.Label(lf, text=hint, foreground="gray").grid(row=i, column=2, padx=8, sticky="w")
            sv.trace_add("write", lambda *_, _a=attr, _sv=sv: self._field_changed(_a, _sv))
            svars[attr] = sv
        ttk.Button(lf, text="Apply", command=lambda: self._apply_block(svars)).grid(
            row=len(fields), column=0, columnspan=3, pady=6
        )
        return svars

    def _field_changed(self, attr: str, sv: tk.StringVar) -> None:
        try:
            val = int(sv.get(), 0)
            if attr == "additional":
                return
            setattr(self.out_state, attr, val)
        except ValueError:
            pass

    def _apply_block(self, svars: dict[str, tk.StringVar]) -> None:
        for attr, sv in svars.items():
            try:
                setattr(self.out_state, attr, int(sv.get(), 0))
            except ValueError:
                pass

    # ── Connect/Disconnect ────────────────────────────────────────────
    def _refresh_adapters(self) -> None:
        self._adapter_map.clear()
        labels: list[str] = []
        for a in pysoem.find_adapters():
            lbl = f"{a.desc} | {a.name}"
            self._adapter_map[lbl] = str(a.name)
            labels.append(lbl)
        self.combo_adapter["values"] = labels
        if labels and not self.sv_adapter.get():
            sel = labels[0]
            for lbl in labels:
                if DEFAULT_ADAPTER.lower() in lbl.lower():
                    sel = lbl
                    break
            self.sv_adapter.set(sel)

    def _toggle_connect(self) -> None:
        if self.worker is not None:
            self.worker.stop()
            self.worker.join()
            self.worker = None
            self.btn_connect.configure(text="Connect")
            self.sv_status.set("Disconnected")
            return

        lbl = self.sv_adapter.get().strip()
        adapter_name = self._adapter_map.get(lbl, "")
        if not adapter_name:
            self._log("ERROR", "No adapter selected")
            return

        try:
            period = float(self.sv_period.get())
        except ValueError:
            period = DEFAULT_PERIOD_MS

        self.worker = EcatWorker(
            adapter   = adapter_name,
            slave_hint= self.sv_slave.get(),
            period_ms = period,
            out_state = self.out_state,
            pvars     = self.pvars,
            q         = self.q,
        )
        self.worker.start()
        self.btn_connect.configure(text="Disconnect")
        self.sv_status.set("Connecting…")

    # ── Command callbacks — ToROI ─────────────────────────────────────
    def _roi_led(self, b: int, g: int, r: int) -> None:
        self.out_state.roi_led_blue  = b
        self.out_state.roi_led_green = g
        self.out_state.roi_led_red   = r
        self._sync_roi_vars()

    def _roi_bb(self, v: int) -> None:
        self.out_state.roi_brightness_blink = v
        self._sync_roi_vars()

    def _roi_hb_step(self) -> None:
        self.out_state.roi_heartbeat = (self.out_state.roi_heartbeat + 1) & 0xFF
        self._sync_roi_vars()

    def _roi_lat_step(self) -> None:
        self.out_state.roi_latency_sqn = (self.out_state.roi_latency_sqn + 1) & 0xFFFF
        self._sync_roi_vars()

    def _roi_reset(self) -> None:
        for attr in ("roi_heartbeat", "roi_terminator", "roi_brightness_blink",
                     "roi_led_blue", "roi_led_green", "roi_led_red", "roi_latency_sqn"):
            default = 1 if attr in ("roi_heartbeat",) else 0
            setattr(self.out_state, attr, default)
        self._sync_roi_vars()

    def _sync_roi_vars(self) -> None:
        if not hasattr(self, "_roi_vars"):
            return
        for attr, sv in self._roi_vars.items():
            sv.set(str(getattr(self.out_state, attr)))

    # ── Command callbacks — ToEEA ─────────────────────────────────────
    def _eea_led(self, b: int, g: int, r: int) -> None:
        self.out_state.s3_led_blue  = b
        self.out_state.s3_led_green = g
        self.out_state.s3_led_red   = r
        self._sync_eea_vars()

    def _eea_bb(self, v: int) -> None:
        self.out_state.s3_brightness_blink = v
        self._sync_eea_vars()

    def _eea_hb_step(self) -> None:
        self.out_state.s3_heartbeat = (self.out_state.s3_heartbeat + 1) & 0xFF
        self._sync_eea_vars()

    def _eea_s3_lat_step(self) -> None:
        self.out_state.s3_latency_sqn = (self.out_state.s3_latency_sqn + 1) & 0xFFFF
        self._sync_eea_vars()

    def _eea_s2_lat_step(self) -> None:
        self.out_state.s2_latency_sqn = (self.out_state.s2_latency_sqn + 1) & 0xFFFF
        self._sync_eea_vars()

    def _eea_s1_lat_step(self) -> None:
        self.out_state.s1_latency_sqn = (self.out_state.s1_latency_sqn + 1) & 0xFFFF
        self._sync_eea_vars()

    def _eea_reset(self) -> None:
        for attr in ("s3_heartbeat", "s3_terminator", "s3_brightness_blink",
                     "s3_led_blue", "s3_led_green", "s3_led_red",
                     "s3_latency_sqn", "s2_latency_sqn", "s1_latency_sqn"):
            setattr(self.out_state, attr, 1 if "heartbeat" in attr else 0)
        self._sync_eea_vars()

    def _sync_eea_vars(self) -> None:
        if not hasattr(self, "_eea_vars"):
            return
        for attr, sv in self._eea_vars.items():
            sv.set(str(getattr(self.out_state, attr)))

    def _lat_start(self) -> None:
        self._latency_running = True
        self._log("INFO", "Auto-latency sequencing started")

    def _lat_stop(self) -> None:
        self._latency_running = False
        self._log("INFO", "Auto-latency sequencing stopped")

    def _apply_additional(self) -> None:
        for i, sv in enumerate(self._add_vars):
            try:
                self.out_state.additional[i] = int(sv.get(), 0) & 0xFFFF
            except ValueError:
                pass
        self._log("INFO", f"Additional outputs applied: {self.out_state.additional}")

    # ── E-stop / Safe ─────────────────────────────────────────────────
    def _cmd_estop(self) -> None:
        self.out_state.estop = True
        self.sv_estop.set("⚠ E-STOP ACTIVE")
        self._log("ESTOP", "All outputs zeroed — E-STOP engaged")

    def _cmd_safe(self) -> None:
        self.out_state.estop = False
        self.out_state.safe()
        self.sv_estop.set("")
        self._sync_roi_vars()
        self._sync_eea_vars()
        self._log("INFO", "Safe state applied — heartbeat=1, all LEDs off")

    # ── CSV capture ───────────────────────────────────────────────────
    def _toggle_csv(self) -> None:
        if self.bv_csv_enable.get():
            path = Path(self.sv_csv_path.get())
            path.parent.mkdir(parents=True, exist_ok=True)
            is_new = not path.exists()
            self._csv_file   = open(path, "a", newline="")
            self._csv_writer = csv.writer(self._csv_file)
            if is_new:
                header = ["timestamp"] + [v.name.replace("EFlexEthercatModbusRTUGateway.", "") for v in self.pvars if v.direction == "inputs"]
                self._csv_writer.writerow(header)
            self._log("INFO", f"CSV capture open: {path}")
        else:
            if self._csv_file:
                self._csv_file.close()
                self._csv_file   = None
                self._csv_writer = None
            self._log("INFO", "CSV capture closed")

    def _browse_csv(self) -> None:
        p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if p:
            self.sv_csv_path.set(p)

    # ── UI tick ───────────────────────────────────────────────────────
    def _ui_tick(self) -> None:
        try:
            while True:
                tag, payload = self.q.get_nowait()

                if tag == "PDO":
                    self._last_decoded = payload
                    self._update_input_table(payload)
                    if self.bv_raw_hex.get():
                        row_vals = list(payload.values())
                        self._log("HEX", " ".join(f"{v:04x}" for v in row_vals[:12]) + " …")
                    if self._csv_writer:
                        ts = time.strftime("%Y-%m-%dT%H:%M:%S")
                        row = [ts] + [payload.get(v.name, 0) for v in self.pvars if v.direction == "inputs"]
                        self._csv_writer.writerow(row)

                elif tag == "INFO":
                    self._log("INFO", payload)
                    if "Connected" in payload:
                        self.sv_status.set(payload)
                    elif "Disconnected" in payload:
                        self.sv_status.set("Disconnected")
                        if self.worker:
                            self.btn_connect.configure(text="Connect")
                            self.worker = None

                elif tag == "ERROR":
                    self._log("ERROR", payload)
                    self.sv_status.set(f"ERROR: {payload[:60]}")

                elif tag == "ESTOP":
                    self._log("ESTOP", payload)

        except queue.Empty:
            pass

        # Update stats
        if self.worker:
            s = self.worker.stats
            self.sv_stats.set(f"samples={s.samples}  errors={s.errors}  wkc={s.wkc}")

        # Auto-increment latency SQN
        if self._latency_running and self.worker:
            self._latency_sqn = (self._latency_sqn + 1) & 0xFFFF
            self.out_state.s1_latency_sqn = self._latency_sqn
            self.out_state.s2_latency_sqn = self._latency_sqn
            self.out_state.s3_latency_sqn = self._latency_sqn
            self.out_state.roi_latency_sqn = self._latency_sqn

        self.root.after(UI_TICK_MS, self._ui_tick)

    def _update_input_table(self, decoded: dict[str, int]) -> None:
        p = "EFlexEthercatModbusRTUGateway."
        for var in self.pvars:
            if var.direction != "inputs":
                continue
            val = decoded.get(var.name, 0)
            decoded_txt = ""

            short = var.name.replace(p, "")
            if "GeneralInfo" in var.name:
                gi = decode_general_info(val)
                decoded_txt = f"fw {gi.fw_part_num}.{gi.fw_part_rev}.{gi.fw_build_num}  des={gi.designator}"
            elif "BrightnessBlinkrate" in var.name:
                b, bk = decode_led_brightness_blink(val)
                decoded_txt = f"bright={b}  blink={bk}"
            elif "Led" in var.name:
                decoded_txt = f"{'ON' if val else 'off'}"

            self.tv_inputs.item(var.name, values=(short, f"{val} / 0x{val:04x}", decoded_txt))

    def _log(self, tag: str, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}][{tag:5s}] {msg}\n")
        self.log.see("end")

    def _clear_log(self) -> None:
        self.log.delete("1.0", "end")

    def _on_close(self) -> None:
        if self.worker:
            self.worker.stop()
            self.worker.join(2.0)
        if self._csv_file:
            self._csv_file.close()
        self.root.destroy()


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = EeaGatewayPanel(root)
    root.mainloop()
