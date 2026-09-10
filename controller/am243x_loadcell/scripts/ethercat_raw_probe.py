#!/usr/bin/env python3
"""Raw EtherCAT BRD probe via Scapy/Npcap on Windows.

Sends a broadcast EtherCAT datagram and prints observed replies with source MACs.
Useful to verify whether multiple slaves are visible on the same adapter path.
"""

from __future__ import annotations

import argparse
import binascii
import time
from typing import List

from scapy.all import Ether, Raw, sendp, sniff  # type: ignore

ETH_TYPE_ECAT = 0x88A4


def build_brd_aprd_frame() -> bytes:
    # EtherCAT datagram:
    # cmd=0x07 (BRD), idx=0x01, adp=0x0000, ado=0x0130 (ESC DL status), len=2, irq=0
    # followed by 2-byte data placeholder + 2-byte WKC
    datagram = bytes.fromhex(
        "07 01 00 00 30 01 02 00 00 00 00 00"
    )
    # EtherCAT header: length=12 bytes datagram, type=0
    ecat_header = bytes.fromhex("0C 00")
    return ecat_header + datagram


def parse_wkc_and_data(payload: bytes) -> tuple[int | None, str]:
    # For our fixed datagram, WKC is expected in last 2 bytes
    if len(payload) < 14:
        return None, ""
    data_bytes = payload[-4:-2]
    wkc_bytes = payload[-2:]
    wkc = int.from_bytes(wkc_bytes, "little")
    return wkc, data_bytes.hex()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iface", required=True, help="Npcap interface name, e.g. \\Device\\NPF_{GUID}")
    ap.add_argument("--count", type=int, default=3, help="number of probes")
    ap.add_argument("--timeout", type=float, default=1.0, help="sniff timeout per probe (seconds)")
    args = ap.parse_args()

    payload = build_brd_aprd_frame()
    frame = Ether(dst="ff:ff:ff:ff:ff:ff", type=ETH_TYPE_ECAT) / Raw(load=payload)

    print(f"iface={args.iface}")
    print(f"probe_payload={binascii.hexlify(payload).decode()}")

    for i in range(1, args.count + 1):
        print(f"\nprobe#{i}")
        sendp(frame, iface=args.iface, verbose=False)
        pkts = sniff(
            iface=args.iface,
            timeout=args.timeout,
            filter="ether proto 0x88a4",
            store=True,
        )

        if not pkts:
            print("  no ethercat frames captured")
            continue

        seen: List[str] = []
        for p in pkts:
            try:
                src = p.src
                dst = p.dst
                raw = bytes(p[Raw].load) if Raw in p else b""
                wkc, data_hex = parse_wkc_and_data(raw)
                key = f"{src}->{dst}|wkc={wkc}|data={data_hex}|len={len(raw)}"
                if key in seen:
                    continue
                seen.append(key)
                print(f"  {key}")
            except Exception as exc:
                print(f"  parse_error={exc}")

        time.sleep(0.2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
