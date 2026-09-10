#!/usr/bin/env python3
"""EEA Modbus RTU Testbench GUI.

Features:
- Configure serial port (port/baud/parity/stop)
- Select slave, FC (3/4), register start/count and poll interval
- Start/Stop polling; decoded registers shown in table; raw log pane
- Write single register (asks confirmation) — disabled until user confirms in dialog

Requires: Python with pyserial (installed in workspace venv). Run from workspace root:
  & c:\\CoRoot\\.venv\\Scripts\\python.exe scripts\\eea_testbench_gui.py
"""
from __future__ import annotations

import threading
import time
import struct
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
# matplotlib is used for live plotting; assume installed in venv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import serial
import serial.rs485
import serial.tools.list_ports
from queue import Queue, Empty
from datetime import datetime, timezone
import os


PARITY_MAP = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}
ENCODER_PLOT_INTERVAL_MS = 20

ENCODER_READ_MAP = {
    # Verified against inputRegistersModbus[] in main.c: reg 0 = encoderPosition for ALL slaves.
    # Slaves 1,2,3 all have encoders (only PALM_BOARD_NODE_ID=4 skips enableEncoder).
    # encoderPosition: bit15=EncOk&!vibrating, bits[14:0]=15-bit filtered absolute position.
    'S3EncoderValue': {'slave': 1, 'fc': 4, 'reg': 0, 'count': 1},
    'S2EncoderValue': {'slave': 2, 'fc': 4, 'reg': 0, 'count': 1},
    'S1EncoderValue': {'slave': 3, 'fc': 4, 'reg': 0, 'count': 1},  # was reg:4 = lsbFrameSQN (wrong!)
}

# Source: main.h — LED_BOARD_NODE_ID=3 (S1), PALM_BOARD_NODE_ID=4 (S4)
# Holding registers for LED (0-indexed, from holdingRegistersModbus[] in main.c):
#   reg 7 = ledRedGreen         = (red<<8) | green
#   reg 8 = ledBlueBrightnessBlinkrate = (blue<<8) | (brightness_nibble<<4) | blink_nibble
#   reg 9 = terminatorHeartbeat = (terminator<<8) | heartbeat
# IMPORTANT: heartbeat low byte (reg9[7:0]) must change every <500ms or
# firmware heartbeatCheck() overrides LED to purple (0xFF00 / 0xFF50).
LED_SLAVE = 3          # LED_BOARD_NODE_ID from main.h
LED_REG_RG   = 7       # ledRedGreen
LED_REG_BBR  = 8       # ledBlueBrightnessBlinkrate
LED_REG_TERM = 9       # terminatorHeartbeat

# Brightness nibble → raw value passed to APA102 driver (source: main.c switch)
# bits [7:4] of ledBlueBrightnessBlinkrate low byte
BRIGHTNESS_CODE_TO_RAW = {0:0, 1:32, 2:64, 3:96, 4:128, 5:160, 6:192, 7:224, 8:255}
# Blink nibble → half-period ms (source: main.c switch)
# bits [3:0] of ledBlueBrightnessBlinkrate low byte; 0 = solid
BLINK_CODE_TO_HALF_MS = {0:0, 1:25, 2:50, 3:75, 4:100, 5:125, 6:250, 7:375, 8:500, 9:750, 10:1000}

CONVERTER_OUT_BASE_DEFAULT = 6
# Actual firmware holding register count from source (holdingRegistersModbus[10])
CONVERTER_OUT_REG_COUNT = 10

CONVERTER_READ_PROFILES = [
    {"name": "Addr1 FC4 R0 C8", "slave": 1, "fc": 4, "reg": 0, "count": 8},
    {"name": "Addr2 FC4 R0 C8", "slave": 2, "fc": 4, "reg": 0, "count": 8},
    {"name": "Addr3 FC4 R0 C10", "slave": 3, "fc": 4, "reg": 0, "count": 10},
    {"name": "Addr4 FC4 R3 C7", "slave": 4, "fc": 4, "reg": 3, "count": 7},
]

STATION_WRITE_WORDS = {
    1: 1,
    2: 1,
    3: 4,
    4: 4,
}

STATION_READ_PROFILE_BY_SLAVE = {
    p['slave']: p for p in CONVERTER_READ_PROFILES
}

STATION_LABELS = {
    1: 'S3',
    2: 'S2',
    3: 'S1',
    4: 'S4',
}

# Exact register dictionaries from GENU EEA firmware source
# (platform/GENU/firmware/eea/Core/Src/main.c).
SOURCE_HOLDING_FIELDS = [
    'InterfaceCommand',
    'EncoderOffset',
    'EdFpnFprFbn',
    'EncoderLockingPosition',
    'MsbCalibrationTimestamp',
    'LsbCalibrationTimestamp',
    'LatencySQN',
    'LedRedGreen',
    'LedBlueBrightnessBlinkrate',
    'TerminatorHeartbeat',
]

SOURCE_INPUT_FIELDS = [
    'EncoderValue',
    'MsbEncoderSQN',
    'LsbEncoderSQN',
    'MsbFrameSQN',
    'LsbFrameSQN',
    'LatencySQN',
    'EdFpnFprFbn',
    'EncoderLockingPosition',
    'LedRedGreen',
    'LedBlueBrightnessBlinkrate',
]

# Source-verified (main.c switch statements):
# Full blink period = 2 * half_period. 0 = solid (no blink).
BLINK_FULL_MS_TO_CODE = {
    0: 0x0,    # solid
    50: 0x1,   # 25ms half
    100: 0x2,  # 50ms half
    150: 0x3,  # 75ms half
    200: 0x4,  # 100ms half
    250: 0x5,  # 125ms half
    500: 0x6,  # 250ms half
    750: 0x7,  # 375ms half
    1000: 0x8, # 500ms half
    1500: 0x9, # 750ms half
    2000: 0xA, # 1000ms half
}

# Brightness nibble labels → code (source: main.c switch, code→raw: 0→0, 1→32, ..., 8→255)
BRIGHTNESS_NAME_TO_CODE = {
    'Off':      0x0,
    '1/8':      0x1,
    '2/8':      0x2,
    '3/8':      0x3,
    '4/8':      0x4,
    '5/8':      0x5,
    '6/8':      0x6,
    '7/8':      0x7,
    'Full':     0x8,
}


def crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, "little")


def make_frame(slave: int, fc: int, reg: int, count: int) -> bytes:
    p = struct.pack(
        ">B B H H",
        slave,
        fc,
        reg,
        count,
    )
    return p + crc16(p)


def parse_regs_from_reply(rx: bytes) -> list[int] | None:
    if not rx or len(rx) < 5:
        return None
    # assume standard Modbus: addr, fc, bytecount, data..., crc_lo, crc_hi
    try:
        bytecount = rx[2]
        data = rx[3 : 3 + bytecount]
        regs = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                regs.append((data[i] << 8) | data[i + 1])
        return regs
    except Exception:
        return None


def decode_general_info_word(word: int) -> dict[str, int]:
    """Decode packed FW info nibble fields: FPN/FPR/FBN/ED."""
    return {
        'FPN': (word >> 12) & 0x0F,
        'FPR': (word >> 8) & 0x0F,
        'FBN': (word >> 4) & 0x0F,
        'ED': word & 0x0F,
    }


def decode_led_red_green(word: int) -> dict[str, int]:
    return {
        'Red': (word >> 8) & 0xFF,
        'Green': word & 0xFF,
    }


def decode_led_blue_bt_br(word: int) -> dict[str, int]:
    low = word & 0xFF
    return {
        'Blue': (word >> 8) & 0xFF,
        'BT': (low >> 4) & 0x0F,
        'BR': low & 0x0F,
    }


def decode_term_hb(word: int) -> dict[str, int]:
    return {
        'Terminator': (word >> 8) & 0xFF,
        'Heartbeat': word & 0xFF,
    }


def decode_encoder_word(word: int) -> dict[str, int | bool]:
    return {
        'valid': bool(word & 0x8000),
        'position': word & 0x7FFF,
    }


def _expected_modbus_reply_length(fc: int, count: int | None = None) -> int:
    if fc == 6:
        return 8
    if fc == 16:
        return 8
    if fc in (3, 4) and count is not None:
        return 5 + (2 * count)
    return 5


def _open_ser(port_cfg: dict) -> serial.Serial:
    """Open serial with settings from port_cfg dict. Raises on failure."""
    ser = serial.Serial(
        port=port_cfg['port'],
        baudrate=int(port_cfg['baud']),
        parity=PARITY_MAP.get(port_cfg['parity'], serial.PARITY_EVEN),
        stopbits=serial.STOPBITS_ONE if int(port_cfg['stop']) == 1 else serial.STOPBITS_TWO,
        bytesize=serial.EIGHTBITS,
        timeout=0,
    )
    try:
        ser.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=True, rts_level_for_rx=False,
            delay_before_tx=None, delay_before_rx=None,
        )
    except Exception:
        pass
    return ser


def _transact(ser: serial.Serial, frame: bytes, read_len: int = 512, expected_len: int | None = None, timeout_s: float = 0.02) -> bytes:
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(frame)
    ser.flush()
    deadline = time.monotonic() + timeout_s
    rx = bytearray()
    while time.monotonic() < deadline:
        waiting = ser.in_waiting
        if waiting:
            rx.extend(ser.read(min(read_len - len(rx), waiting)))
            if len(rx) >= 5:
                if rx[1] & 0x80:
                    if len(rx) >= 5:
                        break
                elif expected_len is not None and len(rx) >= expected_len:
                    break
                elif expected_len is None and len(rx) >= read_len:
                    break
        else:
            time.sleep(0.0005)
    return bytes(rx)


class SerialWorker(threading.Thread):
    """Single owner of the serial port.

    All Modbus transactions go through this thread, eliminating the
    'access denied' / multi-open conflicts that happened when the Poller,
    the heartbeat thread, and button handlers each tried to open COM18.

    Command queue items are dicts with at minimum {'type': ...}.
    Results are posted to out_q as ('cmd_result', {tag, ...}).

    Supported command types:
      write_fc6  : {slave, reg, val, tag}
      read_regs  : {slave, fc, reg, count, tag}
      batch      : {cmds: [list of write_fc6/read_regs dicts], tag}
    """

    def __init__(self, port_cfg: dict, poll_cfg: dict, out_q: Queue, cmd_q: Queue):
        super().__init__(daemon=True)
        self.port_cfg = port_cfg
        self.poll_cfg = poll_cfg   # live dict; worker reads it each cycle
        self.out_q = out_q
        self.cmd_q = cmd_q
        self._stop = threading.Event()
        # Lock guards the shared serial connection so button handlers can
        # borrow it between poll cycles without opening a second connection.
        self._lock = threading.Lock()
        self.ser: serial.Serial | None = None

    def stop(self):
        self._stop.set()

    def _do_write_fc6(self, ser, slave: int, reg: int, val: int) -> tuple[bytes, bytes]:
        with self._lock:
            p = struct.pack('>BBHH', slave, 6, reg, val & 0xFFFF)
            frame = p + crc16(p)
            rx = _transact(ser, frame, 256, expected_len=_expected_modbus_reply_length(6), timeout_s=0.02)
        return frame, rx

    def _do_read_regs(self, ser, slave: int, fc: int, reg: int, count: int) -> tuple[bytes, bytes, list | None]:
        with self._lock:
            frame = make_frame(slave, fc, reg, count)
            rx = _transact(ser, frame, 512, expected_len=_expected_modbus_reply_length(fc, count), timeout_s=0.02)
        ok = bool(rx and len(rx) >= 5 and crc16(rx[:-2]) == rx[-2:])
        regs = parse_regs_from_reply(rx) if ok else None
        return frame, rx, regs

    def run(self):
        try:
            ser = _open_ser(self.port_cfg)
            self.ser = ser
        except Exception as e:
            self.out_q.put(('error', f'Serial open error: {e}'))
            return

        next_poll = time.monotonic()
        logdir = 'notes/gateway_reverse_engineering'
        os.makedirs(logdir, exist_ok=True)
        csvpath = os.path.join(logdir, 'eea_testbench_log.csv')

        with open(csvpath, 'a', encoding='utf-8') as lf:
            lf.write(
                f"# run {datetime.now(timezone.utc).isoformat()} "
                f"port={self.port_cfg['port']} baud={self.port_cfg['baud']} "
                f"parity={self.port_cfg['parity']}\n"
            )

            while not self._stop.is_set():
                now = time.monotonic()

                # Service commands promptly instead of waiting for the next poll boundary.
                wait_s = max(0.0, next_poll - now)
                wait_s = min(wait_s, 0.02)
                try:
                    pending = [self.cmd_q.get(timeout=wait_s)]
                    while True:
                        pending.append(self.cmd_q.get_nowait())
                except Empty:
                    pending = []

                for cmd in pending:
                    ctype = cmd.get('type')
                    tag = cmd.get('tag', '')
                    try:
                        if ctype == 'write_fc6':
                            tx, rx = self._do_write_fc6(ser, cmd['slave'], cmd['reg'], cmd['val'])
                            self.out_q.put(('cmd_result', {
                                'tag': tag, 'tx': tx.hex(),
                                'rx': rx.hex() if rx else '', 'ok': True,
                            }))

                        elif ctype == 'read_regs':
                            tx, rx, regs = self._do_read_regs(ser, cmd['slave'], cmd['fc'], cmd['reg'], cmd['count'])
                            self.out_q.put(('cmd_result', {
                                'tag': tag, 'slave': cmd['slave'], 'fc': cmd['fc'],
                                'reg': cmd['reg'], 'count': cmd['count'],
                                'tx': tx.hex(), 'rx': rx.hex() if rx else '',
                                'ok': regs is not None, 'regs': regs,
                            }))

                        elif ctype == 'batch':
                            results = []
                            for sub in cmd.get('cmds', []):
                                st = sub.get('type')
                                if st == 'write_fc6':
                                    tx, rx = self._do_write_fc6(ser, sub['slave'], sub['reg'], sub['val'])
                                    results.append({'type': 'write_fc6', 'tx': tx.hex(), 'rx': rx.hex() if rx else ''})
                                elif st == 'read_regs':
                                    tx, rx, regs = self._do_read_regs(ser, sub['slave'], sub['fc'], sub['reg'], sub['count'])
                                    results.append({'type': 'read_regs', 'slave': sub['slave'], 'fc': sub['fc'],
                                                    'reg': sub['reg'], 'count': sub['count'],
                                                    'tx': tx.hex(), 'rx': rx.hex() if rx else '',
                                                    'ok': regs is not None, 'regs': regs})
                            self.out_q.put(('cmd_result', {'tag': tag, 'results': results}))

                    except Exception as e:
                        self.out_q.put(('cmd_result', {'tag': tag, 'error': str(e)}))

                # Regular poll — _do_read_regs acquires self._lock internally
                if now >= next_poll:
                    slave = int(self.poll_cfg.get('slave', 1))
                    fc = int(self.poll_cfg.get('fc', 4))
                    reg = int(self.poll_cfg.get('reg', 0))
                    count = int(self.poll_cfg.get('count', 1))
                    interval = float(self.poll_cfg.get('interval', 0.5))

                    t = datetime.now(timezone.utc).isoformat()
                    try:
                        tx, rx, regs = self._do_read_regs(ser, slave, fc, reg, count)
                    except Exception as e:
                        self.out_q.put(('error', f'Serial IO error: {e}'))
                        break

                    self.out_q.put(('sample', {
                        'time': t, 'slave': slave, 'fc': fc, 'reg': reg,
                        'count': count, 'raw': rx.hex() if rx else '', 'regs': regs,
                    }))
                    lf.write(f"{t},{slave},{fc},{reg},{rx.hex() if rx else ''}\n")
                    lf.flush()
                    next_poll = time.monotonic() + interval
                else:
                    continue

        try:
            ser.close()
        except Exception:
            pass
        self.ser = None
        self.out_q.put(('stopped', 'worker stopped'))


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("EEA Modbus Testbench")
        self.out_q = Queue()
        self.cmd_q: Queue = Queue()
        # Live poll config dict; SerialWorker reads these every cycle.
        self.poll_cfg: dict = {'slave': '1', 'fc': '4', 'reg': '0', 'count': '1', 'interval': '0.2'}
        self.worker: SerialWorker | None = None
        # cmd_result callbacks: tag -> callable(result_dict)
        self._cmd_callbacks: dict = {}
        self._cmd_id = 0
        # Heartbeat state
        self._hb_counter: int = 1
        self._hb_after_id = None
        self._hb_active: bool = False
        self._hb_rg: int = 0
        self._hb_bbr: int = 0
        self._hb_term: int = 0
        self._enc_plot_after_id = None
        self._enc_plot_pending = False
        self._enc_plot_index = 0
        self._last_plot_draw = 0.0

        frm = ttk.Frame(root, padding=8)
        frm.pack(fill='both', expand=True)

        # top config
        cfgf = ttk.Labelframe(frm, text="Serial / Poll")
        cfgf.pack(fill='x')
        ttk.Label(cfgf, text="Port").grid(row=0, column=0)
        self.port_var = tk.StringVar(value='COM18')
        self.port_combo = ttk.Combobox(cfgf, width=10, textvariable=self.port_var)
        self.port_combo.grid(row=0, column=1)
        ttk.Label(cfgf, text="Baud").grid(row=0, column=2)
        self.baud_var = tk.StringVar(value='115200')
        ttk.Entry(cfgf, textvariable=self.baud_var, width=8).grid(row=0, column=3)
        ttk.Label(cfgf, text="Parity").grid(row=0, column=4)
        self.par_var = tk.StringVar(value='E')
        ttk.Combobox(cfgf, values=['N','E','O'], width=3, textvariable=self.par_var).grid(row=0, column=5)
        ttk.Label(cfgf, text="Stop").grid(row=0, column=6)
        self.stop_var = tk.StringVar(value='1')
        ttk.Combobox(cfgf, values=['1','2'], width=2, textvariable=self.stop_var).grid(row=0, column=7)

        ttk.Label(cfgf, text="Slave").grid(row=1, column=0)
        self.slave_var = tk.StringVar(value='1')
        ttk.Entry(cfgf, textvariable=self.slave_var, width=4).grid(row=1, column=1)
        ttk.Label(cfgf, text="FC").grid(row=1, column=2)
        self.fc_var = tk.StringVar(value='4')
        ttk.Combobox(cfgf, values=['3','4'], width=2, textvariable=self.fc_var).grid(row=1, column=3)
        ttk.Label(cfgf, text="Reg").grid(row=1, column=4)
        self.reg_var = tk.StringVar(value='0')
        ttk.Entry(cfgf, textvariable=self.reg_var, width=6).grid(row=1, column=5)
        ttk.Label(cfgf, text="Count").grid(row=1, column=6)
        self.count_var = tk.StringVar(value='4')
        ttk.Entry(cfgf, textvariable=self.count_var, width=4).grid(row=1, column=7)
        ttk.Label(cfgf, text="Interval(s)").grid(row=1, column=8)
        self.int_var = tk.StringVar(value='0.2')
        ttk.Entry(cfgf, textvariable=self.int_var, width=6).grid(row=1, column=9)

        self.start_btn = ttk.Button(cfgf, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=10, rowspan=2, padx=6)
        self.stop_btn = ttk.Button(cfgf, text="Stop", command=self.stop, state='disabled')
        self.stop_btn.grid(row=0, column=11, rowspan=2)
        self.scan_btn = ttk.Button(cfgf, text='Scan Ports', command=self.scan_ports)
        self.scan_btn.grid(row=2, column=0, columnspan=2, pady=2)
        self.autodetect_btn = ttk.Button(cfgf, text='Auto Detect Link', command=self.auto_detect_link)
        self.autodetect_btn.grid(row=2, column=2, columnspan=3, pady=2)
        self.identity_btn = ttk.Button(cfgf, text='Read Identity', command=self.read_identity_summary)
        self.identity_btn.grid(row=2, column=5, columnspan=3, pady=2)
        self.link_status_var = tk.StringVar(value='Link: not checked')
        ttk.Label(cfgf, textvariable=self.link_status_var).grid(row=2, column=8, columnspan=4, sticky='w')

        # middle: treeview for decoded registers
        tvf = ttk.Labelframe(frm, text="Decoded registers")
        tvf.pack(fill='x', expand=False)
        self.tree = ttk.Treeview(tvf, columns=('idx','value'), show='headings', height=4)
        self.tree.heading('idx', text='Index')
        self.tree.heading('value', text='Value (uint16)')
        self.tree.pack(fill='x', expand=False)

        snapf = ttk.Labelframe(frm, text='Full Source Field Snapshot (GENU EEA)')
        snapf.pack(fill='both', expand=True)
        self.snapshot_tree = ttk.Treeview(
            snapf,
            columns=('station', 'group', 'field', 'value', 'decoded'),
            show='headings',
            height=10,
        )
        self.snapshot_tree.heading('station', text='Station')
        self.snapshot_tree.heading('group', text='Group')
        self.snapshot_tree.heading('field', text='Field')
        self.snapshot_tree.heading('value', text='Value')
        self.snapshot_tree.heading('decoded', text='Decoded')
        self.snapshot_tree.column('station', width=70, anchor='w')
        self.snapshot_tree.column('group', width=80, anchor='w')
        self.snapshot_tree.column('field', width=220, anchor='w')
        self.snapshot_tree.column('value', width=100, anchor='w')
        self.snapshot_tree.column('decoded', width=360, anchor='w')
        self.snapshot_tree.pack(fill='both', expand=True)

        # bottom: raw log and write controls
        botf = ttk.Frame(frm)
        botf.pack(fill='x')
        logf = ttk.Labelframe(botf, text='Raw log')
        logf.pack(side='left', fill='both', expand=True)
        self.log = scrolledtext.ScrolledText(logf, height=12)
        self.log.pack(fill='both', expand=True)

        writef = ttk.Labelframe(botf, text='Write (single register)')
        writef.pack(side='right', fill='y')
        ttk.Label(writef, text='Reg').grid(row=0, column=0)
        self.wreg = tk.StringVar(value='0')
        ttk.Entry(writef, textvariable=self.wreg, width=6).grid(row=0, column=1)
        ttk.Label(writef, text='Value').grid(row=1, column=0)
        self.wval = tk.StringVar(value='0')
        ttk.Entry(writef, textvariable=self.wval, width=6).grid(row=1, column=1)
        self.write_btn = ttk.Button(writef, text='Write', command=self.write_register)
        self.write_btn.grid(row=2, column=0, columnspan=2, pady=6)

        # LED controls — source: main.c, LED_BOARD_NODE_ID=3 (S1)
        # Registers: 7=ledRedGreen, 8=ledBlueBrightnessBlinkrate, 9=terminatorHeartbeat
        # Heartbeat (reg9 low byte) MUST cycle every <500ms or firmware forces red.
        ledf = ttk.Labelframe(botf, text='LED Control  (slave 3 = S1)')
        ledf.pack(side='right', fill='y', padx=6)
        ttk.Label(ledf, text='Slave 3 (S1) only — regs 7/8/9', foreground='gray').grid(row=0, column=0, columnspan=2, sticky='w')
        ttk.Label(ledf, text='Red (0-255)').grid(row=1, column=0)
        self.r_var = tk.StringVar(value='0')
        ttk.Entry(ledf, textvariable=self.r_var, width=10).grid(row=1, column=1)
        ttk.Label(ledf, text='Green (0-255)').grid(row=2, column=0)
        self.g_var = tk.StringVar(value='0')
        ttk.Entry(ledf, textvariable=self.g_var, width=10).grid(row=2, column=1)
        ttk.Label(ledf, text='Blue (0-255)').grid(row=3, column=0)
        self.b_var = tk.StringVar(value='0')
        ttk.Entry(ledf, textvariable=self.b_var, width=10).grid(row=3, column=1)

        ttk.Label(ledf, text='Blink period ms').grid(row=4, column=0)
        self.br_ms_var = tk.StringVar(value='0')
        ttk.Combobox(
            ledf,
            values=[str(v) for v in sorted(BLINK_FULL_MS_TO_CODE.keys())],
            width=8,
            textvariable=self.br_ms_var,
        ).grid(row=4, column=1)

        ttk.Label(ledf, text='Brightness').grid(row=5, column=0)
        self.bt_name_var = tk.StringVar(value='Full')
        ttk.Combobox(
            ledf,
            values=list(BRIGHTNESS_NAME_TO_CODE.keys()),
            width=8,
            textvariable=self.bt_name_var,
        ).grid(row=5, column=1)

        ttk.Label(ledf, text='Terminator byte').grid(row=6, column=0)
        self.term_var = tk.StringVar(value='0')
        ttk.Entry(ledf, textvariable=self.term_var, width=10).grid(row=6, column=1)
        ttk.Label(ledf, text='0 keeps current terminator', foreground='gray').grid(row=7, column=0, columnspan=2, sticky='w')

        self.hb_cycle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ledf, text='Auto-cycle heartbeat', variable=self.hb_cycle_var).grid(row=8, column=0, columnspan=2, sticky='w')
        self.hb_status_var = tk.StringVar(value='HB: stopped')
        ttk.Label(ledf, textvariable=self.hb_status_var, foreground='gray').grid(row=9, column=0, columnspan=2, sticky='w')

        ttk.Button(ledf, text='Set LED (slave 3, regs 7-9)', command=self.write_leds).grid(row=10, column=0, columnspan=2, pady=4)
        ttk.Button(ledf, text='Stop Heartbeat', command=self.stop_heartbeat_cycle).grid(row=11, column=0, columnspan=2, pady=2)

        presetf = ttk.Frame(ledf)
        presetf.grid(row=12, column=0, columnspan=2, pady=4)
        ttk.Button(presetf, text='Red',    command=lambda: self.apply_led_preset(255, 0, 0,   'Full', 0)).grid(row=0, column=0, padx=1, pady=1)
        ttk.Button(presetf, text='Green',  command=lambda: self.apply_led_preset(0, 255, 0,   'Full', 0)).grid(row=0, column=1, padx=1, pady=1)
        ttk.Button(presetf, text='Blue',   command=lambda: self.apply_led_preset(0, 0, 255,   'Full', 0)).grid(row=1, column=0, padx=1, pady=1)
        ttk.Button(presetf, text='White',  command=lambda: self.apply_led_preset(255, 255, 255,'Full', 0)).grid(row=1, column=1, padx=1, pady=1)
        ttk.Button(presetf, text='Purple', command=lambda: self.apply_led_preset(255, 0, 255, 'Full', 0)).grid(row=2, column=0, padx=1, pady=1)
        ttk.Button(presetf, text='Off',    command=lambda: self.apply_led_preset(0, 0, 0,     'Off',  0)).grid(row=2, column=1, padx=1, pady=1)

        encf = ttk.Labelframe(botf, text='Encoders (All 3)')
        encf.pack(side='right', fill='y', padx=6)
        self.enc_s3_var = tk.StringVar(value='S3: -')
        self.enc_s2_var = tk.StringVar(value='S2: -')
        self.enc_s1_var = tk.StringVar(value='S1: -')
        ttk.Label(encf, textvariable=self.enc_s3_var).pack(anchor='w')
        ttk.Label(encf, textvariable=self.enc_s2_var).pack(anchor='w')
        ttk.Label(encf, textvariable=self.enc_s1_var).pack(anchor='w')
        enc_cfg = ttk.Frame(encf)
        enc_cfg.pack(fill='x', pady=2)
        ttk.Label(enc_cfg, text='Auto ms').grid(row=0, column=0, sticky='w')
        self.enc_auto_ms_var = tk.StringVar(value='20')
        ttk.Entry(enc_cfg, textvariable=self.enc_auto_ms_var, width=6).grid(row=0, column=1, sticky='w', padx=2)
        self.enc_auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(enc_cfg, text='Auto', variable=self.enc_auto_var, command=self.toggle_encoder_auto).grid(row=0, column=2, sticky='w', padx=2)
        ttk.Button(encf, text='Read 3 Encoders', command=self.read_all_encoders).pack(fill='x', pady=4)

        # Converter station controls using source-backed per-slave windows.
        convf = ttk.Labelframe(botf, text='Converter Station Windows')
        convf.pack(side='right', fill='y', padx=6)

        ttk.Label(convf, text='Out Base Reg').grid(row=0, column=0, sticky='e')
        self.conv_base_var = tk.StringVar(value=str(CONVERTER_OUT_BASE_DEFAULT))
        ttk.Entry(convf, textvariable=self.conv_base_var, width=6).grid(row=0, column=1, sticky='w')
        ttk.Label(convf, text='Out Slave').grid(row=0, column=2, sticky='e')
        self.conv_slave_var = tk.StringVar(value='1')
        ttk.Entry(convf, textvariable=self.conv_slave_var, width=4).grid(row=0, column=3, sticky='w')

        ttk.Label(convf, text='W0 (reg+0)').grid(row=1, column=0, sticky='e')
        self.conv_w0_var = tk.StringVar(value='0')
        ttk.Entry(convf, textvariable=self.conv_w0_var, width=8).grid(row=1, column=1, sticky='w')
        ttk.Label(convf, text='W1 (reg+1)').grid(row=1, column=2, sticky='e')
        self.conv_w1_var = tk.StringVar(value='0')
        ttk.Entry(convf, textvariable=self.conv_w1_var, width=8).grid(row=1, column=3, sticky='w')

        ttk.Label(convf, text='W2 (reg+2)').grid(row=2, column=0, sticky='e')
        self.conv_w2_var = tk.StringVar(value='0')
        ttk.Entry(convf, textvariable=self.conv_w2_var, width=8).grid(row=2, column=1, sticky='w')
        ttk.Label(convf, text='W3 (reg+3)').grid(row=2, column=2, sticky='e')
        self.conv_w3_var = tk.StringVar(value='0')
        ttk.Entry(convf, textvariable=self.conv_w3_var, width=8).grid(row=2, column=3, sticky='w')

        self.conv_status_var = tk.StringVar(value='Slave1/2 write 1 word; Slave3/4 write 4 words')
        ttk.Label(convf, textvariable=self.conv_status_var).grid(row=3, column=0, columnspan=4, sticky='w')

        ttk.Button(convf, text='Read Station Window', command=self.read_station_window).grid(row=4, column=0, columnspan=2, pady=4)
        ttk.Button(convf, text='Write Station Window', command=self.write_station_window).grid(row=4, column=2, columnspan=2, pady=4)
        ttk.Button(convf, text='Poll Profiles', command=self.read_converter_profiles).grid(row=5, column=0, columnspan=4, pady=4)
        ttk.Button(convf, text='Read Full Snapshot', command=self.read_full_field_snapshot).grid(row=6, column=0, columnspan=4, pady=4)

        self.root.after(20, self.process_queue)
        self.scan_ports(select_first=True)
        # plotting setup
        self.plot_fig = Figure(figsize=(5, 2.5), dpi=100)
        self.plot_ax = self.plot_fig.add_subplot(111)
        self.plot_canvas = FigureCanvasTkAgg(self.plot_fig, master=frm)
        self.plot_canvas.get_tk_widget().pack(fill='both', expand=True)
        self.plot_time: list[int] = []
        self.plot_series = {'S3': [], 'S2': [], 'S1': []}
        self.max_points = 120
        self.update_plot()

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        port_cfg = {
            'port': self.port_var.get(), 'baud': self.baud_var.get(),
            'parity': self.par_var.get(), 'stop': self.stop_var.get(),
        }
        self.poll_cfg.update({
            'slave': self.slave_var.get(), 'fc': self.fc_var.get(),
            'reg': self.reg_var.get(), 'count': self.count_var.get(),
            'interval': self.int_var.get(),
        })
        # Drain stale queue entries
        while not self.cmd_q.empty():
            try:
                self.cmd_q.get_nowait()
            except Empty:
                break
        self.worker = SerialWorker(port_cfg, self.poll_cfg, self.out_q, self.cmd_q)
        self.worker.start()
        if self.enc_auto_var.get():
            self._start_encoder_plot_loop()
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.log_insert(f"Started worker on {port_cfg['port']}\n")

    def stop(self):
        self._stop_heartbeat_cycle()
        if self.enc_auto_var.get():
            self._stop_encoder_plot_loop()
        if self.worker:
            self.worker.stop()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def _list_serial_ports(self) -> list[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def scan_ports(self, select_first: bool = False):
        ports = self._list_serial_ports()
        self.port_combo['values'] = ports
        if ports:
            preferred = self.port_var.get().strip()
            if preferred not in ports:
                if 'COM18' in ports:
                    self.port_var.set('COM18')
                elif 'COM12' in ports:
                    self.port_var.set('COM12')
                elif select_first:
                    self.port_var.set(ports[0])
            self.log_insert(f"PORT SCAN found={ports}\n")
        else:
            self.log_insert("PORT SCAN found no serial ports\n")

    def _probe_once(self, port: str, baud: int, parity: str, stop_bits: int, slave: int, fc: int, reg: int, count: int) -> tuple[bool, str]:
        ser = serial.Serial()
        ser.port = port
        ser.baudrate = baud
        ser.parity = PARITY_MAP.get(parity, serial.PARITY_EVEN)
        ser.stopbits = serial.STOPBITS_ONE if stop_bits == 1 else serial.STOPBITS_TWO
        ser.bytesize = serial.EIGHTBITS
        ser.timeout = 0.25
        try:
            ser.rs485_mode = serial.rs485.RS485Settings(
                rts_level_for_tx=True,
                rts_level_for_rx=False,
                delay_before_tx=None,
                delay_before_rx=None,
            )
        except Exception:
            pass
        try:
            ser.open()
            tx, rx, regs = self._read_regs(ser, slave, fc, reg, count)
            ok = bool(rx and len(rx) >= 5 and crc16(rx[:-2]) == rx[-2:] and rx[0] == slave)
            detail = f"TX={tx.hex()} RX={rx.hex()} REGS={regs if regs else []}"
            return ok, detail
        except Exception as e:
            return False, str(e)
        finally:
            self._close_serial(ser)

    def auto_detect_link(self):
        self.scan_ports(select_first=True)
        ports = self._list_serial_ports()
        if not ports:
            messagebox.showerror('Auto detect', 'No serial ports available')
            return

        bauds = [115200, 19200, 9600]
        parities = ['E', 'N', 'O']
        probes = [
            {'slave': 1, 'fc': 4, 'reg': 0, 'count': 1},
            {'slave': 2, 'fc': 4, 'reg': 0, 'count': 1},
            {'slave': 3, 'fc': 4, 'reg': 0, 'count': 1},
        ]

        for port in ports:
            for baud in bauds:
                for parity in parities:
                    for p in probes:
                        ok, detail = self._probe_once(port, baud, parity, 1, p['slave'], p['fc'], p['reg'], p['count'])
                        self.log_insert(
                            f"AUTO PROBE port={port} baud={baud} parity={parity} slave={p['slave']} fc={p['fc']} reg={p['reg']} -> {'OK' if ok else 'NO'} {detail}\n"
                        )
                        if ok:
                            self.port_var.set(port)
                            self.baud_var.set(str(baud))
                            self.par_var.set(parity)
                            self.stop_var.set('1')
                            self.slave_var.set(str(p['slave']))
                            self.fc_var.set(str(p['fc']))
                            self.reg_var.set(str(p['reg']))
                            self.count_var.set(str(p['count']))
                            self.link_status_var.set(f"Link: {port} {baud}-{parity}-1 slave{p['slave']}")
                            messagebox.showinfo('Auto detect', f"Detected EEA link on {port} @ {baud}-{parity}-1 (slave {p['slave']})")
                            return

        self.link_status_var.set('Link: no valid Modbus reply found')
        messagebox.showwarning('Auto detect', 'No valid EEA Modbus replies found on scanned ports/settings')

    def read_identity_summary(self):
        # Identity/readback summary for the GENU EEA branch; this reads EEA station windows only.
        specs = [
            {'slave': 1, 'fc': 4, 'reg': 6, 'count': 1, 'label': 'S3GeneralInfo'},
            {'slave': 2, 'fc': 4, 'reg': 6, 'count': 1, 'label': 'S2GeneralInfo'},
            {'slave': 3, 'fc': 4, 'reg': 6, 'count': 1, 'label': 'S1GeneralInfo'},  # reg6=edFpnFprFbn (was reg1=msbEncoderSQN)
        ]
        try:
            ser = self._open_serial()
            lines = []
            close_needed = True
            for s in specs:
                tx, rx, regs = self._read_regs(ser, s['slave'], s['fc'], s['reg'], s['count'])
                if regs:
                    raw = regs[0] & 0xFFFF
                    dec = decode_general_info_word(raw)
                    station = STATION_LABELS.get(s['slave'], f"S{s['slave']}")
                    line = (
                        f"{station} {s['label']}=0x{raw:04X} "
                        f"(FPN={dec['FPN']} FPR={dec['FPR']} FBN={dec['FBN']} ED={dec['ED']})"
                    )
                else:
                    line = f"{s['label']} no-data"
                lines.append(line)
                self.log_insert(
                    f"IDENTITY READ slave={s['slave']} fc={s['fc']} reg={s['reg']} TX={tx.hex()} RX={rx.hex()}\n"
                )

            enc_vals = {}
            for name, spec in ENCODER_READ_MAP.items():
                _, rx, regs = self._read_regs(ser, spec['slave'], spec['fc'], spec['reg'], spec['count'])
                enc_vals[name] = regs[0] if regs else None
                self.log_insert(
                    f"IDENTITY ENC {name} slave={spec['slave']} reg={spec['reg']} RX={rx.hex()}\n"
                )
            self._close_serial(ser)

            lines.append(f"S3EncoderValue={enc_vals.get('S3EncoderValue')}")
            lines.append(f"S2EncoderValue={enc_vals.get('S2EncoderValue')}")
            lines.append(f"S1EncoderValue={enc_vals.get('S1EncoderValue')}")
            lines.append('Laterality note: left/right is not exposed as a confirmed Modbus identity field in current map.')
            messagebox.showinfo('EEA Identity Summary', '\n'.join(lines))
        except Exception as e:
            messagebox.showerror('Read identity error', str(e))

    def process_queue(self):
        try:
            while True:
                typ, data = self.out_q.get_nowait()
                if typ == 'error':
                    self.log_insert(f"ERROR: {data}\n")
                elif typ == 'sample':
                    self.on_sample(data)
                elif typ == 'stopped':
                    self.log_insert(f"{data}\n")
                elif typ == 'cmd_result':
                    tag = data.get('tag', '')
                    cb = self._cmd_callbacks.pop(tag, None)
                    if cb:
                        try:
                            cb(data)
                        except Exception as e:
                            self.log_insert(f"CMD callback error [{tag}]: {e}\n")
                    elif tag not in ('hb', 'led_write', ''):
                        if data.get('error'):
                            self.log_insert(f"CMD {tag} ERROR: {data['error']}\n")
        except Empty:
            pass
        self.root.after(20, self.process_queue)

    def on_sample(self, s: dict):
        t = s['time']
        raw = s['raw']
        regs = s['regs']
        self.log_insert(f"{t} SL={s['slave']} FC={s['fc']} R={s['reg']} RAW={raw}\n")
        # update tree
        self.tree.delete(*self.tree.get_children())
        if regs:
            # show index relative to start and named fields when known
            start_reg = int(s['reg'])
            for i, v in enumerate(regs):
                abs_reg = start_reg + i
                # Map register index to source field name if known
                if s['fc'] == 4 and abs_reg < len(SOURCE_INPUT_FIELDS):
                    name = SOURCE_INPUT_FIELDS[abs_reg]
                elif s['fc'] == 3 and abs_reg < len(SOURCE_HOLDING_FIELDS):
                    name = SOURCE_HOLDING_FIELDS[abs_reg]
                else:
                    name = None
                label = f"{abs_reg} ({name})" if name else str(abs_reg)
                self.tree.insert('', 'end', values=(label, v))
    def log_insert(self, text: str):
        self.log.insert('end', text)
        self.log.see('end')

    def _make_cmd_tag(self, prefix: str) -> str:
        self._cmd_id += 1
        return f'{prefix}_{self._cmd_id}'

    def write_register(self):
        # cautious: ask for confirmation
        port = self.port_var.get()
        if not messagebox.askyesno('Confirm write', f"Write register {self.wreg.get()} value {self.wval.get()} on {port}?\nThis will change device state."):
            return
        # perform single write (Modbus FC=6)
        try:
            ser = self._open_serial()
            slave = int(self.slave_var.get())
            reg = int(self.wreg.get())
            val = int(self.wval.get()) & 0xFFFF
            tx, rx = self._write_reg_fc6(ser, slave, reg, val)
            self._close_serial(ser)
            self.log_insert(f"WRITE TX={tx.hex()} RX={rx.hex()}\n")
        except Exception as e:
            messagebox.showerror('Write error', str(e))

    def _word_entry_values(self) -> list[int]:
        return [
            int(self.conv_w0_var.get(), 0) & 0xFFFF,
            int(self.conv_w1_var.get(), 0) & 0xFFFF,
            int(self.conv_w2_var.get(), 0) & 0xFFFF,
            int(self.conv_w3_var.get(), 0) & 0xFFFF,
        ]

    def _set_word_entries(self, words: list[int]):
        vals = list(words) + [0, 0, 0, 0]
        self.conv_w0_var.set(str(vals[0] & 0xFFFF))
        self.conv_w1_var.set(str(vals[1] & 0xFFFF))
        self.conv_w2_var.set(str(vals[2] & 0xFFFF))
        self.conv_w3_var.set(str(vals[3] & 0xFFFF))

    def read_station_window(self):
        try:
            slave = int(self.conv_slave_var.get())
            base = int(self.conv_base_var.get())
            write_words = STATION_WRITE_WORDS.get(slave, 1)
            prof = STATION_READ_PROFILE_BY_SLAVE.get(slave)

            ser = self._open_serial()

            # Read writable holding window at register 6 (source: holdingRegistersModbus[6]=LatencySQN, [7]=LedRedGreen ...)
            txw, rxw, regsw = self._read_regs(ser, slave, 3, base, write_words)
            self.log_insert(
                f"STATION OUT READ slave={slave} fc=3 reg={base} count={write_words} TX={txw.hex()} RX={rxw.hex()} REGS={regsw if regsw else []}\n"
            )
            if regsw:
                self._set_word_entries(regsw)

            # Read mapped input window profile for this station.
            if prof:
                txi, rxi, regsi = self._read_regs(ser, prof['slave'], prof['fc'], prof['reg'], prof['count'])
                self.log_insert(
                    f"STATION IN READ {prof['name']} TX={txi.hex()} RX={rxi.hex()} REGS={regsi if regsi else []}\n"
                )

            self._close_serial(ser)
            self.conv_status_var.set(f"Slave {slave}: write words={write_words}, profile={prof['name'] if prof else 'none'}")
        except Exception as e:
            messagebox.showerror('Read station window error', str(e))

    def write_station_window(self):
        try:
            slave = int(self.conv_slave_var.get())
            base = int(self.conv_base_var.get())
            write_words = STATION_WRITE_WORDS.get(slave, 1)
            words = self._word_entry_values()[:write_words]

            if not messagebox.askyesno(
                'Confirm station write',
                f"Write {write_words} holding word(s) to slave {slave} at reg {base}?"
            ):
                return

            ser = self._open_serial()
            for i, val in enumerate(words):
                reg = base + i
                tx, rx = self._write_reg_fc6(ser, slave, reg, val)
                _, rxb, regs = self._read_regs(ser, slave, 3, reg, 1)
                self.log_insert(
                    f"STATION OUT WRITE slave={slave} reg={reg} val=0x{val:04x} TX={tx.hex()} RX={rx.hex()} READBACK={regs if regs else []} RXRB={rxb.hex()}\n"
                )
            self._close_serial(ser)
        except Exception as e:
            messagebox.showerror('Write station window error', str(e))

    def apply_led_preset(self, r: int, g: int, b: int, brightness_name: str, blink_ms: int):
        self.r_var.set(str(r & 0xFF))
        self.g_var.set(str(g & 0xFF))
        self.b_var.set(str(b & 0xFF))
        self.bt_name_var.set(brightness_name)
        self.br_ms_var.set(str(blink_ms))
        self.write_leds()

    def write_leds(self):
        # Source: main.c, LED_BOARD_NODE_ID=3
        # reg7=ledRedGreen=(R<<8)|G, reg8=ledBlueBrightnessBlinkrate=(B<<8)|(bt_nibble<<4)|br_nibble
        # reg9=terminatorHeartbeat=(term<<8)|hb; heartbeat byte MUST cycle every <500ms
        try:
            r = int(self.r_var.get(), 0) & 0xFF
            g = int(self.g_var.get(), 0) & 0xFF
            b = int(self.b_var.get(), 0) & 0xFF
            term = int(self.term_var.get(), 0) & 0xFF

            bt_name = self.bt_name_var.get().strip()
            if bt_name not in BRIGHTNESS_NAME_TO_CODE:
                raise ValueError(f"Unknown brightness '{bt_name}'")
            bt_code = BRIGHTNESS_NAME_TO_CODE[bt_name] & 0x0F

            br_ms = int(self.br_ms_var.get(), 0)
            if br_ms not in BLINK_FULL_MS_TO_CODE:
                raise ValueError(f"Unknown blink period '{br_ms}' — pick from combobox")
            br_code = BLINK_FULL_MS_TO_CODE[br_ms] & 0x0F

            w_rg  = (r << 8) | g
            w_bbr = (b << 8) | ((bt_code << 4) | br_code)

            self.log_insert(
                f"LED SET slave={LED_SLAVE}  "
                f"reg{LED_REG_RG}=0x{w_rg:04X} (R={r},G={g})  "
                f"reg{LED_REG_BBR}=0x{w_bbr:04X} (B={b},BT={bt_name},BR={br_ms}ms)\n"
            )

            hb = 1
            self._execute_led_write(w_rg, w_bbr, term, hb)

            # Start heartbeat cycling via root.after (no new thread needed)
            self._hb_rg   = w_rg
            self._hb_bbr  = w_bbr
            self._hb_term = term
            self._hb_counter = hb + 1
            self._start_heartbeat_cycle()

        except Exception as e:
            messagebox.showerror('LED write error', str(e))

    def _start_heartbeat_cycle(self):
        """Schedule repeating heartbeat writes via root.after (no thread, no extra serial open)."""
        self._stop_heartbeat_cycle()
        if not self.hb_cycle_var.get():
            return
        self._hb_active = True
        self._schedule_next_hb()

    def _schedule_next_hb(self):
        if not self._hb_active:
            return
        self._hb_after_id = self.root.after(200, self._send_heartbeat)

    def _send_heartbeat(self):
        if not self._hb_active:
            return
        hb = self._hb_counter & 0xFF
        if hb == 0:
            hb = 1
        try:
            self._execute_led_write(self._hb_rg, self._hb_bbr, self._hb_term, hb)
            self._hb_counter = hb + 1
            self.hb_status_var.set(f'HB: running (hb={hb})')
        except Exception as e:
            self.hb_status_var.set(f'HB: error ({e})')
        self._schedule_next_hb()

    def _stop_heartbeat_cycle(self):
        self._hb_active = False
        if self._hb_after_id is not None:
            try:
                self.root.after_cancel(self._hb_after_id)
            except Exception:
                pass
            self._hb_after_id = None
        self.hb_status_var.set('HB: stopped')

    def stop_heartbeat_cycle(self):
        self._stop_heartbeat_cycle()

    def _start_encoder_plot_loop(self):
        self._stop_encoder_plot_loop()
        self._schedule_encoder_plot_read(1)

    def _schedule_encoder_plot_read(self, delay_ms: int = ENCODER_PLOT_INTERVAL_MS):
        try:
            delay_ms = max(1, int(self.enc_auto_ms_var.get(), 0))
        except Exception:
            delay_ms = ENCODER_PLOT_INTERVAL_MS
        if self._enc_plot_after_id is not None:
            try:
                self.root.after_cancel(self._enc_plot_after_id)
            except Exception:
                pass
        self._enc_plot_after_id = self.root.after(delay_ms, self._queue_encoder_plot_read)

    def _queue_encoder_plot_read(self):
        self._enc_plot_after_id = None
        if not self.enc_auto_var.get():
            return
        if self._enc_plot_pending:
            self._schedule_encoder_plot_read()
            return
        self._enc_plot_pending = True
        try:
            self.read_all_encoders(schedule_loop=False)
        finally:
            self._enc_plot_pending = False
            self._schedule_encoder_plot_read()

    def _on_encoder_plot_result(self, data: dict):
        self._enc_plot_pending = False
        try:
            if data.get('error'):
                self.log_insert(f"ENC-PLOT ERROR: {data['error']}\n")
                return

            results = data.get('results', [])
            values: dict[str, int | None] = {}
            states: dict[str, bool] = {}
            for (name, _), result in zip(ENCODER_READ_MAP.items(), results):
                regs = result.get('regs') or []
                if regs:
                    dec = decode_encoder_word(regs[0])
                    values[name] = int(dec['position'])
                    states[name] = bool(dec['valid'])
                else:
                    values[name] = None
                    states[name] = False
            self._apply_encoder_snapshot(values, states)
        finally:
            self._schedule_encoder_plot_read()

    def _stop_encoder_plot_loop(self):
        self._enc_plot_pending = False
        if self._enc_plot_after_id is not None:
            try:
                self.root.after_cancel(self._enc_plot_after_id)
            except Exception:
                pass
            self._enc_plot_after_id = None

    def toggle_encoder_auto(self):
        if self.enc_auto_var.get():
            self.read_all_encoders(schedule_loop=False)
            self._start_encoder_plot_loop()
        else:
            self._stop_encoder_plot_loop()

    def _encoder_status_text(self, label: str, value: int | None, valid: bool) -> str:
        if value is None:
            return f'{label}: -'
        suffix = ' ok' if valid else ' invalid/vibrating'
        return f'{label}: {value}{suffix}'

    def _apply_encoder_snapshot(self, values: dict[str, int | None], states: dict[str, bool]):
        self.enc_s3_var.set(self._encoder_status_text('S3', values.get('S3EncoderValue'), states.get('S3EncoderValue', False)))
        self.enc_s2_var.set(self._encoder_status_text('S2', values.get('S2EncoderValue'), states.get('S2EncoderValue', False)))
        self.enc_s1_var.set(self._encoder_status_text('S1', values.get('S1EncoderValue'), states.get('S1EncoderValue', False)))

        if all(values.get(key) is not None for key in ENCODER_READ_MAP):
            self._enc_plot_index += 1
            self.plot_time.append(self._enc_plot_index)
            self.plot_series['S3'].append(int(values['S3EncoderValue']))
            self.plot_series['S2'].append(int(values['S2EncoderValue']))
            self.plot_series['S1'].append(int(values['S1EncoderValue']))
            if len(self.plot_time) > self.max_points:
                self.plot_time = self.plot_time[-self.max_points:]
                for key in self.plot_series:
                    self.plot_series[key] = self.plot_series[key][-self.max_points:]
            now = time.monotonic()
            if now - self._last_plot_draw >= 0.02:
                self.update_plot()
                self._last_plot_draw = now

    def _read_encoder_snapshot(self) -> tuple[dict[str, int | None], dict[str, bool]]:
        ser = self._open_serial()
        try:
            values: dict[str, int | None] = {}
            states: dict[str, bool] = {}
            for name, spec in ENCODER_READ_MAP.items():
                _, _, regs = self._read_regs(ser, spec['slave'], spec['fc'], spec['reg'], spec['count'])
                if regs:
                    dec = decode_encoder_word(regs[0])
                    values[name] = int(dec['position'])
                    states[name] = bool(dec['valid'])
                else:
                    values[name] = None
                    states[name] = False
            return values, states
        finally:
            self._close_serial(ser)

    def _execute_batch_sync(self, cmds: list[dict]):
        ser = self._open_serial()
        try:
            results = []
            for cmd in cmds:
                if cmd['type'] == 'write_fc6':
                    tx, rx = self._write_reg_fc6(ser, cmd['slave'], cmd['reg'], cmd['val'])
                    results.append({'type': 'write_fc6', 'tx': tx.hex(), 'rx': rx.hex() if rx else ''})
                elif cmd['type'] == 'write_fc16':
                    tx, rx = self._write_regs_fc16(ser, cmd['slave'], cmd['reg'], cmd['values'])
                    results.append({'type': 'write_fc16', 'tx': tx.hex(), 'rx': rx.hex() if rx else ''})
                elif cmd['type'] == 'read_regs':
                    tx, rx, regs = self._read_regs(ser, cmd['slave'], cmd['fc'], cmd['reg'], cmd['count'])
                    results.append({'type': 'read_regs', 'tx': tx.hex(), 'rx': rx.hex() if rx else '', 'regs': regs})
            return results
        finally:
            self._close_serial(ser)

    def _execute_led_write(self, w_rg: int, w_bbr: int, term: int, hb: int):
        reg9 = ((term & 0xFF) << 8) | (hb & 0xFF)
        results = self._execute_batch_sync([
            {'type': 'write_fc16', 'slave': LED_SLAVE, 'reg': LED_REG_RG, 'values': [w_rg, w_bbr, reg9]},
            {'type': 'read_regs', 'slave': LED_SLAVE, 'fc': 3, 'reg': LED_REG_RG, 'count': 3},
        ])
        if len(results) >= 2:
            readback = results[1].get('regs') or []
            self.log_insert(f"LED WRITEBACK regs7-9={readback}\n")

    def read_all_encoders(self, schedule_loop: bool = True):
        try:
            values, states = self._read_encoder_snapshot()
            self._apply_encoder_snapshot(values, states)
            if schedule_loop and self.enc_auto_var.get():
                self._start_encoder_plot_loop()
        except Exception as e:
            messagebox.showerror('Encoder read error', str(e))

    def _open_serial(self):
        """Return the worker's shared serial connection (with lock held), or open a
        new one-shot connection when the worker is not running.
        ALWAYS call _close_serial(ser) when done to release the lock or close.
        """
        if self.worker and self.worker.is_alive() and self.worker.ser and self.worker.ser.is_open:
            self.worker._lock.acquire()
            return self.worker.ser
        # Worker not running — open a temporary dedicated connection
        return _open_ser({
            'port': self.port_var.get(), 'baud': self.baud_var.get(),
            'parity': self.par_var.get(), 'stop': self.stop_var.get(),
        })

    def _close_serial(self, ser):
        """Release the lock if we borrowed the worker's ser, otherwise close."""
        if (self.worker and self.worker.is_alive()
                and self.worker.ser is ser):
            self.worker._lock.release()
        else:
            try:
                ser.close()
            except Exception:
                pass

    def _read_regs(self, ser, slave: int, fc: int, reg: int, count: int):
        p = struct.pack('>B B H H', slave, fc, reg, count)
        frame = p + crc16(p)
        rx = _transact(ser, frame, 512, expected_len=_expected_modbus_reply_length(fc, count), timeout_s=0.02)
        ok = bool(rx and len(rx) >= 5 and crc16(rx[:-2]) == rx[-2:])
        regs = parse_regs_from_reply(rx) if ok else None
        return frame, rx, regs

    def _write_reg_fc6(self, ser, slave: int, reg: int, val: int):
        p = struct.pack('>B B H H', slave, 6, reg, val & 0xFFFF)
        frame = p + crc16(p)
        rx = _transact(ser, frame, 256, expected_len=_expected_modbus_reply_length(6), timeout_s=0.02)
        return frame, rx

    def _write_regs_fc16(self, ser, slave: int, start_reg: int, values: list[int]):
        count = len(values)
        payload = bytearray(struct.pack('>B B H H B', slave, 16, start_reg, count, count * 2))
        for value in values:
            payload.extend(struct.pack('>H', value & 0xFFFF))
        frame = bytes(payload) + crc16(bytes(payload))
        rx = _transact(ser, frame, 256, expected_len=_expected_modbus_reply_length(16), timeout_s=0.02)
        return frame, rx

    def _regs_to_bytes(self, regs: list[int]) -> bytearray:
        out = bytearray()
        for r in regs:
            out.append((r >> 8) & 0xFF)
            out.append(r & 0xFF)
        return out

    def _bytes_to_regs(self, b: bytearray) -> list[int]:
        regs = []
        for i in range(0, len(b), 2):
            hi = b[i] if i < len(b) else 0
            lo = b[i + 1] if i + 1 < len(b) else 0
            regs.append((hi << 8) | lo)
        return regs

    def read_output_block(self):
        try:
            base = int(self.conv_base_var.get())
            slave = int(self.conv_slave_var.get())
            ser = self._open_serial()
            _, rx, regs = self._read_regs(ser, slave, 3, base, CONVERTER_OUT_REG_COUNT)
            self._close_serial(ser)
            self.log_insert(f"OUT-BLOCK READ A={slave} R={base} C={CONVERTER_OUT_REG_COUNT} RX={rx.hex()}\n")
            if not regs:
                return

            b = self._regs_to_bytes(regs)
            self.roi_hb_var.set(str(b[0]))
            self.roi_term_var.set(str(b[1]))
            self.roi_bb_var.set(str(b[2]))
            self.roi_b_var.set(str(b[3]))
            self.roi_g_var.set(str(b[4]))
            self.roi_r_var.set(str(b[5]))
            self.roi_lat_var.set(str((b[6] << 8) | b[7]))

            self.s3_hb_var.set(str(b[8]))
            self.s3_term_var.set(str(b[9]))
            self.s3_bb_var.set(str(b[10]))
            self.s3_b_var.set(str(b[11]))
            self.s3_g_var.set(str(b[12]))
            self.s3_r_var.set(str(b[13]))
            self.s3_lat_var.set(str((b[14] << 8) | b[15]))
            self.s2_lat_var.set(str((b[16] << 8) | b[17]))
            self.s1_lat_var.set(str((b[18] << 8) | b[19]))
            for i in range(10):
                off = 20 + i * 2
                self.add_vars[i].set(str((b[off] << 8) | b[off + 1]))
        except Exception as e:
            messagebox.showerror('Read out block error', str(e))

    def write_output_block(self):
        try:
            base = int(self.conv_base_var.get())
            slave = int(self.conv_slave_var.get())
            ser = self._open_serial()

            # Preserve unknown bytes by reading current block first.
            _, rx0, regs0 = self._read_regs(ser, slave, 3, base, CONVERTER_OUT_REG_COUNT)
            if regs0 and len(regs0) >= CONVERTER_OUT_REG_COUNT:
                b = self._regs_to_bytes(regs0)
            else:
                b = bytearray(CONVERTER_OUT_REG_COUNT * 2)
                self.log_insert(f"OUT-BLOCK PRE-READ failed, writing from zeros RX={rx0.hex()}\n")

            b[0] = int(self.roi_hb_var.get()) & 0xFF
            b[1] = int(self.roi_term_var.get()) & 0xFF
            b[2] = int(self.roi_bb_var.get()) & 0xFF
            b[3] = int(self.roi_b_var.get()) & 0xFF
            b[4] = int(self.roi_g_var.get()) & 0xFF
            b[5] = int(self.roi_r_var.get()) & 0xFF
            roi_lat = int(self.roi_lat_var.get()) & 0xFFFF
            b[6], b[7] = (roi_lat >> 8) & 0xFF, roi_lat & 0xFF

            b[8] = int(self.s3_hb_var.get()) & 0xFF
            b[9] = int(self.s3_term_var.get()) & 0xFF
            b[10] = int(self.s3_bb_var.get()) & 0xFF
            b[11] = int(self.s3_b_var.get()) & 0xFF
            b[12] = int(self.s3_g_var.get()) & 0xFF
            b[13] = int(self.s3_r_var.get()) & 0xFF
            s3_lat = int(self.s3_lat_var.get()) & 0xFFFF
            b[14], b[15] = (s3_lat >> 8) & 0xFF, s3_lat & 0xFF
            s2_lat = int(self.s2_lat_var.get()) & 0xFFFF
            b[16], b[17] = (s2_lat >> 8) & 0xFF, s2_lat & 0xFF
            s1_lat = int(self.s1_lat_var.get()) & 0xFFFF
            b[18], b[19] = (s1_lat >> 8) & 0xFF, s1_lat & 0xFF

            for i in range(10):
                v = int(self.add_vars[i].get()) & 0xFFFF
                off = 20 + i * 2
                b[off], b[off + 1] = (v >> 8) & 0xFF, v & 0xFF

            new_regs = self._bytes_to_regs(b)
            if not messagebox.askyesno(
                'Confirm full block write',
                f"Write {CONVERTER_OUT_REG_COUNT} regs starting at {base} on slave {slave}?"
            ):
                self._close_serial(ser)
                return

            for i, val in enumerate(new_regs):
                reg = base + i
                tx, rx = self._write_reg_fc6(ser, slave, reg, val)
                self.log_insert(f"OUT-BLOCK WRITE reg={reg} val=0x{val:04x} TX={tx.hex()} RX={rx.hex()}\n")

            self._close_serial(ser)
        except Exception as e:
            messagebox.showerror('Write out block error', str(e))

    def read_converter_profiles(self):
        try:
            ser = self._open_serial()
            for prof in CONVERTER_READ_PROFILES:
                tx, rx, regs = self._read_regs(
                    ser,
                    prof['slave'],
                    prof['fc'],
                    prof['reg'],
                    prof['count'],
                )
                self.log_insert(
                    f"PROFILE {prof['name']} TX={tx.hex()} RX={rx.hex()} REGS={regs if regs else []}\n"
                )
            self._close_serial(ser)
        except Exception as e:
            messagebox.showerror('Profile poll error', str(e))

    def _decode_source_field(self, field: str, value: int, regs: list[int] | None = None) -> str:
        if field == 'EdFpnFprFbn':
            d = decode_general_info_word(value)
            return f"ED={d['ED']} FPN={d['FPN']} FPR={d['FPR']} FBN={d['FBN']}"
        if field == 'LedRedGreen':
            d = decode_led_red_green(value)
            return f"R={d['Red']} G={d['Green']}"
        if field == 'LedBlueBrightnessBlinkrate':
            d = decode_led_blue_bt_br(value)
            return f"B={d['Blue']} BT=0x{d['BT']:X} BR=0x{d['BR']:X}"
        if field == 'TerminatorHeartbeat':
            d = decode_term_hb(value)
            return f"Term={d['Terminator']} HB={d['Heartbeat']}"
        if regs and field == 'LsbEncoderSQN' and len(regs) > 1:
            msb = regs[1] if len(regs) > 1 else 0
            return f"EncoderSQN={(msb << 16) | value}"
        if regs and field == 'LsbFrameSQN' and len(regs) > 3:
            msb = regs[3] if len(regs) > 3 else 0
            return f"FrameSQN={(msb << 16) | value}"
        return ''

    def _snapshot_insert(self, station: str, group: str, field: str, value: int | None, decoded: str = ''):
        if value is None:
            val_txt = '-'
        else:
            val_txt = f"{value} (0x{value:04X})"
        self.snapshot_tree.insert('', 'end', values=(station, group, field, val_txt, decoded))

    def read_full_field_snapshot(self):
        # Pull all source-defined fields as exposed by the gateway station windows.
        try:
            self.snapshot_tree.delete(*self.snapshot_tree.get_children())
            ser = self._open_serial()
            in_profiles = [
                {'slave': 1, 'reg': 0, 'count': 8, 'station': 'S3'},
                {'slave': 2, 'reg': 0, 'count': 8, 'station': 'S2'},
                {'slave': 3, 'reg': 0, 'count': 10, 'station': 'S1'},
                {'slave': 4, 'reg': 3, 'count': 7, 'station': 'S4'},
            ]
            out_profiles = [
                {'slave': 1, 'reg': 6, 'count': 1, 'station': 'S3'},
                {'slave': 2, 'reg': 6, 'count': 1, 'station': 'S2'},
                {'slave': 3, 'reg': 6, 'count': 4, 'station': 'S1'},
                {'slave': 4, 'reg': 6, 'count': 4, 'station': 'S4'},
            ]

            for p in in_profiles:
                tx, rx, regs = self._read_regs(ser, p['slave'], 4, p['reg'], p['count'])
                self.log_insert(
                    f"FULL SNAPSHOT IN station={p['station']} slave={p['slave']} reg={p['reg']} count={p['count']} TX={tx.hex()} RX={rx.hex()} REGS={regs if regs else []}\n"
                )
                if not regs:
                    self._snapshot_insert(p['station'], 'Input', 'Window', None, 'no response or invalid CRC')
                    continue

                for idx, val in enumerate(regs):
                    field = SOURCE_INPUT_FIELDS[idx] if idx < len(SOURCE_INPUT_FIELDS) else f"InputReg{idx}"
                    decoded = self._decode_source_field(field, val, regs)
                    self._snapshot_insert(p['station'], 'Input', f"r{p['reg'] + idx} {field}", val, decoded)

            for p in out_profiles:
                tx, rx, regs = self._read_regs(ser, p['slave'], 3, p['reg'], p['count'])
                self.log_insert(
                    f"FULL SNAPSHOT OUT station={p['station']} slave={p['slave']} reg={p['reg']} count={p['count']} TX={tx.hex()} RX={rx.hex()} REGS={regs if regs else []}\n"
                )
                if not regs:
                    self._snapshot_insert(p['station'], 'Holding', 'Window', None, 'no response or invalid CRC')
                    continue

                # Gateway exposes write windows starting at source index 6.
                src_start = 6
                for idx, val in enumerate(regs):
                    src_idx = src_start + idx
                    field = SOURCE_HOLDING_FIELDS[src_idx] if src_idx < len(SOURCE_HOLDING_FIELDS) else f"HoldingReg{src_idx}"
                    decoded = self._decode_source_field(field, val, regs)
                    self._snapshot_insert(p['station'], 'Holding', f"r{p['reg'] + idx} {field}", val, decoded)

            self._close_serial(ser)
        except Exception as e:
            messagebox.showerror('Read full snapshot error', str(e))

    def update_plot(self):
        self.plot_ax.clear()
        if not self.plot_time:
            self.plot_ax.set_title('Encoder Positions')
            self.plot_ax.set_xlabel('samples')
            self.plot_ax.set_ylabel('position (0..32767)')
            self.plot_canvas.draw_idle()
            return
        for label, color in [('S3', '#d62728'), ('S2', '#2ca02c'), ('S1', '#1f77b4')]:
            series = self.plot_series[label]
            if series:
                self.plot_ax.plot(self.plot_time[-len(series):], series, label=label, color=color, linewidth=1.6)
        self.plot_ax.legend(loc='upper right')
        self.plot_ax.set_title('Encoder Positions')
        self.plot_ax.set_xlabel('samples')
        self.plot_ax.set_ylabel('position (0..32767)')
        self.plot_ax.grid(True, alpha=0.3)
        self.plot_canvas.draw_idle()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
