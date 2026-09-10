#!/usr/bin/env python3
"""Simple read-only Modbus monitor for the EEA device.

Polls FC=4 (input registers) and FC=3 (holding registers) for slave 1 over RS485
and prints parsed unsigned 16-bit register values. Non-destructive.
"""
from __future__ import annotations

import struct
import time
from datetime import datetime
import serial
import serial.rs485


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


def make_frame(slave: int, fc: int, reg: int, count: int) -> bytes:
    return struct.pack(
        ">B B H H", slave, fc, reg, count
    ) + crc16(struct.pack(
        ">B B H H", slave, fc, reg, count
    ))


def parse_registers_from_reply(rx: bytes) -> list[int] | None:
    if not rx or len(rx) < 5:
        return None
    # standard reply: addr, fc, bytecount, data..., crc_lo, crc_hi
    bytecount = rx[2]
    data = rx[3 : 3 + bytecount]
    regs = []
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            regs.append((data[i] << 8) | data[i + 1])
    return regs


def monitor_once(ser, slave=1, fc=4, reg_start=0, count=4):
    frame = make_frame(slave, fc, reg_start, count)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(frame)
    ser.flush()
    time.sleep(0.04)
    rx = ser.read(512)
    return rx


def main():
    port = "COM18"
    baud = 115200
    parity = serial.PARITY_EVEN
    ser = serial.Serial(port=port, baudrate=baud, parity=parity, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.2)
    try:
        ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=True, rts_level_for_rx=False, delay_before_tx=None, delay_before_rx=None)
    except Exception:
        pass
    ser.open()

    slave = 1
    try:
        for cycle in range(10):
            t = datetime.utcnow().isoformat() + "Z"
            # poll FC4 registers 0..3
            rx = monitor_once(ser, slave=slave, fc=4, reg_start=0, count=4)
            regs = parse_registers_from_reply(rx)
            print(f"{t} Slave={slave} FC=4 regs0..3 -> {regs} raw={rx.hex()}")
            # poll FC3 registers 0..3
            rx2 = monitor_once(ser, slave=slave, fc=3, reg_start=0, count=4)
            regs2 = parse_registers_from_reply(rx2)
            print(f"{t} Slave={slave} FC=3 regs0..3 -> {regs2} raw={rx2.hex()}")
            time.sleep(0.5)
    finally:
        ser.close()


if __name__ == "__main__":
    main()
