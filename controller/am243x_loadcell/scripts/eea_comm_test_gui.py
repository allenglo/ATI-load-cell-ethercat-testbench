#!/usr/bin/env python3
"""Basic EEA serial/Modbus trial GUI.

Purpose:
- Quickly test COM connectivity.
- Blast common read/write Modbus RTU packets.
- Try LED/register writes by trial and error.
- See raw TX/RX bytes live.
"""

from __future__ import annotations

import struct
import threading
import time
import tkinter as tk
from tkinter import ttk

import serial


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def with_crc(pdu: bytes) -> bytes:
    crc = crc16_modbus(pdu)
    return pdu + struct.pack("<H", crc)


def frame_read(slave: int, fc: int, reg: int, count: int) -> bytes:
    return with_crc(struct.pack(">BBHH", slave, fc, reg, count))


def frame_write_single(slave: int, reg: int, value: int) -> bytes:
    return with_crc(struct.pack(">BBHH", slave, 6, reg, value & 0xFFFF))


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("EEA Comm Test GUI")
        self.ser: serial.Serial | None = None
        self.reader_stop = threading.Event()
        self.reader_thread: threading.Thread | None = None

        self.port_var = tk.StringVar(value="COM18")
        self.baud_var = tk.StringVar(value="115200")
        self.parity_var = tk.StringVar(value="N")
        self.stop_var = tk.StringVar(value="1")
        self.slave_var = tk.StringVar(value="10")

        self.raw_hex_var = tk.StringVar(value="01 03 00 00 00 01")
        self.reg_var = tk.StringVar(value="6")
        self.val_var = tk.StringVar(value="1")

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill="both", expand=True)

        row1 = ttk.Frame(frm)
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="Port").pack(side="left")
        ttk.Entry(row1, textvariable=self.port_var, width=10).pack(side="left", padx=4)
        ttk.Label(row1, text="Baud").pack(side="left")
        ttk.Combobox(row1, textvariable=self.baud_var, width=10, values=["115200", "57600", "38400", "19200", "9600"]).pack(side="left", padx=4)
        ttk.Label(row1, text="Parity").pack(side="left")
        ttk.Combobox(row1, textvariable=self.parity_var, width=4, values=["N", "E", "O"]).pack(side="left", padx=4)
        ttk.Label(row1, text="Stop").pack(side="left")
        ttk.Combobox(row1, textvariable=self.stop_var, width=4, values=["1", "2"]).pack(side="left", padx=4)
        ttk.Label(row1, text="Slave").pack(side="left")
        ttk.Entry(row1, textvariable=self.slave_var, width=6).pack(side="left", padx=4)

        row2 = ttk.Frame(frm)
        row2.pack(fill="x", pady=2)
        ttk.Button(row2, text="Connect", command=self.connect).pack(side="left", padx=2)
        ttk.Button(row2, text="Disconnect", command=self.disconnect).pack(side="left", padx=2)
        ttk.Button(row2, text="Probe Reads", command=self.probe_reads).pack(side="left", padx=8)
        ttk.Button(row2, text="LED Trial Burst", command=self.led_trial_burst).pack(side="left", padx=2)

        row3 = ttk.Frame(frm)
        row3.pack(fill="x", pady=2)
        ttk.Label(row3, text="Reg").pack(side="left")
        ttk.Entry(row3, textvariable=self.reg_var, width=8).pack(side="left", padx=4)
        ttk.Label(row3, text="Val").pack(side="left")
        ttk.Entry(row3, textvariable=self.val_var, width=8).pack(side="left", padx=4)
        ttk.Button(row3, text="Write FC06", command=self.write_fc06).pack(side="left", padx=4)

        row4 = ttk.Frame(frm)
        row4.pack(fill="x", pady=2)
        ttk.Label(row4, text="Raw hex (without CRC is OK)").pack(side="left")
        ttk.Entry(row4, textvariable=self.raw_hex_var, width=52).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(row4, text="Send Raw", command=self.send_raw_hex).pack(side="left", padx=2)

        self.log = tk.Text(frm, height=24, wrap="none")
        self.log.pack(fill="both", expand=True, pady=6)

    def _log(self, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}] {msg}\n")
        self.log.see("end")

    def connect(self) -> None:
        if self.ser and self.ser.is_open:
            self._log("Already connected.")
            return
        try:
            parity_map = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}
            stop_map = {"1": serial.STOPBITS_ONE, "2": serial.STOPBITS_TWO}
            self.ser = serial.Serial(
                port=self.port_var.get().strip(),
                baudrate=int(self.baud_var.get()),
                bytesize=serial.EIGHTBITS,
                parity=parity_map.get(self.parity_var.get().strip().upper(), serial.PARITY_NONE),
                stopbits=stop_map.get(self.stop_var.get().strip(), serial.STOPBITS_ONE),
                timeout=0.05,
                write_timeout=0.5,
            )
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._log("Connected.")
            self.start_reader()
        except Exception as e:
            self._log(f"Connect failed: {e}")

    def disconnect(self) -> None:
        self.stop_reader()
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None
        self._log("Disconnected.")

    def start_reader(self) -> None:
        self.reader_stop.clear()

        def worker() -> None:
            while not self.reader_stop.is_set():
                if not self.ser or not self.ser.is_open:
                    time.sleep(0.05)
                    continue
                try:
                    data = self.ser.read(128)
                    if data:
                        self.root.after(0, lambda d=data: self._log(f"RX {d.hex()}"))
                except Exception as e:
                    self.root.after(0, lambda: self._log(f"Reader error: {e}"))
                    return

        self.reader_thread = threading.Thread(target=worker, daemon=True)
        self.reader_thread.start()

    def stop_reader(self) -> None:
        self.reader_stop.set()
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=0.4)
        self.reader_thread = None

    def send(self, frame: bytes, desc: str) -> None:
        if not self.ser or not self.ser.is_open:
            self._log("Not connected.")
            return
        try:
            self.ser.write(frame)
            self._log(f"TX {desc} :: {frame.hex()}")
        except Exception as e:
            self._log(f"Send failed: {e}")

    def current_slave(self) -> int:
        try:
            return int(self.slave_var.get())
        except Exception:
            return 10

    def probe_reads(self) -> None:
        s = self.current_slave()
        requests = [
            ("FC03 reg0 cnt8", frame_read(s, 3, 0, 8)),
            ("FC04 reg0 cnt8", frame_read(s, 4, 0, 8)),
            ("FC03 reg3 cnt7", frame_read(s, 3, 3, 7)),
            ("FC04 reg3 cnt7", frame_read(s, 4, 3, 7)),
            ("FC03 reg6 cnt4", frame_read(s, 3, 6, 4)),
            ("FC03 reg2880 cnt1", frame_read(s, 3, 2880, 1)),
            ("FC04 reg2880 cnt1", frame_read(s, 4, 2880, 1)),
        ]
        for desc, req in requests:
            self.send(req, desc)
            time.sleep(0.05)

    def write_fc06(self) -> None:
        s = self.current_slave()
        try:
            reg = int(self.reg_var.get())
            val = int(self.val_var.get(), 0)
        except Exception:
            self._log("Bad reg/value.")
            return
        self.send(frame_write_single(s, reg, val), f"FC06 reg{reg} val{val}")

    def led_trial_burst(self) -> None:
        s = self.current_slave()
        vals = [0, 1, 2, 3, 0x00FF, 0x0F0F, 0x1234, 0xFFFF]
        for v in vals:
            self.send(frame_write_single(s, 6, v), f"FC06 reg6 val{v}")
            time.sleep(0.05)

    def send_raw_hex(self) -> None:
        txt = self.raw_hex_var.get().strip().replace(",", " ")
        if not txt:
            return
        try:
            b = bytes.fromhex(txt)
        except Exception:
            self._log("Invalid hex string.")
            return

        # If CRC seems missing and length is enough, append CRC automatically.
        if len(b) >= 4:
            payload = b[:-2]
            given_crc = b[-2:]
            calc = struct.pack("<H", crc16_modbus(payload))
            if given_crc != calc:
                b = with_crc(b)
                self._log("CRC auto-appended.")

        self.send(b, "RAW")

    def on_close(self) -> None:
        self.disconnect()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
