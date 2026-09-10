#!/usr/bin/env python3
"""
blink_td_rd_leds.py  --  Force TD/RD LEDs on U-Linx USPTL4 to blink.

Strategy:
  1. Open COM18 at each common baud rate.
  2. Send rapid raw byte blasts  -> TD LED blinks (we're transmitting).
  3. Send valid Modbus RTU frames -> real device might answer  -> RD LED blinks.
  4. Drain any incoming bytes     -> confirms RD path is live.

Usage:
  python blink_td_rd_leds.py [--port COM18] [--rounds 3] [--quiet]
"""
from __future__ import annotations

import argparse
import struct
import sys
import time

import serial

# ── Modbus RTU CRC ─────────────────────────────────────────────────────────

def _crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def modbus_rtu_frame(slave: int, fc: int, start_reg: int, count: int) -> bytes:
    body = struct.pack(">BBHH", slave, fc, start_reg, count)
    crc = _crc16(body)
    return body + struct.pack("<H", crc)


# ── LED blink helpers ──────────────────────────────────────────────────────

BAUDS = [9600, 19200, 38400, 57600, 115200, 4800, 2400]

# Short bursts — just enough to make the LED visibly flash
RAW_BLAST = bytes([0xAA, 0x55] * 20)          # 40 bytes, alternating pattern

# Standard Modbus RTU register reads: FC03, regs 0-4, slaves 1-32
def build_modbus_burst(slaves: range, reg_start: int = 0, reg_count: int = 4) -> list[bytes]:
    frames: list[bytes] = []
    for s in slaves:
        for fc in (3, 4, 1):
            frames.append(modbus_rtu_frame(s, fc, reg_start, reg_count))
    return frames


def blink_at_baud(port: str, baud: int, rounds: int, quiet: bool) -> dict:
    result = {"baud": baud, "tx_bytes": 0, "rx_bytes": 0, "modbus_ok": []}

    try:
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=0.12,        # 120 ms read timeout
            write_timeout=2.0,
        )
    except serial.SerialException as e:
        print(f"  [baud={baud}]  OPEN FAILED: {e}")
        return result

    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        frames = build_modbus_burst(range(1, 33))

        for rnd in range(rounds):
            # ── TX: raw blast first (guarantees TD blink) ───────────────
            ser.write(RAW_BLAST)
            result["tx_bytes"] += len(RAW_BLAST)
            time.sleep(0.01)

            # ── TX: Modbus RTU frames ────────────────────────────────────
            for frame in frames:
                ser.write(frame)
                result["tx_bytes"] += len(frame)

                # Quick read attempt after each frame
                rx = ser.read(8)
                if rx:
                    result["rx_bytes"] += len(rx)
                    # Check if it looks like a valid Modbus response
                    if len(rx) >= 4 and rx[1] == frame[1]:
                        slave_id = rx[0]
                        result["modbus_ok"].append(
                            f"slave={slave_id} fc={rx[1]} data={rx.hex()}"
                        )
                        if not quiet:
                            print(
                                f"  [baud={baud}]  *** MODBUS RESPONSE  "
                                f"slave={slave_id} fc={rx[1]}  raw={rx.hex()}"
                            )

            # Final drain
            leftover = ser.read(64)
            if leftover:
                result["rx_bytes"] += len(leftover)

            if not quiet:
                print(
                    f"  [baud={baud}]  round {rnd+1}/{rounds}  "
                    f"tx={result['tx_bytes']} B  rx={result['rx_bytes']} B"
                )

    finally:
        ser.close()

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Blink U-Linx TD/RD LEDs via rapid serial sends.")
    parser.add_argument("--port", default="COM18", help="COM port (default: COM18)")
    parser.add_argument("--rounds", type=int, default=3, help="Burst rounds per baud (default: 3)")
    parser.add_argument("--bauds", default="", help="Override baud list (comma-sep). Default: all common.")
    parser.add_argument("--quiet", action="store_true", help="Less output per frame")
    args = parser.parse_args()

    bauds = BAUDS
    if args.bauds:
        bauds = [int(b.strip()) for b in args.bauds.split(",") if b.strip()]

    print(f"Target port : {args.port}")
    print(f"Baud rates  : {bauds}")
    print(f"Rounds/baud : {args.rounds}")
    print(f"{'─' * 60}")
    print("Watch the U-Linx box — TD LED should blink at every baud rate.")
    print("If RD LED blinks too, the EEA is responding!\n")

    total_tx = 0
    total_rx = 0
    all_hits: list[str] = []

    for baud in bauds:
        print(f"[baud={baud}]  opening {args.port} ...")
        r = blink_at_baud(args.port, baud, args.rounds, args.quiet)
        total_tx += r["tx_bytes"]
        total_rx += r["rx_bytes"]
        if r["modbus_ok"]:
            all_hits.extend([f"baud={baud} {h}" for h in r["modbus_ok"]])
        print(
            f"[baud={baud}]  done  tx={r['tx_bytes']} B  rx={r['rx_bytes']} B"
            + (f"  HITS={len(r['modbus_ok'])}" if r["modbus_ok"] else "")
        )
        print()

    print(f"{'=' * 60}")
    print(f"Total TX : {total_tx} bytes")
    print(f"Total RX : {total_rx} bytes")

    if all_hits:
        print(f"\n*** MODBUS RESPONSES DETECTED ({len(all_hits)}) ***")
        for h in all_hits:
            print(f"  {h}")
        return 0
    else:
        print("\nNo Modbus responses.  TD should have blinked.  RD did not.")
        print("Next steps:")
        print("  1. Confirm A→A  B→B wiring  (if no TD blink: port/wiring issue)")
        print("  2. If TD blinked but no RD: EEA not responding — check slave ID / baud")
        print("  3. Try --bauds 19200  or  --bauds 9600  focused run")
        print("  4. Swap A/B wires and retry if still nothing")
        return 1


if __name__ == "__main__":
    sys.exit(main())
