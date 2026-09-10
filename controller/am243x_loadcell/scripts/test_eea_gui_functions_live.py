#!/usr/bin/env python3
"""Live non-destructive validation for EEA GUI serial functions.

This script exercises the same wire-level operations used by eea_testbench_gui.py:
- FC3/FC4 polling
- converter profile polling
- full output block read + write-back (same values)
- single-register write-back (same value)
- LED register write path using S3 mapping (write-back same values)

No intentional value mutation is performed.
"""

from __future__ import annotations

import argparse
import json
import struct
import time
from datetime import datetime

import serial
import serial.rs485


OUTPUTS_START = 4352
CONVERTER_OUT_BASE_DEFAULT = 6
CONVERTER_OUT_REG_COUNT = 20
CONVERTER_READ_PROFILES = [
    {"name": "Addr1 FC4 R0 C8", "slave": 1, "fc": 4, "reg": 0, "count": 8},
    {"name": "Addr2 FC4 R0 C10", "slave": 2, "fc": 4, "reg": 0, "count": 10},
    {"name": "Addr3 FC4 R3 C7", "slave": 3, "fc": 4, "reg": 3, "count": 7},
    {"name": "Addr4 FC4 R0 C8", "slave": 4, "fc": 4, "reg": 0, "count": 8},
]


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


def parse_regs_from_reply(rx: bytes) -> list[int] | None:
    if not rx or len(rx) < 5:
        return None
    byte_count = rx[2]
    data = rx[3 : 3 + byte_count]
    out = []
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            out.append((data[i] << 8) | data[i + 1])
    return out


def regs_to_bytes(regs: list[int]) -> bytearray:
    out = bytearray()
    for value in regs:
        out.append((value >> 8) & 0xFF)
        out.append(value & 0xFF)
    return out


def open_serial(port: str, baud: int, parity: str, stop_bits: int, timeout: float) -> serial.Serial:
    parity_map = {
        "N": serial.PARITY_NONE,
        "E": serial.PARITY_EVEN,
        "O": serial.PARITY_ODD,
    }
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baud
    ser.parity = parity_map.get(parity.upper(), serial.PARITY_EVEN)
    ser.stopbits = serial.STOPBITS_ONE if stop_bits == 1 else serial.STOPBITS_TWO
    ser.bytesize = serial.EIGHTBITS
    ser.timeout = timeout
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
    return ser


def read_regs(ser: serial.Serial, slave: int, fc: int, reg: int, count: int) -> dict:
    payload = struct.pack(">B B H H", slave, fc, reg, count)
    tx = payload + crc16(payload)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(tx)
    ser.flush()
    time.sleep(0.03)
    rx = ser.read(512)
    valid_crc = bool(rx and len(rx) >= 5 and crc16(rx[:-2]) == rx[-2:])
    regs = parse_regs_from_reply(rx) if valid_crc else None
    return {
        "tx": tx.hex(),
        "rx": rx.hex(),
        "valid_crc": valid_crc,
        "regs": regs,
    }


def write_fc6(ser: serial.Serial, slave: int, reg: int, value: int) -> dict:
    payload = struct.pack(">B B H H", slave, 6, reg, value & 0xFFFF)
    tx = payload + crc16(payload)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(tx)
    ser.flush()
    time.sleep(0.02)
    rx = ser.read(256)
    valid_crc = bool(rx and len(rx) >= 8 and crc16(rx[:-2]) == rx[-2:])
    echo_match = bool(valid_crc and rx[:6] == tx[:6])
    return {
        "tx": tx.hex(),
        "rx": rx.hex(),
        "valid_crc": valid_crc,
        "echo_match": echo_match,
    }


def run_test(args: argparse.Namespace) -> dict:
    now = datetime.utcnow().isoformat() + "Z"
    result = {
        "timestamp": now,
        "port": args.port,
        "baud": args.baud,
        "parity": args.parity,
        "stop_bits": args.stopbits,
        "slave": args.slave,
        "checks": {},
    }

    ser = open_serial(args.port, args.baud, args.parity, args.stopbits, args.timeout)
    try:
        checks = result["checks"]

        # 1) FC4 and FC3 base poll
        checks["poll_fc4"] = read_regs(ser, args.slave, 4, args.reg, args.count)
        checks["poll_fc3"] = read_regs(ser, args.slave, 3, args.reg, args.count)

        # 2) Profile poll set
        profile_rows = []
        for profile in CONVERTER_READ_PROFILES:
            row = {"profile": profile}
            row.update(read_regs(ser, profile["slave"], profile["fc"], profile["reg"], profile["count"]))
            profile_rows.append(row)
        checks["profile_poll"] = profile_rows

        # 3) Output block read
        out_read = read_regs(ser, args.slave, 3, args.out_base, CONVERTER_OUT_REG_COUNT)
        checks["output_block_read"] = out_read

        # 4) Output block write-back same values
        out_write_rows = []
        if out_read.get("regs") and len(out_read["regs"]) >= CONVERTER_OUT_REG_COUNT:
            for index, value in enumerate(out_read["regs"][:CONVERTER_OUT_REG_COUNT]):
                reg = args.out_base + index
                wr = write_fc6(ser, args.slave, reg, value)
                wr["reg"] = reg
                wr["value"] = value
                out_write_rows.append(wr)
        checks["output_block_writeback"] = out_write_rows

        # 5) Single register write-back same value
        single_read = read_regs(ser, args.slave, 3, args.single_reg, 1)
        single_wr = None
        if single_read.get("regs"):
            single_wr = write_fc6(ser, args.slave, args.single_reg, single_read["regs"][0])
        checks["single_writeback"] = {
            "pre_read": single_read,
            "write": single_wr,
        }

        # 6) LED mapping write path using read-modify-write with no net change
        led_bits = {"B": 296, "G": 304, "R": 312}
        led_regs = sorted({OUTPUTS_START + (bit // 16) for bit in led_bits.values()})
        led_rows = []
        for reg in led_regs:
            reg_read = read_regs(ser, args.slave, 3, reg, 1)
            row = {"reg": reg, "read": reg_read, "write": None}
            if reg_read.get("regs"):
                current = reg_read["regs"][0]
                row["write"] = write_fc6(ser, args.slave, reg, current)
            led_rows.append(row)
        checks["led_write_path"] = led_rows

        # Plausibility summary
        profile_ok = sum(1 for r in profile_rows if r.get("valid_crc"))
        out_write_ok = sum(1 for r in out_write_rows if r.get("valid_crc") and r.get("echo_match"))
        led_write_ok = sum(
            1
            for r in led_rows
            if (r.get("write") or {}).get("valid_crc") and (r.get("write") or {}).get("echo_match")
        )
        result["plausibility"] = {
            "poll_fc4_ok": bool(checks["poll_fc4"].get("valid_crc")),
            "poll_fc3_ok": bool(checks["poll_fc3"].get("valid_crc")),
            "profile_ok_count": profile_ok,
            "profile_total": len(profile_rows),
            "out_block_read_ok": bool(out_read.get("valid_crc")),
            "out_block_write_ok_count": out_write_ok,
            "out_block_write_total": len(out_write_rows),
            "single_write_ok": bool(
                (single_wr or {}).get("valid_crc") and (single_wr or {}).get("echo_match")
            ),
            "led_write_ok_count": led_write_ok,
            "led_write_total": len(led_rows),
        }
    finally:
        ser.close()

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live EEA GUI function tester")
    parser.add_argument("--port", default="COM18")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--parity", default="E", choices=["N", "E", "O"])
    parser.add_argument("--stopbits", type=int, default=1, choices=[1, 2])
    parser.add_argument("--timeout", type=float, default=0.5)
    parser.add_argument("--slave", type=int, default=1)
    parser.add_argument("--reg", type=int, default=0)
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--out-base", dest="out_base", type=int, default=CONVERTER_OUT_BASE_DEFAULT)
    parser.add_argument("--single-reg", dest="single_reg", type=int, default=6)
    parser.add_argument(
        "--out",
        default=r"c:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\notes\host_master\EEA_GUI_LIVE_TEST_RESULTS.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = run_test(args)
    out_path = args.out
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    print(f"saved={out_path}")
    print(json.dumps(data.get("plausibility", {}), indent=2))


if __name__ == "__main__":
    main()
