#!/usr/bin/env python3
"""Extract readable gateway settings from Hilscher SyCon XML BinData blobs.

This script targets:
- EthercatModbusRTUGateway/_S129/SYCON_net.xml

Outputs:
- text report with likely protocol settings and mappings
- decoded UTF-16 XML fragment if present
- decompressed zipped stream (if present)
"""

from __future__ import annotations

import binascii
import re
import zlib
from pathlib import Path

ROOT = Path(r"C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex")
INPUT = ROOT / "external" / "INR_DEV-main" / "platform" / "EFlex" / "firmware" / "EthercatModbusRTUGateway" / "EthercatModbusRTUGateway" / "_S129" / "SYCON_net.xml"
OUTDIR = ROOT / "notes" / "gateway_reverse_engineering"


def decode_bin_hex(xml_text: str) -> bytes:
    m = re.search(r"<BinData[^>]*>([0-9A-Fa-f]+)</BinData>", xml_text, re.S)
    if not m:
        raise RuntimeError("BinData hex block not found")
    hex_blob = re.sub(r"\s+", "", m.group(1))
    return binascii.unhexlify(hex_blob)


def extract_utf16_strings(data: bytes, min_chars: int = 4) -> list[str]:
    # Find runs of printable UTF-16LE text by decoding windows around null-separated bytes.
    out: list[str] = []
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){" + str(min_chars).encode() + rb",}", data):
        try:
            s = m.group(0).decode("utf-16le", errors="ignore")
        except Exception:
            continue
        s = s.strip()
        if s:
            out.append(s)
    # Deduplicate while preserving order.
    seen = set()
    uniq = []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def extract_embedded_xml(data: bytes) -> str | None:
    marker = "<?xml version=\"1.0\"?>".encode("utf-16le")
    i = data.find(marker)
    if i < 0:
        return None
    tail = data[i:]
    # Decode as UTF-16LE and cut at the first trailing null-heavy run.
    txt = tail.decode("utf-16le", errors="ignore")
    # Heuristic end marker for an FDT XML payload.
    end_tag = "</FDT>"
    j = txt.find(end_tag)
    if j >= 0:
        return txt[: j + len(end_tag)]
    return txt


def try_extract_zlib_stream(data: bytes) -> bytes | None:
    # Look for common zlib headers after 'zippedStream' marker.
    idx = data.find(b"zippedStream")
    search_from = idx if idx >= 0 else 0
    for sig in (b"\x78\x01", b"\x78\x9c", b"\x78\xda"):
        i = data.find(sig, search_from)
        if i < 0:
            continue
        chunk = data[i:]
        try:
            return zlib.decompress(chunk)
        except Exception:
            continue
    return None


def find_keywords(text: str, keywords: list[str]) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    hits = []
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in keywords):
            hits.append(ln)
    return hits


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    xml_text = INPUT.read_text(encoding="utf-8", errors="ignore")
    bindata = decode_bin_hex(xml_text)

    (OUTDIR / "bindata_size.txt").write_text(f"BinData bytes: {len(bindata)}\n", encoding="utf-8")

    utf16_strings = extract_utf16_strings(bindata)
    (OUTDIR / "bindata_utf16_strings.txt").write_text("\n".join(utf16_strings), encoding="utf-8")

    embedded_xml = extract_embedded_xml(bindata)
    if embedded_xml:
        (OUTDIR / "embedded_fdt.xml").write_text(embedded_xml, encoding="utf-8")

    decomp = try_extract_zlib_stream(bindata)
    if decomp:
        try:
            # Keep both raw and text decode attempts.
            (OUTDIR / "zipped_stream_decompressed.bin").write_bytes(decomp)
            txt = decomp.decode("utf-8", errors="ignore")
            (OUTDIR / "zipped_stream_decompressed.txt").write_text(txt, encoding="utf-8")
        except Exception:
            pass

    combined = "\n".join(
        [
            embedded_xml or "",
            "\n".join(utf16_strings),
            (decomp.decode("utf-8", errors="ignore") if decomp else ""),
        ]
    )
    keywords = [
        "modbus",
        "rtu",
        "baud",
        "parity",
        "stop",
        "slave",
        "address",
        "register",
        "function",
        "ethercat",
        "mailbox",
    ]
    hits = find_keywords(combined, keywords)
    (OUTDIR / "likely_settings_hits.txt").write_text("\n".join(hits), encoding="utf-8")

    print(f"Wrote outputs to: {OUTDIR}")
    print(f"UTF16 strings: {len(utf16_strings)}")
    print(f"Embedded XML: {'yes' if embedded_xml else 'no'}")
    print(f"Zlib decompressed: {'yes' if decomp else 'no'}")
    print(f"Keyword hits: {len(hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
