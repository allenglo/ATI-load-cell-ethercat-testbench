#!/usr/bin/env python3
import argparse
import serial
import serial.rs485
import time

PARITY_MAP = {0: serial.PARITY_NONE, 1: serial.PARITY_EVEN, 2: serial.PARITY_ODD}


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


def make_read_frame(slave: int, reg: int, count: int) -> bytes:
    import struct
    p = struct.pack('>B B H H', slave, 3, reg, count)
    return p + crc16(p)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', default='COM18')
    p.add_argument('--baud', type=int, default=115200)
    p.add_argument('--parity', type=int, default=1, help='0=None,1=Even,2=Odd')
    p.add_argument('--stopbits', type=int, default=1, help='1 or 2')
    p.add_argument('--slave', type=int, default=10)
    p.add_argument('--reg', type=int, default=0)
    p.add_argument('--count', type=int, default=8)
    p.add_argument('--timeout', type=float, default=0.2)
    p.add_argument('--rts', type=int, default=1, help='RTS control: 1 enable DE/RE toggle')
    args = p.parse_args()

    parity = PARITY_MAP.get(args.parity, serial.PARITY_EVEN)
    stopbits = serial.STOPBITS_ONE if args.stopbits == 1 else serial.STOPBITS_TWO

    ser = serial.Serial()
    ser.port = args.port
    ser.baudrate = args.baud
    ser.parity = parity
    ser.stopbits = stopbits
    ser.bytesize = serial.EIGHTBITS
    ser.timeout = args.timeout

    # configure RS485 driver toggling if available
    try:
        rs = serial.rs485.RS485Settings(rts_level_for_tx=True, rts_level_for_rx=False, delay_before_tx=None, delay_before_rx=None)
        ser.rs485_mode = rs
    except Exception:
        # older pyserial may require setting after open
        pass

    print(f'Opening {args.port} @ {args.baud} parity={parity} stopbits={args.stopbits} rs485_rts={args.rts}')
    ser.open()

    # some platforms require setting rs485_mode after open
    try:
        ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=True, rts_level_for_rx=False, delay_before_tx=None, delay_before_rx=None)
    except Exception:
        pass

    frame = make_read_frame(args.slave, args.reg, args.count)
    print('TX:', frame.hex())
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(frame)
    ser.flush()
    time.sleep(0.05)
    rx = ser.read(256)
    print('RX len:', len(rx))
    if rx:
        print('RX hex:', rx.hex())
    else:
        print('No response')
    ser.close()
