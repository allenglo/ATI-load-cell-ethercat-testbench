#!/usr/bin/env python3
"""Targeted Modbus RTU probe for EEA devices on COM port.

Sends read-holding-register (FC=3) frames to address range and a small set
of registers using the DTM-suggested serial settings, logging timestamped
responses until a valid Modbus reply (CRC OK, matching slave) is observed.

Usage: run from project root with the venv active. The script will write
responses to notes/gateway_reverse_engineering/probe_log.txt
"""
from __future__ import annotations

import time
import serial
import serial.rs485
from datetime import datetime

PARITY_MAP = {0: serial.PARITY_NONE, 1: serial.PARITY_EVEN, 2: serial.PARITY_ODD}


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


def make_read_frame(slave: int, reg: int, count: int = 8) -> bytes:
    import struct

    p = struct.pack(
        ">B B H H",
        slave,
        3,
        reg,
        count,
    )
    return p + crc16(p)


def valid_modbus_reply(tx_slave: int, rx: bytes) -> bool:
    # basic sanity checks: length >=5, CRC ok, slave matches
    if not rx or len(rx) < 5:
        return False
    if rx[0] != tx_slave:
        return False
    # verify CRC
    msg, rcrc = rx[:-2], rx[-2:]
    if crc16(msg) != rcrc:
        return False
    return True


def main() -> int:
    port = "COM18"
    baud = 115200
    parity_enum = 1
    stopbits = 1
    timeout = 0.2
    addresses = list(range(1, 17))
    registers = [0, 2880]
    count = 8

    parity = PARITY_MAP.get(parity_enum, serial.PARITY_EVEN)

    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baud
    ser.parity = parity
    ser.stopbits = serial.STOPBITS_ONE if stopbits == 1 else serial.STOPBITS_TWO
    ser.bytesize = serial.EIGHTBITS
    ser.timeout = timeout

    # configure RS485 driver toggling if available
    try:
        ser.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=True, rts_level_for_rx=False, delay_before_tx=None, delay_before_rx=None
        )
    except Exception:
        pass

    print(f"Opening {port} @ {baud} parity={parity} stopbits={stopbits}")
    ser.open()

    # set after open if necessary
    try:
        ser.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=True, rts_level_for_rx=False, delay_before_tx=None, delay_before_rx=None
        )
    except Exception:
        pass

    logpath = "notes/gateway_reverse_engineering/probe_log.txt"
    # ensure directory exists
    import os
    os.makedirs(os.path.dirname(logpath), exist_ok=True)
    found = False
    attempt = 0
    start = time.time()
    with open(logpath, "a", encoding="utf-8") as lf:
        lf.write(f"\n--- Probe run start {datetime.utcnow().isoformat()}Z ---\n")
        # loop until we find at least one valid reply
        while not found and attempt < 1000:
            attempt += 1
            for a in addresses:
                for r in registers:
                    frame = make_read_frame(a, r, count)
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    t0 = datetime.utcnow()
                    ser.write(frame)
                    ser.flush()
                    time.sleep(0.05)
                    rx = ser.read(512)
                    t1 = datetime.utcnow()
                    entry = f"{t1.isoformat()}Z TX a={a} r={r} len={len(frame)} txhex={frame.hex()} -> RX len={len(rx)} rxhex={rx.hex()}\n"
                    print(entry.strip())
                    lf.write(entry)
                    lf.flush()
                    if valid_modbus_reply(a, rx):
                        found = True
                        lf.write(f"VALID_REPLY {t1.isoformat()}Z slave={a} reg={r} rx={rx.hex()}\n")
                        print("VALID_REPLY", a, r, rx.hex())
                        break
                if found:
                    break
            # small pause between rounds
            time.sleep(0.1)

    ser.close()
    dur = time.time() - start
    print(f"Probe finished attempts={attempt} duration_s={dur:.1f} found={found}")
    return 0 if found else 2


if __name__ == "__main__":
    raise SystemExit(main())
