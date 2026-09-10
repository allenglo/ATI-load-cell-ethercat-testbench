#!/usr/bin/env python3
"""Search Listary local history for path provenance clues.

Reads:
- %APPDATA%/Listary/UserProfile/Settings/PathHistory.json
- %APPDATA%/Listary/UserProfile/Settings/SearchHistory.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search Listary history")
    parser.add_argument(
        "query",
        nargs="?",
        default="eea|eflex|hilscher|modbus|ethercat|confluence|svn|truenas|\\\\",
        help="Regex to match against path/id/keyword",
    )
    parser.add_argument("--limit", type=int, default=80, help="Max rows to print")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"Version": 0, "Data": []}
    return json.loads(path.read_text(encoding="utf-8"))


def match_rows(rows: list[dict[str, Any]], rx: re.Pattern[str]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        path = str(row.get("Path") or "")
        source = str(row.get("Source") or "")
        keyword = str(row.get("Keyword") or "")

        hk = row.get("HistoryKey") or {}
        hid = str(hk.get("Id") or "")
        hkeyword = str(hk.get("Keyword") or "")
        htype = str(hk.get("Type") or "")

        bag = " | ".join([path, source, keyword, hid, hkeyword, htype])
        if rx.search(bag):
            out.append(row)
    return out


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    hk = row.get("HistoryKey") or {}
    return {
        "time": row.get("Time") or row.get("AccessTime"),
        "path": row.get("Path") or hk.get("Id"),
        "keyword": row.get("Keyword") or hk.get("Keyword"),
        "source": row.get("Source"),
        "type": hk.get("Type"),
    }


def main() -> None:
    args = parse_args()
    rx = re.compile(args.query, re.IGNORECASE)

    appdata = os.environ.get("APPDATA", "")
    settings = Path(appdata) / "Listary" / "UserProfile" / "Settings"

    path_hist = load_json(settings / "PathHistory.json").get("Data", [])
    search_hist = load_json(settings / "SearchHistory.json").get("Data", [])

    path_hits = [normalize_row(r) for r in match_rows(path_hist, rx)]
    search_hits = [normalize_row(r) for r in match_rows(search_hist, rx)]

    combined = sorted(path_hits + search_hits, key=lambda r: str(r.get("time") or ""), reverse=True)
    print(f"matches={len(combined)}")
    for row in combined[: args.limit]:
        print(
            f"{row.get('time')} | {row.get('type') or ''} | "
            f"{row.get('keyword') or ''} | {row.get('path') or ''}"
        )


if __name__ == "__main__":
    main()
