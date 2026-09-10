#!/usr/bin/env python3
"""
Rapid trial-and-error Modbus RTU comms against EEA via COM port.
- Cycles baud/parity/stop-bit combinations.
- Tries likely slave IDs and likely registers from gateway mapping.
- Sends both read and write requests.
- Logs every response byte stream to a file.
"""

from __future__ import annotations

import argparse
import datetime as dt
import struct
import time
from pathlib import Path

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


def add_crc(pdu: bytes) -> bytes:
    c = crc16_modbus(pdu)
    return pdu + struct.pack("<H", c)


def frame_fc03_or_fc04(slave: int, fc: int, reg: int, count: int) -> bytes:
    return add_crc(struct.pack(">BBHH", slave, fc, reg, count))


def frame_fc06(slave: int, reg: int, value: int) -> bytes:
    return add_crc(struct.pack(">BBHH", slave, 6, reg, value & 0xFFFF))


def frame_fc16(slave: int, reg: int, values: list[int]) -> bytes:
    count = len(values)
    body = struct.pack(">BBHHB", slave, 16, reg, count, count * 2)
    for v in values:
        body += struct.pack(">H", v & 0xFFFF)
    return add_crc(body)


def looks_like_modbus_reply(req: bytes, resp: bytes) -> bool:
    if len(resp) < 5:
        return False
    if crc16_modbus(resp[:-2]) != struct.unpack("<H", resp[-2:])[0]:
        return False
    if resp[0] != req[0]:
        return False
    if resp[1] not in (req[1], req[1] | 0x80):
        return False
    return True


def build_requests(slave: int) -> list[tuple[str, bytes]]:
    reqs: list[tuple[str, bytes]] = []

    # Reads: likely map points from extracted gateway config.
    for fc in (3, 4):
        reqs.append((f"FC{fc} reg0 cnt8", frame_fc03_or_fc04(slave, fc, 0, 8)))
        reqs.append((f"FC{fc} reg3 cnt7", frame_fc03_or_fc04(slave, fc, 3, 7)))
        reqs.append((f"FC{fc} reg6 cnt4", frame_fc03_or_fc04(slave, fc, 6, 4)))
        reqs.append((f"FC{fc} reg2880 cnt1", frame_fc03_or_fc04(slave, fc, 2880, 1)))
        reqs.append((f"FC{fc} reg2880 cnt4", frame_fc03_or_fc04(slave, fc, 2880, 4)))

    # Writes: register 6 is frequently used in mapping for outputs.
    for val in (0, 1, 2, 3, 0x00FF, 0x0F0F, 0x1234, 0xFFFF):
        reqs.append((f"FC06 reg6 val{val}", frame_fc06(slave, 6, val)))

    reqs.append(("FC16 reg6 [1,2,3,4]", frame_fc16(slave, 6, [1, 2, 3, 4])))
    reqs.append(("FC16 reg6 [255,0,255,0]", frame_fc16(slave, 6, [255, 0, 255, 0])))
    reqs.append(("FC16 reg6 [4660,22136,0,65535]", frame_fc16(slave, 6, [0x1234, 0x5678, 0, 0xFFFF])))

    return reqs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM18")
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    bauds = [115200, 57600, 38400, 19200, 9600]
    parities = [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD]
    stopbits = [serial.STOPBITS_ONE, serial.STOPBITS_TWO]
    slaves = [1, 2, 3, 4, 10]

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(args.out) if args.out else Path(f"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/logs/eea_trial_{stamp}.log")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tx_total = 0
    rx_total = 0
    valid_modbus = 0

    with out_path.open("w", encoding="utf-8") as log:
        log.write(f"Start: {dt.datetime.now().isoformat()}\n")
        log.write(f"Port={args.port} rounds={args.rounds}\n")

        for baud in bauds:
            for parity in parities:
                for sb in stopbits:
                    profile = f"baud={baud} parity={parity} stop={1 if sb == serial.STOPBITS_ONE else 2}"
                    print(f"\\n[PROFILE] {profile}")
                    log.write(f"\n[PROFILE] {profile}\n")

                    try:
                        ser = serial.Serial(
                            port=args.port,
                            baudrate=baud,
                            bytesize=serial.EIGHTBITS,
                            parity=parity,
                            stopbits=sb,
                            timeout=0.10,
                            write_timeout=0.8,
                        )
                    except Exception as e:
                        print(f"  open failed: {e}")
                        log.write(f"  open failed: {e}\n")
                        continue

                    try:
                        ser.reset_input_buffer()
                        ser.reset_output_buffer()

                        # Kick line with obvious pulse pattern.
                        raw = bytes([0x55, 0xAA] * 40)
                        ser.write(raw)
                        tx_total += len(raw)
                        time.sleep(0.01)

                        for _ in range(args.rounds):
                            for s in slaves:
                                for label, req in build_requests(s):
                                    try:
                                        ser.write(req)
                                        tx_total += len(req)
                                    except Exception:
                                        continue

                                    resp = ser.read(64)
                                    if resp:
                                        rx_total += len(resp)
                                        ok = looks_like_modbus_reply(req, resp)
                                        if ok:
                                            valid_modbus += 1

                                        line = (
                                            f"{dt.datetime.now().isoformat()} {profile} "
                                            f"slave={s} {label} req={req.hex()} resp={resp.hex()} "
                                            f"valid_modbus={ok}"
                                        )
                                        print("  RX", line)
                                        log.write(line + "\n")

                            # Drain between sweeps.
                            tail = ser.read(128)
                            if tail:
                                rx_total += len(tail)
                                line = f"{dt.datetime.now().isoformat()} {profile} tail={tail.hex()}"
                                print("  RX", line)
                                log.write(line + "\n")

                    finally:
                        ser.close()

        summary = (
            f"\nDone tx_total={tx_total} rx_total={rx_total} "
            f"valid_modbus={valid_modbus} log={out_path}\n"
        )
        print(summary)
        log.write(summary)

    return 0 if rx_total > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
