import queue
import threading
import time
import tkinter as tk
from tkinter import ttk

import serial
from serial.tools import list_ports

PREFERRED_PORTS = ["COM10"]
TARGET_HINTS = [
    "XDS110 Class Application/User UART",
    "XDS110",
    "Texas Instruments",
]
BAUD = 115200
RETRY_SECONDS = 2.0

COMMAND_HELP = (
    "Known drive commands: ST=stop, TC=0=zero torque, MO=0=motor off, "
    "MO=1=motor on, UM=5=torque mode, RM=1=ready/reset mode, PX=position, "
    "EC=error code, MO/UM/RM/PX are readbacks."
)

class SerialMonitorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Serial Monitor + Pin Command (Auto-Reconnect)")
        self.root.geometry("900x520")

        self.text = tk.Text(root, wrap="none", font=("Consolas", 10))
        self.text.pack(fill="both", expand=True)

        frame = ttk.Frame(root)
        frame.pack(fill="x")
        self.status = ttk.Label(frame, text="Searching serial port...")
        self.status.pack(side="left", padx=8, pady=6)

        cmd_frame = ttk.Frame(frame)
        cmd_frame.pack(side="right", padx=8)
        ttk.Label(cmd_frame, text="Pin:").pack(side="left")
        self.pin_var = tk.StringVar(value="13")
        self.pin_entry = ttk.Entry(cmd_frame, textvariable=self.pin_var, width=6)
        self.pin_entry.pack(side="left", padx=(4, 4))
        self.pin_entry.bind("<Return>", self.send_pin_command)
        send_btn = ttk.Button(cmd_frame, text="Send", command=self.send_pin_command)
        send_btn.pack(side="left", padx=(0, 6))

        self.cmd_var = tk.StringVar(value="MO")
        ttk.Label(cmd_frame, text="Raw:").pack(side="left")
        self.cmd_entry = ttk.Entry(cmd_frame, textvariable=self.cmd_var, width=12)
        self.cmd_entry.pack(side="left", padx=(4, 4))
        self.cmd_entry.bind("<Return>", self.send_raw_command)
        ttk.Button(cmd_frame, text="Run", command=self.send_raw_command).pack(side="left", padx=(0, 6))

        actions = ttk.Frame(root)
        actions.pack(fill="x", padx=8, pady=(0, 6))
        ttk.Button(actions, text="Snapshot", command=self.snapshot_state).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Stop + Zero + Off", command=self.safe_release).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Prep Torque Mode", command=self.prepare_torque_mode).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Torque On", command=self.motor_on).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Torque Off", command=self.motor_off).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Clear", command=self.clear).pack(side="right", padx=(0, 6))

        self.q: queue.Queue[str] = queue.Queue()
        self.stop_evt = threading.Event()
        self.io_lock = threading.Lock()
        self.ser: serial.Serial | None = None
        self.current_port: str | None = None

        self.q.put(f"[INFO] {COMMAND_HELP}\n")

        t = threading.Thread(target=self.connection_worker, daemon=True)
        t.start()
        self.reader_thread = t

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(50, self.drain_queue)

    def clear(self) -> None:
        self.text.delete("1.0", "end")

    def _port_matches_target(self, info: list_ports.ListPortInfo) -> bool:
        hay = " | ".join(
            [
                str(info.device or ""),
                str(info.description or ""),
                str(info.manufacturer or ""),
                str(info.product or ""),
                str(info.hwid or ""),
            ]
        ).lower()
        return any(h.lower() in hay for h in TARGET_HINTS)

    def _candidate_ports(self) -> list[str]:
        ports = []
        for p in PREFERRED_PORTS:
            if p not in ports:
                ports.append(p)

        for info in list_ports.comports():
            if self._port_matches_target(info) and info.device not in ports:
                ports.append(info.device)

        if self.current_port and self.current_port not in ports:
            ports.insert(0, self.current_port)

        return ports

    def _close_serial(self) -> None:
        with self.io_lock:
            ser = self.ser
            self.ser = None
            self.current_port = None
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass

    def _send_sequence(self, title: str, commands: list[tuple[str, float, int]]) -> None:
        def worker() -> None:
            try:
                with self.io_lock:
                    ser = self.ser
                    port = self.current_port
                    if ser is None or port is None:
                        raise RuntimeError("No connected port")

                    self.q.put(f"[GUI] {title} on {port}\n")
                    for cmd, wait_seconds, read_bytes in commands:
                        ser.write((cmd + "\r").encode("ascii"))
                        ser.flush()
                        time.sleep(wait_seconds)
                        raw = ser.read(ser.in_waiting or read_bytes)
                        response = raw.decode(errors="replace").strip()
                        self.q.put(f"[GUI] {port} << {cmd}\n")
                        if response:
                            self.q.put(f"[{port}] {response}\n")

                self.q.put(f"[GUI] {title} complete\n")
            except Exception as exc:
                self.q.put(f"[GUI] {title} failed: {exc}\n")

        threading.Thread(target=worker, daemon=True).start()

    def snapshot_state(self) -> None:
        self._send_sequence(
            "Snapshot",
            [
                ("MO", 0.04, 256),
                ("UM", 0.04, 256),
                ("RM", 0.04, 256),
                ("EC", 0.04, 256),
                ("PX", 0.04, 256),
            ],
        )

    def safe_release(self) -> None:
        self._send_sequence(
            "Safe release",
            [
                ("ST", 0.04, 256),
                ("TC=0", 0.02, 256),
                ("MO=0", 0.04, 256),
                ("MO", 0.04, 256),
                ("EC", 0.04, 256),
            ],
        )

    def prepare_torque_mode(self) -> None:
        self._send_sequence(
            "Prepare torque mode",
            [
                ("ST", 0.04, 256),
                ("TC=0", 0.02, 256),
                ("MO=0", 0.04, 256),
                ("UM=5", 0.05, 256),
                ("RM=1", 0.05, 256),
                ("MO=1", 0.05, 256),
                ("MO", 0.04, 256),
                ("UM", 0.04, 256),
                ("RM", 0.04, 256),
            ],
        )

    def motor_on(self) -> None:
        self._send_sequence("Motor on", [("MO=1", 0.05, 256), ("MO", 0.04, 256)])

    def motor_off(self) -> None:
        self._send_sequence("Motor off", [("MO=0", 0.05, 256), ("MO", 0.04, 256)])

    def send_raw_command(self, _event=None) -> None:
        raw = self.cmd_var.get().strip()
        if not raw:
            self.q.put("[GUI] Empty command ignored\n")
            return

        self._send_sequence("Raw command", [(raw, 0.05, 256)])

    def connection_worker(self) -> None:
        while not self.stop_evt.is_set():
            ports = self._candidate_ports()
            if not ports:
                self.q.put("[INFO] No matching serial ports found; waiting...\n")
                time.sleep(RETRY_SECONDS)
                continue

            connected = False
            for port in ports:
                if self.stop_evt.is_set():
                    return
                try:
                    ser = serial.Serial(port, BAUD, timeout=0.2)
                    with self.io_lock:
                        self.ser = ser
                        self.current_port = port
                    self.q.put(f"[INFO] Connected to {port} at {BAUD} bps\n")
                    self.q.put(f"[INFO] Auto-reconnect active. Waiting for logs on {port}...\n\n")
                    connected = True
                    break
                except Exception as exc:
                    self.q.put(f"[WARN] {port} unavailable: {exc}\n")

            if not connected:
                self.q.put(f"[INFO] Retry in {RETRY_SECONDS:.1f}s...\n")
                time.sleep(RETRY_SECONDS)
                continue

            while not self.stop_evt.is_set():
                try:
                    with self.io_lock:
                        ser = self.ser
                        port = self.current_port or "?"
                        if ser is None:
                            break
                        data = ser.read(1024)
                    if data:
                        text = data.decode(errors="replace")
                        for line in text.splitlines(True):
                            self.q.put(f"[{port}] {line}")
                except Exception as exc:
                    self.q.put(f"[WARN] Connection lost ({self.current_port}): {exc}\n")
                    self._close_serial()
                    self.q.put(f"[INFO] Reconnecting in {RETRY_SECONDS:.1f}s...\n")
                    time.sleep(RETRY_SECONDS)
                    break

    def send_pin_command(self, _event=None) -> None:
        raw = self.pin_var.get().strip()
        try:
            pin = int(raw)
        except ValueError:
            self.q.put(f"[GUI] Invalid pin '{raw}'. Use integer 0..80\n")
            return

        if pin < 0 or pin > 80:
            self.q.put(f"[GUI] Pin out of range: {pin}. Use 0..80\n")
            return

        payload = f"{pin}\n".encode("ascii")
        with self.io_lock:
            ser = self.ser
            port = self.current_port

        if ser is None or port is None:
            self.q.put("[GUI] No connected port to send command\n")
            return

        try:
            with self.io_lock:
                ser.write(payload)
                ser.flush()
            self.q.put(f"[GUI] Sent pin command {pin} to {port}\n")
        except Exception as exc:
            self.q.put(f"[GUI] Send failed on {port}: {exc}\n")
            self._close_serial()

    def drain_queue(self) -> None:
        had_data = False
        while True:
            try:
                msg = self.q.get_nowait()
            except queue.Empty:
                break
            had_data = True
            self.text.insert("end", msg)
            self.text.see("end")

        with self.io_lock:
            port = self.current_port

        if port:
            self.status.config(text=f"Connected: {port} @ {BAUD} (auto-reconnect ON)")
        elif had_data:
            self.status.config(text="Disconnected - scanning for device...")

        if not self.stop_evt.is_set():
            self.root.after(50, self.drain_queue)

    def on_close(self) -> None:
        self.stop_evt.set()
        self._close_serial()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    SerialMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
