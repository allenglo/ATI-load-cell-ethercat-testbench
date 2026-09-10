#!/usr/bin/env python3
"""EtherCAT bus scanner for Windows (pysoem).

Use this to verify real slave visibility through direct link or switch path.
No hardcoded device assumptions are used unless provided via CLI flags.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from typing import List, Optional

import pysoem


@dataclass
class SlaveInfo:
    index: int
    name: str
    manufacturer_id: int
    product_code: int
    revision: int
    alias: int
    position: int


@dataclass
class AdapterResult:
    adapter_name: str
    adapter_desc: str
    opened: bool
    slave_count: int
    slaves: List[SlaveInfo]
    error: Optional[str]


def _to_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    return int(value, 0)


def discover_on_adapter(adapter_name: str, adapter_desc: str, timeout_us: int) -> AdapterResult:
    master = pysoem.Master()
    try:
        master.open(adapter_name)
        count = master.config_init()
        if count < 0:
            return AdapterResult(
                adapter_name=adapter_name,
                adapter_desc=_to_text(adapter_desc),
                opened=True,
                slave_count=count,
                slaves=[],
                error=f"config_init returned {count}",
            )
        slaves: List[SlaveInfo] = []
        for i, s in enumerate(master.slaves):
            slaves.append(
                SlaveInfo(
                    index=i,
                    name=_to_text(s.name),
                    manufacturer_id=s.man,
                    product_code=s.id,
                    revision=s.rev,
                    alias=getattr(s, "alias", 0),
                    position=getattr(s, "position", i),
                )
            )

        # Optional lightweight process data roundtrip to prove exchange path.
        wkc = None
        if count > 0:
            try:
                master.config_map()
                master.state = pysoem.SAFEOP_STATE
                master.write_state()
                master.state_check(pysoem.SAFEOP_STATE, timeout_us)
                master.send_processdata()
                wkc = master.receive_processdata(timeout_us)
            except Exception:
                # Keep scan robust even if state transition is blocked by one slave.
                wkc = None

        result = AdapterResult(
            adapter_name=adapter_name,
            adapter_desc=_to_text(adapter_desc),
            opened=True,
            slave_count=count,
            slaves=slaves,
            error=None,
        )
        # Attach WKC as dynamic field to keep dataclass concise.
        setattr(result, "wkc", wkc)
        return result
    except Exception as exc:
        return AdapterResult(
            adapter_name=adapter_name,
            adapter_desc=_to_text(adapter_desc),
            opened=False,
            slave_count=0,
            slaves=[],
            error=str(exc),
        )
    finally:
        try:
            master.close()
        except Exception:
            pass


def matches_expectation(
    all_slaves: List[SlaveInfo],
    expect_total: Optional[int],
    expect_ati_man: Optional[int],
    expect_ati_prod: Optional[int],
    expect_name_contains: List[str],
) -> bool:
    if expect_total is not None and len(all_slaves) != expect_total:
        return False

    if expect_ati_man is None and expect_ati_prod is None:
        ati_ok = True
    else:
        ati_ok = False
        for s in all_slaves:
            man_ok = expect_ati_man is None or s.manufacturer_id == expect_ati_man
            prod_ok = expect_ati_prod is None or s.product_code == expect_ati_prod
            if man_ok and prod_ok:
                ati_ok = True
                break

    names_ok = True
    for needle in expect_name_contains:
        needle_l = needle.lower()
        if not any(needle_l in s.name.lower() for s in all_slaves):
            names_ok = False
            break

    return ati_ok and names_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan EtherCAT slaves on available adapters")
    parser.add_argument(
        "--adapter-contains",
        action="append",
        default=[],
        help="Only test adapters whose name/desc contains this text (repeatable)",
    )
    parser.add_argument("--timeout-us", type=int, default=50000, help="SOEM timeout in microseconds")
    parser.add_argument("--expect-total-slaves", type=int, default=None)
    parser.add_argument("--expect-ati-man", type=parse_int, default=None, help="ATI manufacturer ID (dec or 0x)")
    parser.add_argument("--expect-ati-prod", type=parse_int, default=None, help="ATI product code (dec or 0x)")
    parser.add_argument(
        "--expect-name-contains",
        action="append",
        default=[],
        help="Require at least one discovered slave with this substring in name (repeatable)",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    adapters = pysoem.find_adapters()
    if not adapters:
        print("No EtherCAT-capable adapters found by pysoem.")
        return 2

    filters = [x.lower() for x in args.adapter_contains]
    selected = []
    for ad in adapters:
        hay = f"{ad.name} {ad.desc}".lower()
        if not filters or any(f in hay for f in filters):
            selected.append(ad)

    if not selected:
        print("No adapters matched --adapter-contains filters.")
        return 2

    results: List[AdapterResult] = []
    all_slaves: List[SlaveInfo] = []

    for ad in selected:
        res = discover_on_adapter(_to_text(ad.name), _to_text(ad.desc), args.timeout_us)
        results.append(res)
        all_slaves.extend(res.slaves)

    if args.json:
        payload = {
            "timestamp": int(time.time()),
            "results": [asdict(r) for r in results],
            "expectation_passed": matches_expectation(
                all_slaves,
                args.expect_total_slaves,
                args.expect_ati_man,
                args.expect_ati_prod,
                args.expect_name_contains,
            ),
        }
        # include dynamic wkc if present
        for i, r in enumerate(results):
            if hasattr(r, "wkc"):
                payload["results"][i]["wkc"] = getattr(r, "wkc")
        print(json.dumps(payload, indent=2))
    else:
        print("=== EtherCAT Adapter Scan ===")
        for r in results:
            print(f"\nAdapter: {r.adapter_name}")
            print(f"Desc   : {r.adapter_desc}")
            if r.error:
                print(f"Open   : FAIL ({r.error})")
                continue
            print("Open   : OK")
            print(f"Slaves : {r.slave_count}")
            if hasattr(r, "wkc"):
                print(f"WKC    : {getattr(r, 'wkc')}")
            for s in r.slaves:
                print(
                    "  - idx={idx} name='{name}' man=0x{man:08x} prod=0x{prod:08x} rev=0x{rev:08x} alias={alias} pos={pos}".format(
                        idx=s.index,
                        name=s.name,
                        man=s.manufacturer_id,
                        prod=s.product_code,
                        rev=s.revision,
                        alias=s.alias,
                        pos=s.position,
                    )
                )

        ok = matches_expectation(
            all_slaves,
            args.expect_total_slaves,
            args.expect_ati_man,
            args.expect_ati_prod,
            args.expect_name_contains,
        )
        print(f"\nExpectation passed: {ok}")

    has_expectation = (
        args.expect_total_slaves is not None
        or args.expect_ati_man is not None
        or args.expect_ati_prod is not None
        or bool(args.expect_name_contains)
    )
    if has_expectation:
        ok = matches_expectation(
            all_slaves,
            args.expect_total_slaves,
            args.expect_ati_man,
            args.expect_ati_prod,
            args.expect_name_contains,
        )
        return 0 if ok else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
