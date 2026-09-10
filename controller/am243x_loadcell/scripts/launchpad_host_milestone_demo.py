#!/usr/bin/env python3
"""
Demoable milestone script for the LaunchPad-host firmware lane.

Purpose:
- Keep USB-Ethernet+pysoem as a debug validator.
- Emit firmware-style one-line force/torque output that matches planned COM10 format.
- Write a concise run report for future agents.
"""

from __future__ import annotations

import argparse
import datetime as dt
import random
import statistics
import struct
import time
from pathlib import Path
from typing import List, Optional

try:
    import pysoem
except Exception:
    pysoem = None


ATI_VENDOR_ID = 1842
ATI_PRODUCT_CODE = 642265170


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LaunchPad-host milestone demo (live or mock)")
    p.add_argument("--mode", choices=["auto", "live", "mock"], default="auto")
    p.add_argument("--adapter-contains", default="Realtek Gaming USB 2.5GbE")
    p.add_argument("--cycles", type=int, default=20)
    p.add_argument("--period-ms", type=float, default=10.0)
    p.add_argument("--force-scale", type=float, default=1e-6)
    p.add_argument("--torque-scale", type=float, default=1e-6)
    p.add_argument("--report-dir", default="../reports/host_master")
    return p.parse_args()


def pick_adapter(substring: str) -> str:
    assert pysoem is not None
    adapters = pysoem.find_adapters()
    needle = substring.lower()
    for a in adapters:
        joined = f"{a.name} {a.desc}".lower()
        if needle in joined:
            return a.name
    raise RuntimeError(f"No adapter matched: {substring!r}")


def decode_channels(raw: bytes) -> Optional[List[int]]:
    if len(raw) < 24:
        return None
    try:
        return list(struct.unpack_from("<6i", raw, 0))
    except struct.error:
        return None


def line_for_sample(idx: int, ts: float, wkc: int, vals: List[int], force_scale: float, torque_scale: float) -> str:
    fx, fy, fz, tx, ty, tz = vals
    return (
        f"LP_HOST_DEMO n={idx:04d} ts={ts:.3f} wkc={wkc} "
        f"Fx={fx * force_scale:.6f} Fy={fy * force_scale:.6f} Fz={fz * force_scale:.6f} "
        f"Tx={tx * torque_scale:.6f} Ty={ty * torque_scale:.6f} Tz={tz * torque_scale:.6f}"
    )


def run_mock(args: argparse.Namespace) -> tuple[list[str], str]:
    lines: list[str] = []
    seed = 2430
    random.seed(seed)
    base = [600000, -120000, 80000, 10000, -9000, 7000]

    for i in range(1, args.cycles + 1):
        jitter = [random.randint(-1200, 1200) for _ in range(6)]
        vals = [base[k] + jitter[k] for k in range(6)]
        line = line_for_sample(i, time.time(), 3, vals, args.force_scale, args.torque_scale)
        print(line)
        lines.append(line)
        time.sleep(max(args.period_ms / 1000.0, 0.001))

    return lines, "mock"


def run_live(args: argparse.Namespace) -> tuple[list[str], str]:
    if pysoem is None:
        raise RuntimeError("pysoem not available in this Python environment")

    lines: list[str] = []
    adapter_name = pick_adapter(args.adapter_contains)
    print(f"Using adapter: {adapter_name}")

    master = pysoem.Master()
    master.open(adapter_name)
    try:
        slave_count = master.config_init()
        if slave_count <= 0:
            raise RuntimeError("No EtherCAT slaves detected")

        ati_slave = None
        for s in master.slaves:
            if s.man == ATI_VENDOR_ID and s.id == ATI_PRODUCT_CODE:
                ati_slave = s
                break
        if ati_slave is None:
            raise RuntimeError("ATI slave not found")

        master.config_map()
        master.state = pysoem.SAFEOP_STATE
        master.write_state()
        master.state_check(pysoem.SAFEOP_STATE, 50000)
        master.send_processdata()
        master.receive_processdata(50000)
        master.state = pysoem.OP_STATE
        master.write_state()
        master.state_check(pysoem.OP_STATE, 50000)

        period_s = max(args.period_ms / 1000.0, 0.001)
        for i in range(1, args.cycles + 1):
            t0 = time.time()
            master.send_processdata()
            wkc = master.receive_processdata(50000)
            raw = bytes(ati_slave.input)
            vals = decode_channels(raw)
            if vals is None:
                continue
            line = line_for_sample(i, t0, wkc, vals, args.force_scale, args.torque_scale)
            print(line)
            lines.append(line)
            elapsed = time.time() - t0
            if elapsed < period_s:
                time.sleep(period_s - elapsed)

        return lines, "live"
    finally:
        try:
            master.state = pysoem.INIT_STATE
            master.write_state()
        except Exception:
            pass
        master.close()


def write_report(report_dir: Path, mode_used: str, lines: list[str], args: argparse.Namespace) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = report_dir / f"MILESTONE_01_DEMO_{ts}.md"

    decoded_count = len(lines)
    sample_tail = lines[-1] if lines else "<no decoded sample>"

    forces = []
    torques = []
    for line in lines:
        parts = line.split()
        kv = {p.split("=", 1)[0]: p.split("=", 1)[1] for p in parts if "=" in p}
        try:
            forces.extend([float(kv["Fx"]), float(kv["Fy"]), float(kv["Fz"])])
            torques.extend([float(kv["Tx"]), float(kv["Ty"]), float(kv["Tz"])])
        except Exception:
            continue

    force_mean = statistics.fmean(forces) if forces else 0.0
    torque_mean = statistics.fmean(torques) if torques else 0.0

    text = "\n".join(
        [
            "# Milestone 01 Demo Report",
            "",
            "Goal:",
            "- Demonstrate firmware-style one-line F/T stream format for LaunchPad host lane.",
            "",
            f"Mode used: {mode_used}",
            f"Cycles requested: {args.cycles}",
            f"Decoded lines: {decoded_count}",
            f"Mean force value (all Fx/Fy/Fz pooled): {force_mean:.6f}",
            f"Mean torque value (all Tx/Ty/Tz pooled): {torque_mean:.6f}",
            "",
            "Last sample:",
            f"- {sample_tail}",
            "",
            "Next step:",
            "- Keep this output contract when moving to COM10 firmware print path.",
        ]
    )

    out.write_text(text + "\n", encoding="utf-8")
    return out


def main() -> int:
    args = parse_args()
    report_dir = (Path(__file__).resolve().parent / args.report_dir).resolve()

    mode_used = args.mode
    lines: list[str]

    if args.mode == "mock":
        lines, mode_used = run_mock(args)
    elif args.mode == "live":
        lines, mode_used = run_live(args)
    else:
        # auto mode: try live first, fall back to mock so milestone is always demoable
        try:
            lines, mode_used = run_live(args)
        except Exception as exc:
            print(f"LIVE mode unavailable ({exc}); falling back to mock mode")
            lines, mode_used = run_mock(args)

    report_path = write_report(report_dir, mode_used, lines, args)
    print(f"Milestone report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
