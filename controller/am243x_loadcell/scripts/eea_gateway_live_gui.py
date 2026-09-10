#!/usr/bin/env python3
"""Live EtherCAT host GUI for EEA gateway reverse engineering.

Purpose:
- Connect to the Hilscher EtherCAT/Modbus-RTU gateway.
- Read and decode mapped process image fields with verbose debug output.
- Write selected output controls (heartbeat, LED, latency sequence) to gateway PDO output.

This mirrors the load-cell GUI workflow, but focused on the EEA gateway map.
"""

from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from tkinter import scrolledtext, ttk

import pysoem

from eea_gateway_map import (
    decode_general_info,
    decode_led_brightness_blink,
    decode_process_image,
    load_gateway_process_map,
)


UI_TICK_MS = 100
TIMEOUT_US = 50000
DEFAULT_PERIOD_MS = 10.0
DEFAULT_ADAPTER_HINT = "Realtek"
DEFAULT_SLAVE_HINT = "EFlexEthercatModbusRTUGateway"


@dataclass
class LoopStats:
    samples: int = 0
    errors: int = 0
    last_wkc: int = 0


class EeaGatewayGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("EEA Gateway EtherCAT Live GUI")
        self.root.geometry("1220x840")

        self.process_vars = load_gateway_process_map()
        self.q: queue.Queue[tuple[str, str]] = queue.Queue()

        self.master: pysoem.Master | None = None
        self.slave: pysoem.CdefSlave | None = None

        self.stop_evt = threading.Event()
        self.worker: threading.Thread | None = None
        self.stats = LoopStats()

        self.adapter_var = tk.StringVar(value="")
        self.slave_hint_var = tk.StringVar(value=DEFAULT_SLAVE_HINT)
        self.period_var = tk.StringVar(value=str(DEFAULT_PERIOD_MS))

        self.hb_var = tk.StringVar(value="1")
        self.term_var = tk.StringVar(value="0")
        self.bright_blink_var = tk.StringVar(value="0x11")
        self.led_blue_var = tk.StringVar(value="0")
        self.led_green_var = tk.StringVar(value="0")
        self.led_red_var = tk.StringVar(value="0")
        self.lat_seq_var = tk.StringVar(value="1")

        self.status_var = tk.StringVar(value="Disconnected")
        self.sample_var = tk.StringVar(value="samples=0 errors=0 wkc=0")
        self.decoded_var = tk.StringVar(value="-")

        self.adapter_name_by_label: dict[str, str] = {}
        self._build_ui()
        self.refresh_adapters()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(UI_TICK_MS, self.ui_tick)

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")

        ttk.Label(top, text="Adapter:").pack(side="left")
        self.adapter_combo = ttk.Combobox(top, textvariable=self.adapter_var, state="readonly", width=60)
        self.adapter_combo.pack(side="left", padx=(6, 8), fill="x", expand=True)
        ttk.Button(top, text="Refresh", command=self.refresh_adapters).pack(side="left", padx=(0, 8))

        ttk.Label(top, text="Slave hint:").pack(side="left")
        ttk.Entry(top, textvariable=self.slave_hint_var, width=34).pack(side="left", padx=(6, 8))

        ttk.Label(top, text="Period ms:").pack(side="left")
        ttk.Entry(top, textvariable=self.period_var, width=8).pack(side="left", padx=(6, 8))

        self.conn_btn = ttk.Button(top, text="Connect", command=self.toggle_connect)
        self.conn_btn.pack(side="left")

        ctl = ttk.LabelFrame(self.root, text="ToEEA / ToROI Output Controls", padding=8)
        ctl.pack(fill="x", padx=8, pady=(0, 8))

        fields = [
            ("Heartbeat", self.hb_var),
            ("Terminator", self.term_var),
            ("BrightBlink", self.bright_blink_var),
            ("LED Blue", self.led_blue_var),
            ("LED Green", self.led_green_var),
            ("LED Red", self.led_red_var),
            ("Latency Seq", self.lat_seq_var),
        ]
        for i, (label, var) in enumerate(fields):
            ttk.Label(ctl, text=label).grid(row=0, column=i * 2, sticky="e", padx=4, pady=2)
            ttk.Entry(ctl, textvariable=var, width=8).grid(row=0, column=i * 2 + 1, sticky="w", padx=4, pady=2)
        ttk.Button(ctl, text="Apply Outputs", command=self.apply_outputs_once).grid(row=0, column=len(fields) * 2, padx=8)

        st = ttk.LabelFrame(self.root, text="Status", padding=8)
        st.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Label(st, textvariable=self.status_var).grid(row=0, column=0, sticky="w", padx=6)
        ttk.Label(st, textvariable=self.sample_var).grid(row=0, column=1, sticky="w", padx=6)
        ttk.Label(st, textvariable=self.decoded_var).grid(row=1, column=0, columnspan=2, sticky="w", padx=6)

        log_frame = ttk.LabelFrame(self.root, text="Verbose Debug Stream", padding=8)
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.log = scrolledtext.ScrolledText(log_frame, wrap="none", font=("Consolas", 10))
        self.log.pack(fill="both", expand=True)

    def refresh_adapters(self) -> None:
        self.adapter_name_by_label.clear()
        labels: list[str] = []
        for adapter in pysoem.find_adapters():
            label = f"{adapter.desc} | {adapter.name}"
            self.adapter_name_by_label[label] = str(adapter.name)
            labels.append(label)
        self.adapter_combo["values"] = labels
        if labels and not self.adapter_var.get():
            # Prefer adapter containing the default hint.
            selected = labels[0]
            for lbl in labels:
                if DEFAULT_ADAPTER_HINT.lower() in lbl.lower():
                    selected = lbl
                    break
            self.adapter_var.set(selected)

    def toggle_connect(self) -> None:
        if self.worker and self.worker.is_alive():
            self.stop_evt.set()
            self.conn_btn.configure(text="Connect")
            return

        adapter_label = self.adapter_var.get().strip()
        if not adapter_label:
            self._log("ERROR", "No adapter selected")
            return

        self.stop_evt.clear()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        self.conn_btn.configure(text="Disconnect")

    def _select_slave(self, m: pysoem.Master) -> pysoem.CdefSlave | None:
        hint = self.slave_hint_var.get().strip().lower()
        for s in m.slaves:
            n = (s.name or "").lower()
            if hint and hint in n:
                return s
        return m.slaves[0] if m.slaves else None

    def _build_output_image(self) -> bytes:
        # Build the first ToROI and ToEEA controls in little-endian layout.
        hb = int(self.hb_var.get(), 0) & 0xFF
        term = int(self.term_var.get(), 0) & 0xFF
        bright = int(self.bright_blink_var.get(), 0) & 0xFF
        led_b = int(self.led_blue_var.get(), 0) & 0xFF
        led_g = int(self.led_green_var.get(), 0) & 0xFF
        led_r = int(self.led_red_var.get(), 0) & 0xFF
        lat = int(self.lat_seq_var.get(), 0) & 0xFFFF

        # Output image is 40 bytes in this map region.
        out = bytearray(40)

        # ToROI (offset 0 in slave output image for this PDO region)
        out[0] = hb
        out[1] = term
        out[2] = bright
        out[3] = led_b
        out[4] = led_g
        out[5] = led_r
        out[6:8] = lat.to_bytes(2, "little")

        # ToEEA starts at byte 8 in this gateway block.
        out[8] = hb
        out[9] = term
        out[10] = bright
        out[11] = led_b
        out[12] = led_g
        out[13] = led_r
        out[14:16] = lat.to_bytes(2, "little")
        return bytes(out)

    def apply_outputs_once(self) -> None:
        if not self.slave:
            self._log("WARN", "Not connected; cannot apply outputs")
            return
        try:
            self.slave.output = self._build_output_image()
            self._log("TX", f"Applied output image: {self.slave.output.hex()}")
        except Exception as exc:
            self._log("ERROR", f"apply output failed: {exc}")

    def _worker_loop(self) -> None:
        try:
            period = max(1.0, float(self.period_var.get().strip())) / 1000.0
        except Exception:
            period = DEFAULT_PERIOD_MS / 1000.0

        adapter_name = self.adapter_name_by_label.get(self.adapter_var.get().strip(), "")
        if not adapter_name:
            self.q.put(("ERROR", "Adapter lookup failed"))
            return

        m = pysoem.Master()
        try:
            m.open(adapter_name)
            n = m.config_init()
            if n <= 0:
                self.q.put(("ERROR", "No EtherCAT slaves found"))
                return

            s = self._select_slave(m)
            if s is None:
                self.q.put(("ERROR", "Gateway slave not found"))
                return

            m.config_map()
            m.state_check(pysoem.SAFEOP_STATE, TIMEOUT_US)
            m.state = pysoem.OP_STATE
            m.write_state()
            m.state_check(pysoem.OP_STATE, TIMEOUT_US)

            self.master = m
            self.slave = s
            self.q.put(("INFO", f"Connected to slave: {s.name}"))

            while not self.stop_evt.is_set():
                s.output = self._build_output_image()
                wkc = m.send_processdata()
                m.receive_processdata(TIMEOUT_US)

                self.stats.samples += 1
                self.stats.last_wkc = int(wkc)

                raw_in = bytes(s.input)
                decoded = decode_process_image(raw_in, self.process_vars, "inputs")

                g_s1 = int(decoded.get("EFlexEthercatModbusRTUGateway.FromEEA.S1GeneralInfo", 0))
                g_s2 = int(decoded.get("EFlexEthercatModbusRTUGateway.FromEEA.S2GeneralInfo", 0))
                g_s3 = int(decoded.get("EFlexEthercatModbusRTUGateway.FromEEA.S3GeneralInfo", 0))
                roi_g = int(decoded.get("EFlexEthercatModbusRTUGateway.FromROI.S4GeneralInfo", 0))

                s1_cfg = decode_general_info(g_s1)
                s2_cfg = decode_general_info(g_s2)
                s3_cfg = decode_general_info(g_s3)
                roi_cfg = decode_general_info(roi_g)

                bright_blink = int(decoded.get("EFlexEthercatModbusRTUGateway.FromEEA.S3BrightnessBlinkrate", 0))
                b, p = decode_led_brightness_blink(bright_blink)

                line = (
                    f"wkc={wkc} S1fw={s1_cfg.fw_part_num}.{s1_cfg.fw_part_rev}.{s1_cfg.fw_build_num} "
                    f"S2fw={s2_cfg.fw_part_num}.{s2_cfg.fw_part_rev}.{s2_cfg.fw_build_num} "
                    f"S3fw={s3_cfg.fw_part_num}.{s3_cfg.fw_part_rev}.{s3_cfg.fw_build_num} "
                    f"ROIfw={roi_cfg.fw_part_num}.{roi_cfg.fw_part_rev}.{roi_cfg.fw_build_num} "
                    f"S3_led(bright={b},blink={p})"
                )
                self.q.put(("DATA", line))
                time.sleep(period)

        except Exception as exc:
            self.stats.errors += 1
            self.q.put(("ERROR", str(exc)))
        finally:
            try:
                if self.master:
                    self.master.state = pysoem.PREOP_STATE
                    self.master.write_state()
                    self.master.close()
            except Exception:
                pass
            self.master = None
            self.slave = None
            self.q.put(("INFO", "Disconnected"))

    def _log(self, tag: str, msg: str) -> None:
        self.log.insert("end", f"[{tag}] {msg}\n")
        self.log.see("end")

    def ui_tick(self) -> None:
        try:
            while True:
                tag, msg = self.q.get_nowait()
                self._log(tag, msg)
                if tag == "DATA":
                    self.decoded_var.set(msg)
                self.sample_var.set(
                    f"samples={self.stats.samples} errors={self.stats.errors} wkc={self.stats.last_wkc}"
                )
                if tag == "INFO" and msg == "Disconnected":
                    self.status_var.set("Disconnected")
                    self.conn_btn.configure(text="Connect")
                elif tag == "INFO" and msg.startswith("Connected"):
                    self.status_var.set(msg)
                elif tag == "ERROR":
                    self.status_var.set(f"Error: {msg}")
        except queue.Empty:
            pass
        self.root.after(UI_TICK_MS, self.ui_tick)

    def on_close(self) -> None:
        self.stop_evt.set()
        self.root.destroy()


if __name__ == "__main__":
    tk_root = tk.Tk()
    app = EeaGatewayGui(tk_root)
    tk_root.mainloop()
