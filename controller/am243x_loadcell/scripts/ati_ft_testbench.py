#!/usr/bin/env python3
"""
Minimal EtherCAT testbench for ATI F/T sensor readouts.

This uses pysoem as EtherCAT master, discovers the ATI slave,
attempts OP-state process-data exchange, and prints raw + decoded channels.
"""

from __future__ import annotations

import argparse
import shutil
import statistics
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pysoem


ATI_VENDOR_ID = 1842
ATI_PRODUCT_CODE = 642265170


@dataclass
class Sample:
    ts: float
    raw: bytes
    channels_i32: Optional[List[int]]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ATI EtherCAT F/T readout testbench")
    p.add_argument(
        "--adapter-contains",
        default="Realtek Gaming USB 2.5GbE",
        help="Substring to select the EtherCAT-capable adapter",
    )
    p.add_argument("--cycles", type=int, default=200, help="Number of cyclic reads")
    p.add_argument("--period-ms", type=float, default=10.0, help="Cycle period in ms")
    p.add_argument("--print-every", type=int, default=1, help="Print every Nth cycle (1=print all)")
    p.add_argument("--timeout-us", type=int, default=50000, help="SOEM timeout in us")
    p.add_argument("--force-scale", type=float, default=1.0, help="Scale for Fx/Fy/Fz")
    p.add_argument("--torque-scale", type=float, default=1.0, help="Scale for Tx/Ty/Tz")
    p.add_argument("--line-log", default="", help="Optional append log file path (one line per sample)")
    p.add_argument("--max-log-lines", type=int, default=300, help="Keep only latest N lines in --line-log")
    p.add_argument("--upload-dir", default="", help="Optional directory to copy latest log snapshot")
    p.add_argument(
        "--name-contains",
        default="ATI EtherCAT F/T Sensor",
        help="Fallback name match if vendor/product match is unavailable",
    )
    p.add_argument("--json", action="store_true", help="Reserved for future use")
    return p.parse_args()


def pick_adapter(substring: str) -> str:
    adapters = pysoem.find_adapters()
    needle = substring.lower()
    for a in adapters:
        joined = f"{a.name} {a.desc}".lower()
        if needle in joined:
            return a.name
    raise RuntimeError(f"No adapter matched: {substring!r}")


def read_identity(slave: pysoem.CdefSlave) -> None:
    print("=== Identity (CoE) ===")
    reads = [
        (0x1008, 0x00, "Device Name"),
        (0x1009, 0x00, "Hardware Version"),
        (0x100A, 0x00, "Software Version"),
        (0x1018, 0x01, "Vendor ID"),
        (0x1018, 0x02, "Product Code"),
        (0x1018, 0x03, "Revision"),
        (0x1018, 0x04, "Serial"),
    ]
    for idx, sub, label in reads:
        try:
            data = slave.sdo_read(idx, sub)
            if idx == 0x1018:
                val = int.from_bytes(data, "little", signed=False)
                print(f"{label:16}: 0x{val:08X} ({val})")
            else:
                text = data.rstrip(b"\x00").decode("utf-8", errors="replace")
                print(f"{label:16}: {text}")
        except Exception as exc:  # noqa: BLE001
            print(f"{label:16}: <read failed: {exc}>")


def decode_channels(raw: bytes) -> Optional[List[int]]:
    # Most ATI PDO layouts expose 6 signed 32-bit channels (Fx, Fy, Fz, Tx, Ty, Tz)
    if len(raw) < 24:
        return None
    try:
        return list(struct.unpack_from("<6i", raw, 0))
    except struct.error:
        return None


def line_for_sample(idx: int, ts: float, wkc: int, decoded: List[int], force_scale: float, torque_scale: float) -> str:
    fx, fy, fz, tx, ty, tz = decoded
    fx_s = fx * force_scale
    fy_s = fy * force_scale
    fz_s = fz * force_scale
    tx_s = tx * torque_scale
    ty_s = ty * torque_scale
    tz_s = tz * torque_scale
    return (
        f"{idx:04d} ts={ts:.3f} wkc={wkc} "
        f"Fx={fx_s:.6f} Fy={fy_s:.6f} Fz={fz_s:.6f} "
        f"Tx={tx_s:.6f} Ty={ty_s:.6f} Tz={tz_s:.6f}"
    )


def trim_log_file(path: Path, keep_lines: int) -> None:
    if keep_lines <= 0 or not path.exists():
        return
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) <= keep_lines:
        return
    path.write_text("\n".join(lines[-keep_lines:]) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    adapter_name = pick_adapter(args.adapter_contains)
    print(f"Adapter: {adapter_name}")

    line_log_path: Optional[Path] = Path(args.line_log) if args.line_log else None
    if line_log_path is not None:
        line_log_path.parent.mkdir(parents=True, exist_ok=True)

    master = pysoem.Master()
    master.open(adapter_name)

    try:
        slave_count = master.config_init()
        if slave_count <= 0:
            raise RuntimeError("No EtherCAT slaves detected")

        print(f"Discovered slaves: {slave_count}")
        ati_slave = None
        for i, s in enumerate(master.slaves):
            print(
                f"[{i}] name={s.name!r} man=0x{s.man:08X} "
                f"prod=0x{s.id:08X} rev=0x{s.rev:08X}"
            )
            if s.man == ATI_VENDOR_ID and s.id == ATI_PRODUCT_CODE:
                ati_slave = s
        if ati_slave is None:
            for s in master.slaves:
                if args.name_contains.lower() in s.name.lower():
                    ati_slave = s
                    break
        if ati_slave is None:
            raise RuntimeError("ATI slave not found on selected adapter")

        read_identity(ati_slave)

        master.config_map()
        master.state = pysoem.SAFEOP_STATE
        master.write_state()
        master.state_check(pysoem.SAFEOP_STATE, args.timeout_us)

        # Prime IO before OP request
        master.send_processdata()
        master.receive_processdata(args.timeout_us)

        master.state = pysoem.OP_STATE
        master.write_state()
        master.state_check(pysoem.OP_STATE, args.timeout_us)
        print(f"Master state after OP request: 0x{master.state:02X}")

        samples: List[Sample] = []
        period_s = max(args.period_ms / 1000.0, 0.001)
        print("=== Cyclic Readout ===")
        for i in range(args.cycles):
            t0 = time.time()
            master.send_processdata()
            wkc = master.receive_processdata(args.timeout_us)
            raw = bytes(ati_slave.input)
            decoded = decode_channels(raw)
            samples.append(Sample(ts=t0, raw=raw, channels_i32=decoded))

            if args.print_every > 0 and (i + 1) % args.print_every == 0:
                prefix = raw[:32].hex(" ")
                if decoded is None:
                    print(f"#{i+1:03d} wkc={wkc} in_len={len(raw)} raw[0:32]={prefix}")
                else:
                    line = line_for_sample(
                        i + 1,
                        t0,
                        wkc,
                        decoded,
                        args.force_scale,
                        args.torque_scale,
                    )
                    print(line)
                    if line_log_path is not None:
                        with line_log_path.open("a", encoding="utf-8") as f:
                            f.write(line + "\n")

            elapsed = time.time() - t0
            if elapsed < period_s:
                time.sleep(period_s - elapsed)

        decoded_samples = [s.channels_i32 for s in samples if s.channels_i32 is not None]
        print("=== Summary ===")
        print(f"Samples collected: {len(samples)}")
        print(f"Decoded channel samples: {len(decoded_samples)}")
        if decoded_samples:
            cols = list(zip(*decoded_samples))
            names = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
            for name, col in zip(names, cols):
                print(
                    f"{name}: min={min(col)} max={max(col)} mean={statistics.fmean(col):.2f}"
                )
        else:
            print("No 6xint32 decode available from current PDO payload.")

        if line_log_path is not None:
            trim_log_file(line_log_path, args.max_log_lines)
            print(f"Log file updated: {line_log_path}")
            if args.upload_dir:
                upload_dir = Path(args.upload_dir)
                upload_dir.mkdir(parents=True, exist_ok=True)
                dst = upload_dir / "ati_ft_latest.log"
                shutil.copy2(line_log_path, dst)
                print(f"Uploaded latest log snapshot: {dst}")

        return 0
    finally:
        try:
            master.state = pysoem.INIT_STATE
            master.write_state()
        except Exception:  # noqa: BLE001
            pass
        master.close()


if __name__ == "__main__":
    raise SystemExit(main())
