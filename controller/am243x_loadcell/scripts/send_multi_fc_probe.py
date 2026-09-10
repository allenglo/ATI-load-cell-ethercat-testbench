#!/usr/bin/env python3
"""Broader non-destructive Modbus probe: try FC=1,2,3,4 across address/reg ranges.

Logs timestamped TX/RX and records which addr/fc/reg produced valid replies.
"""
from __future__ import annotations

import struct
import time
from datetime import datetime
import serial
import serial.rs485


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
    if fc in (1, 2):
        # coils/discrete: reg, count
        p = struct.pack(">B B H H", slave, fc, reg, count)
    elif fc in (3, 4):
        p = struct.pack(">B B H H", slave, fc, reg, count)
    else:
        raise ValueError("unsupported fc")
    return p + crc16(p)


def valid_reply(tx_slave: int, rx: bytes) -> bool:
    if not rx or len(rx) < 5:
        return False
    if rx[0] != tx_slave:
        return False
    if crc16(rx[:-2]) != rx[-2:]:
        return False
    return True


def main() -> int:
    port = "COM18"
    baud = 115200
    parity = serial.PARITY_EVEN
    stopbits = serial.STOPBITS_ONE
    timeout = 0.15

    addresses = list(range(1, 9))
    registers_small = list(range(0, 17))
    registers_big = list(range(2880, 2896))
    fcs = [1, 2, 3, 4]
    count = 4

    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baud
    ser.parity = parity
    ser.stopbits = stopbits
    ser.bytesize = serial.EIGHTBITS
    ser.timeout = timeout

    try:
        ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=True, rts_level_for_rx=False, delay_before_tx=None, delay_before_rx=None)
    except Exception:
        pass

    print(f"Opening {port} @ {baud} parity={parity}")
    ser.open()

    log = "notes/gateway_reverse_engineering/multi_fc_probe_log.txt"
    import os
    os.makedirs(os.path.dirname(log), exist_ok=True)

    found = []
    with open(log, "a", encoding="utf-8") as lf:
        lf.write(f"\n--- Multi-FC probe start {datetime.utcnow().isoformat()}Z ---\n")
        for a in addresses:
            for fc in fcs:
                # try small registers then big block
                for reg in registers_small + registers_big:
                    frame = make_frame(a, fc, reg, count)
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    t1 = datetime.utcnow()
                    ser.write(frame)
                    ser.flush()
                    time.sleep(0.04)
                    rx = ser.read(512)
                    t2 = datetime.utcnow()
                    line = f"{t2.isoformat()}Z A={a} FC={fc} R={reg} TX={frame.hex()} RX={rx.hex()}\n"
                    lf.write(line)
                    lf.flush()
                    print(line.strip())
                    if valid_reply(a, rx):
                        found.append((a, fc, reg, rx.hex()))
                        lf.write(f"VALID A={a} FC={fc} R={reg} RX={rx.hex()}\n")
                        lf.flush()
        lf.write(f"--- Multi-FC probe end {datetime.utcnow().isoformat()}Z found={len(found)} ---\n")

    ser.close()
    print(f"Done, found {len(found)} replies. Log: {log}")
    if found:
        for f in found:
            print("FOUND:", f)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
