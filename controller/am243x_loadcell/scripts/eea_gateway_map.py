#!/usr/bin/env python3
"""Utilities for EEA EtherCAT<->serial gateway process image mapping.

Source of truth:
- ecatms_sys_X44_usr_config.xml from INR_DEV FileArchive
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


DEFAULT_ECATMS_PATH = Path(
    r"C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\external\INR_DEV-main\platform\EFlex\krc5_eflex\src\eflex\FileArchive\DeviceControllers#KR C5 micro\ExternalFiles\Config\User\Common\ecatms_sys_X44_usr_config.xml"
)

# Absolute process-image base offsets for the gateway slave (from ecatms XML ProcessData entries).
# pysoem slave.output / slave.input start at local byte 0, which maps to these global bit positions.
PDO_OUTPUT_BASE_BIT: int = 208   # Gateway Send PDO start  (length 320 bits  = 40 bytes)
PDO_INPUT_BASE_BIT: int = 688    # Gateway Receive PDO start (length 672 bits = 84 bytes)


@dataclass(frozen=True)
class ProcessVar:
    direction: str  # "inputs" or "outputs"
    name: str
    data_type: str
    bit_size: int
    bit_offs: int


@dataclass(frozen=True)
class DecodedGeneralInfo:
    designator: int
    fw_part_num: int
    fw_part_rev: int
    fw_build_num: int


def _iter_vars(root: ET.Element, direction: str) -> Iterable[ProcessVar]:
    section_name = "Inputs" if direction == "inputs" else "Outputs"
    section = root.find(f".//ProcessImage/{section_name}")
    if section is None:
        return
    for var in section.findall("Variable"):
        name = (var.findtext("Name") or "").strip()
        if "EFlexEthercatModbusRTUGateway." not in name:
            continue
        yield ProcessVar(
            direction=direction,
            name=name,
            data_type=(var.findtext("DataType") or "").strip(),
            bit_size=int(var.findtext("BitSize") or "0"),
            bit_offs=int(var.findtext("BitOffs") or "0"),
        )


def load_gateway_process_map(ecatms_path: Path = DEFAULT_ECATMS_PATH) -> list[ProcessVar]:
    tree = ET.parse(ecatms_path)
    root = tree.getroot()
    vars_in = list(_iter_vars(root, "inputs"))
    vars_out = list(_iter_vars(root, "outputs"))
    all_vars = vars_in + vars_out
    all_vars.sort(key=lambda v: (v.direction, v.bit_offs, v.name))
    return all_vars


def decode_general_info(gen_info: int) -> DecodedGeneralInfo:
    return DecodedGeneralInfo(
        designator=(gen_info & 0x1000) >> 12,
        fw_part_num=(gen_info & 0x0F00) >> 8,
        fw_part_rev=(gen_info & 0x00F0) >> 4,
        fw_build_num=(gen_info & 0x000F),
    )


def decode_led_brightness_blink(value: int) -> tuple[int, int]:
    brightness = (value & 0xF0) >> 4
    blink_period_code = value & 0x0F
    return brightness, blink_period_code


def _read_unsigned_le(buf: bytes, bit_offs: int, bit_size: int) -> int:
    if bit_offs % 8 != 0:
        raise ValueError(f"Unsupported non-byte-aligned field at bit offset {bit_offs}")
    if bit_size % 8 != 0:
        raise ValueError(f"Unsupported non-byte-sized field size {bit_size}")
    byte_offs = bit_offs // 8
    byte_len = bit_size // 8
    raw = buf[byte_offs : byte_offs + byte_len]
    if len(raw) != byte_len:
        return 0
    return int.from_bytes(raw, byteorder="little", signed=False)


def decode_process_image(
    pdo_bytes: bytes,
    process_vars: list[ProcessVar],
    direction: str,
) -> dict[str, int]:
    """Decode a slave PDO buffer into a field map.

    pdo_bytes must be the raw slave.input or slave.output from pysoem, which
    starts at local byte 0 corresponding to PDO_INPUT_BASE_BIT / PDO_OUTPUT_BASE_BIT
    in the global process image.  We subtract the base so bit_offs becomes local.
    """
    base = PDO_INPUT_BASE_BIT if direction == "inputs" else PDO_OUTPUT_BASE_BIT
    out: dict[str, int] = {}
    for var in process_vars:
        if var.direction != direction:
            continue
        local_bit_offs = var.bit_offs - base
        if local_bit_offs < 0:
            continue
        out[var.name] = _read_unsigned_le(pdo_bytes, local_bit_offs, var.bit_size)
    return out


def encode_process_image(
    field_values: dict[str, int],
    process_vars: list[ProcessVar],
) -> bytes:
    """Pack a field map into a slave output PDO byte array (local offsets).

    Returns a bytearray sized to hold all output fields.
    """
    base = PDO_OUTPUT_BASE_BIT
    # Determine size needed
    max_bit = max(
        (v.bit_offs - base + v.bit_size)
        for v in process_vars
        if v.direction == "outputs"
    )
    buf = bytearray((max_bit + 7) // 8)
    for var in process_vars:
        if var.direction != "outputs":
            continue
        local_bit = var.bit_offs - base
        if local_bit < 0:
            continue
        if var.bit_size % 8 != 0 or local_bit % 8 != 0:
            continue  # non-byte-aligned; skip for now
        byte_off = local_bit // 8
        byte_len = var.bit_size // 8
        val = field_values.get(var.name, 0) & ((1 << var.bit_size) - 1)
        buf[byte_off : byte_off + byte_len] = val.to_bytes(byte_len, "little")
    return bytes(buf)


if __name__ == "__main__":
    vars_map = load_gateway_process_map()
    print(f"Loaded {len(vars_map)} gateway process-image variables")
    print("First 15:")
    for row in vars_map[:15]:
        print(f"- {row.direction:7s} {row.bit_offs:4d} {row.bit_size:3d} {row.data_type:7s} {row.name}")
