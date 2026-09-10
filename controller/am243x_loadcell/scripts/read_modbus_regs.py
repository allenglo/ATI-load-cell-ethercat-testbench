#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
import time

import serial
import serial.rs485


PARITY_MAP = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}


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


def parse_regs(rx: bytes) -> list[int] | None:
    if not rx or len(rx) < 5:
        return None
    bc = rx[2]
    data = rx[3 : 3 + bc]
    out = []
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            out.append((data[i] << 8) | data[i + 1])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Read Modbus FC3/FC4 registers")
    parser.add_argument("--port", default="COM18")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--parity", default="E", choices=["N", "E", "O"])
    parser.add_argument("--stopbits", type=int, default=1, choices=[1, 2])
    parser.add_argument("--slave", type=int, required=True)
    parser.add_argument("--fc", type=int, default=4, choices=[3, 4])
    parser.add_argument("--reg", type=int, required=True)
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    ser = serial.Serial()
    ser.port = args.port
    ser.baudrate = args.baud
    ser.parity = PARITY_MAP[args.parity]
    ser.stopbits = serial.STOPBITS_ONE if args.stopbits == 1 else serial.STOPBITS_TWO
    ser.bytesize = serial.EIGHTBITS
    ser.timeout = 0.5
    try:
        ser.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=True,
            rts_level_for_rx=False,
            delay_before_tx=None,
            delay_before_rx=None,
        )
    except Exception:
        pass
    ser.open()

    try:
        p = struct.pack(">B B H H", args.slave, args.fc, args.reg, args.count)
        tx = p + crc16(p)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(tx)
        ser.flush()
        time.sleep(0.03)
        rx = ser.read(512)

        crc_ok = bool(rx and len(rx) >= 5 and crc16(rx[:-2]) == rx[-2:])
        regs = parse_regs(rx) if crc_ok else None

        print(f"TX={tx.hex()}")
        print(f"RX={rx.hex()}")
        print(f"CRC_OK={crc_ok}")
        print(f"REGS={regs}")

        return 0 if crc_ok else 2
    finally:
        ser.close()


if __name__ == "__main__":
    raise SystemExit(main())
