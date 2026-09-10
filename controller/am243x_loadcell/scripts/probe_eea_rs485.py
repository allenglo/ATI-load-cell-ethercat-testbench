#!/usr/bin/env python3
"""Quick Modbus RTU probe for EEA/U-Linx RS485 bring-up.

This script:
- Lists serial ports and filters likely USB/RS485 adapters.
- Tries Modbus RTU register reads over configurable baud/slave ranges.
- Prints a compact success/failure report for first-link validation.

Default assumptions come from local notes:
- RS485 2-wire half-duplex on TDA/TDB
- 8N1
- Typical baud: 9600 or 19200
"""

from __future__ import annotations

import argparse
import itertools
import sys
from dataclasses import dataclass
from typing import Iterable

import minimalmodbus
import serial.tools.list_ports


@dataclass
class ProbeAttempt:
    port: str
    baud: int
    slave_id: int
    register: int
    function_code: int
    ok: bool
    value: int | None
    error: str | None


def parse_int_list(spec: str) -> list[int]:
    values: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start = int(a)
            end = int(b)
            step = 1 if end >= start else -1
            values.extend(range(start, end + step, step))
        else:
            values.append(int(part))
    deduped = sorted(set(values))
    if not deduped:
        raise ValueError("No values parsed from list specification")
    return deduped


def score_port(description: str, hwid: str) -> int:
    text = f"{description} {hwid}".lower()
    score = 0
    if "usb" in text:
        score += 2
    if "ftdi" in text or "cp210" in text or "ch340" in text or "pl2303" in text:
        score += 4
    if "rs485" in text or "serial" in text:
        score += 2
    if "bluetooth" in text:
        score -= 4
    if "intel(r) active management technology" in text:
        score -= 5
    return score


def find_candidate_ports(force_ports: list[str] | None = None) -> list[str]:
    if force_ports:
        return force_ports

    ports = list(serial.tools.list_ports.comports())
    ranked: list[tuple[int, str]] = []
    for p in ports:
        ranked.append((score_port(p.description, p.hwid), p.device))

    ranked.sort(reverse=True)
    # Keep only non-negative score ports by default; if none, return all.
    best = [dev for score, dev in ranked if score >= 0]
    if best:
        return best
    return [p.device for p in ports]


def list_ports() -> None:
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No COM ports found.")
        return
    print("Detected COM ports:")
    for p in ports:
        s = score_port(p.description, p.hwid)
        print(f"  {p.device:7} score={s:2d}  {p.description}  [{p.hwid}]")


def iter_attempts(
    ports: Iterable[str],
    bauds: list[int],
    slave_ids: list[int],
    registers: list[int],
    function_codes: list[int],
    timeout_s: float,
) -> Iterable[ProbeAttempt]:
    for port, baud, slave_id, reg, fc in itertools.product(ports, bauds, slave_ids, registers, function_codes):
        try:
            ins = minimalmodbus.Instrument(port, slave_id)
            ins.serial.baudrate = baud
            ins.serial.bytesize = 8
            ins.serial.parity = serial.PARITY_NONE
            ins.serial.stopbits = 1
            ins.serial.timeout = timeout_s
            ins.mode = minimalmodbus.MODE_RTU
            value = ins.read_register(reg, number_of_decimals=0, functioncode=fc, signed=False)
            yield ProbeAttempt(port, baud, slave_id, reg, fc, True, int(value), None)
            continue
        except Exception as exc:
            yield ProbeAttempt(port, baud, slave_id, reg, fc, False, None, str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe EEA RS485 Modbus RTU connectivity")
    parser.add_argument("--ports", default="", help="Comma-separated ports, e.g. COM11,COM12")
    parser.add_argument("--baud", default="9600,19200", help="Baud list/ranges, e.g. 9600,19200")
    parser.add_argument("--slave-ids", default="1-8", help="Slave ID list/ranges, e.g. 1-8")
    parser.add_argument("--registers", default="0,1", help="Register list/ranges to try")
    parser.add_argument("--function-codes", default="3,4", help="Function codes to try (3 or 4)")
    parser.add_argument("--timeout", type=float, default=0.25, help="Serial timeout in seconds")
    parser.add_argument("--list-only", action="store_true", help="Only list ports and exit")
    args = parser.parse_args()

    list_ports()
    if args.list_only:
        return 0

    force_ports = [p.strip() for p in args.ports.split(",") if p.strip()] if args.ports else None
    try:
        bauds = parse_int_list(args.baud)
        slave_ids = parse_int_list(args.slave_ids)
        registers = parse_int_list(args.registers)
        function_codes = parse_int_list(args.function_codes)
    except ValueError as exc:
        print(f"Invalid list argument: {exc}")
        return 2

    ports = find_candidate_ports(force_ports)
    if not ports:
        print("No candidate ports to probe.")
        return 3

    print("\nProbe plan:")
    print(f"  Ports        : {', '.join(ports)}")
    print(f"  Baud         : {bauds}")
    print(f"  Slave IDs    : {slave_ids}")
    print(f"  Registers    : {registers}")
    print(f"  FunctionCode : {function_codes}")
    print(f"  Timeout (s)  : {args.timeout}")

    total = 0
    success = 0
    first_hits: list[ProbeAttempt] = []

    for a in iter_attempts(ports, bauds, slave_ids, registers, function_codes, args.timeout):
        total += 1
        if a.ok:
            success += 1
            first_hits.append(a)
            print(
                f"[OK] port={a.port} baud={a.baud} id={a.slave_id} reg={a.register} fc={a.function_code} value={a.value}"
            )
            if success >= 5:
                break
        else:
            # Keep output readable; only print first error per tuple group is enough in practice.
            if total <= 20:
                print(
                    f"[NO] port={a.port} baud={a.baud} id={a.slave_id} reg={a.register} fc={a.function_code} err={a.error}"
                )

    print("\nSummary:")
    print(f"  Attempts : {total}")
    print(f"  Success  : {success}")

    if first_hits:
        print("  Result   : Modbus response detected")
        return 0

    print("  Result   : No Modbus response detected")
    print("  Hint     : Verify U-Linx driver/port, RS485 polarity (A/B), and slave ID/baud.")
    return 4


if __name__ == "__main__":
    sys.exit(main())
