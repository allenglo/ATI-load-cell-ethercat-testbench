import argparse
import sys
import time

import serial
import serial.tools.list_ports


def list_ports() -> list[serial.tools.list_ports_common.ListPortInfo]:
    return list(serial.tools.list_ports.comports())


def decode_text(data: bytes, clean_text: bool) -> str:
    text = data.decode("utf-8", errors="replace")
    if not clean_text:
        return text

    # Keep common printable ASCII + CR/LF/TAB; replace noisy bytes with '.'
    cleaned = []
    for ch in text:
        o = ord(ch)
        if ch in "\r\n\t" or 32 <= o <= 126:
            cleaned.append(ch)
        else:
            cleaned.append(".")
    return "".join(cleaned)


def pick_auto_port(ports: list[serial.tools.list_ports_common.ListPortInfo]) -> str | None:
    """Prefer XDS110 Application/User UART.  Never grab Auxiliary Data Port
    (used for flashing) unless it is the only port present.
    """
    by_name = {p.device: p for p in ports}

    for p in ports:
        desc = (p.description or "").lower()
        if "application/user uart" in desc:
            return p.device

    # Fall back to first non-auxiliary COM port
    for name in sorted(by_name.keys()):
        desc = (by_name[name].description or "").lower()
        if name.upper().startswith("COM") and "auxiliary data port" not in desc:
            return name

    # Last resort: auxiliary port
    for p in ports:
        desc = (p.description or "").lower()
        if "auxiliary data port" in desc:
            return p.device

    return None


def open_port(port: str, baud: int) -> serial.Serial | None:
    """Try to open port; return None on failure."""
    try:
        ser = serial.Serial(port, baud, timeout=0.2)
        print(f"[uart_monitor] Opened {port} @ {baud} baud", flush=True)
        return ser
    except Exception as exc:
        print(f"[uart_monitor] Cannot open {port}: {exc}", flush=True)
        return None


def run_timed(ser: serial.Serial, seconds: float, raw: bool, clean_text: bool) -> str:
    """Read from an open port for `seconds`; return all text received."""
    all_text = ""
    end_time = time.time() + seconds
    while time.time() < end_time:
        data = ser.read(256)
        if not data:
            continue
        if raw:
            sys.stdout.buffer.write(data)
            sys.stdout.flush()
        else:
            text = decode_text(data, clean_text)
            all_text += text
            sys.stdout.write(text)
            sys.stdout.flush()
    return all_text


def run_follow(port: str, baud: int, raw: bool, retry_interval: float, clean_text: bool) -> int:
    """Continuously read UART; auto-reconnect on any error.  Ctrl-C exits cleanly."""
    print(f"[uart_monitor] Follow mode on {port} (Ctrl-C to stop)", flush=True)
    ser: serial.Serial | None = None
    try:
        while True:
            if ser is None or not ser.is_open:
                # Check current port list to give a friendly message
                current_ports = [p.device for p in list_ports()]
                if port not in current_ports and port.upper() != "AUTO":
                    print(
                        f"[uart_monitor] {port} not visible – waiting {retry_interval}s …",
                        flush=True,
                    )
                    time.sleep(retry_interval)
                    continue
                ser = open_port(port, baud)
                if ser is None:
                    time.sleep(retry_interval)
                    continue

            try:
                data = ser.read(256)
            except Exception as exc:
                print(f"\n[uart_monitor] Read error ({exc}); reconnecting …", flush=True)
                try:
                    ser.close()
                except Exception:
                    pass
                ser = None
                time.sleep(retry_interval)
                continue

            if not data:
                continue

            if raw:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
            else:
                text = decode_text(data, clean_text)
                sys.stdout.write(text)
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n[uart_monitor] Stopped by user.", flush=True)
        if ser and ser.is_open:
            ser.close()
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Read UART output from AM243x LaunchPad")
    parser.add_argument("--port", default="AUTO", help="Serial port (default: AUTO)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--seconds", type=float, default=15.0,
                        help="How long to read in timed mode (ignored with --follow)")
    parser.add_argument("--raw", action="store_true", help="Print raw bytes instead of decoded text")
    parser.add_argument(
        "--no-clean-text",
        action="store_true",
        help="Disable text cleanup (show all decoded replacement chars)",
    )
    parser.add_argument("--follow", action="store_true",
                        help="Run forever, auto-reconnecting when port drops (like tail -f)")
    parser.add_argument("--retry-interval", type=float, default=2.0,
                        help="Seconds between reconnect attempts (--follow mode, default 2.0)")
    parser.add_argument(
        "--expect",
        default="",
        help="If set, exit non-zero unless this text appears in UART output (timed mode only)",
    )
    args = parser.parse_args()

    ports = list_ports()
    port_names = [p.device for p in ports]
    if ports:
        formatted = ", ".join(f"{p.device} [{p.description}]" for p in ports)
    else:
        formatted = "(none)"
    print(f"[uart_monitor] Visible ports: {formatted}", flush=True)

    requested_port = args.port
    if requested_port.upper() == "AUTO":
        auto = pick_auto_port(ports)
        if not auto:
            print("[uart_monitor] ERROR: No suitable COM ports found for AUTO selection")
            return 1
        requested_port = auto
        print(f"[uart_monitor] AUTO selected port: {requested_port}", flush=True)

    selected_info = next((p for p in ports if p.device == requested_port), None)
    if selected_info:
        print(
            f"[uart_monitor] Selected: {selected_info.device} [{selected_info.description}]",
            flush=True,
        )
        desc = (selected_info.description or "").lower()
        if "auxiliary data port" in desc:
            print(
                "[uart_monitor] WARNING: Auxiliary Data Port selected; console text is usually on Application/User UART",
                flush=True,
            )

    # ---- follow (infinite) mode ----
    if args.follow:
        return run_follow(
            requested_port,
            args.baud,
            args.raw,
            args.retry_interval,
            clean_text=(not args.no_clean_text),
        )

    # ---- timed mode ----
    if requested_port not in port_names:
        print(f"[uart_monitor] WARNING: {requested_port} not currently listed, attempting open anyway")

    all_text = ""
    try:
        with serial.Serial(requested_port, args.baud, timeout=0.2) as ser:
            print(f"[uart_monitor] Opened {requested_port} @ {args.baud} baud", flush=True)
            all_text = run_timed(
                ser,
                args.seconds,
                args.raw,
                clean_text=(not args.no_clean_text),
            )
    except Exception as exc:
        print(f"[uart_monitor] ERROR opening/reading {requested_port}: {exc}")
        return 1

    if args.expect:
        if args.expect in all_text:
            print(f"\n[uart_monitor] EXPECT matched: {args.expect}")
        else:
            print(f"\n[uart_monitor] EXPECT not found: {args.expect}")
            print("[uart_monitor] Done reading UART")
            return 2

    print("\n[uart_monitor] Done reading UART")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
