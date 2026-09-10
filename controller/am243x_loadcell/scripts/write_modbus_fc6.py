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
    parser = argparse.ArgumentParser(description="Write one Modbus holding register (FC6) and read back")
    parser.add_argument("--port", default="COM18")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--parity", default="E", choices=["N", "E", "O"])
    parser.add_argument("--stopbits", type=int, default=1, choices=[1, 2])
    parser.add_argument("--slave", type=int, required=True)
    parser.add_argument("--reg", type=int, required=True)
    parser.add_argument("--value", type=lambda x: int(x, 0), required=True)
    parser.add_argument("--verify-fc", type=int, default=3, choices=[3, 4])
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
        # pre-read
        pre_p = struct.pack(">B B H H", args.slave, args.verify_fc, args.reg, 1)
        pre_tx = pre_p + crc16(pre_p)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(pre_tx)
        ser.flush()
        time.sleep(0.03)
        pre_rx = ser.read(256)
        pre_ok = bool(pre_rx and len(pre_rx) >= 5 and crc16(pre_rx[:-2]) == pre_rx[-2:])
        pre_regs = parse_regs(pre_rx) if pre_ok else None

        # write
        value = args.value & 0xFFFF
        wp = struct.pack(">B B H H", args.slave, 6, args.reg, value)
        wtx = wp + crc16(wp)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(wtx)
        ser.flush()
        time.sleep(0.03)
        wrx = ser.read(256)
        w_ok = bool(wrx and len(wrx) >= 8 and crc16(wrx[:-2]) == wrx[-2:] and wrx[:6] == wtx[:6])

        # post-read
        post_p = struct.pack(">B B H H", args.slave, args.verify_fc, args.reg, 1)
        post_tx = post_p + crc16(post_p)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(post_tx)
        ser.flush()
        time.sleep(0.03)
        post_rx = ser.read(256)
        post_ok = bool(post_rx and len(post_rx) >= 5 and crc16(post_rx[:-2]) == post_rx[-2:])
        post_regs = parse_regs(post_rx) if post_ok else None

        print(f"PRE_TX={pre_tx.hex()} PRE_RX={pre_rx.hex()} PRE_OK={pre_ok} PRE_REGS={pre_regs}")
        print(f"WR_TX={wtx.hex()} WR_RX={wrx.hex()} WR_OK={w_ok}")
        print(f"POST_TX={post_tx.hex()} POST_RX={post_rx.hex()} POST_OK={post_ok} POST_REGS={post_regs}")

        return 0 if (pre_ok and w_ok and post_ok) else 2
    finally:
        ser.close()


if __name__ == "__main__":
    raise SystemExit(main())
