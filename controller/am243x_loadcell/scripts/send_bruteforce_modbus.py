#!/usr/bin/env python3
import serial
import serial.rs485
import time
import struct

PARITY_MAP = {0: serial.PARITY_NONE, 1: serial.PARITY_EVEN, 2: serial.PARITY_ODD}
STOP_MAP = {1: serial.STOPBITS_ONE, 2: serial.STOPBITS_TWO}


def crc16_bytes(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def valid_modbus_response(resp: bytes) -> bool:
    if len(resp) < 5:
        return False
    # CRC check
    data, crc = resp[:-2], resp[-2:]
    calc = crc16_bytes(data)
    recv = int.from_bytes(crc, 'little')
    return calc == recv


def make_read(slave, reg, count):
    p = struct.pack('>B B H H', slave, 3, reg, count)
    crc = crc16_bytes(p)
    return p + crc.to_bytes(2, 'little')


if __name__ == '__main__':
    port = 'COM18'
    bauds = [115200]
    parities = [0,1,2]
    stops = [1,2]
    slaves = [1,2,3,4,10]
    regs = [0,3,6,2880]
    rts_modes = ['rs485_true', 'rs485_false', 'manual', 'none']
    timeout = 0.15

    found = []
    total = 0
    for baud in bauds:
        for parity in parities:
            for stop in stops:
                for rts_mode in rts_modes:
                    for slave in slaves:
                        for reg in regs:
                            total += 1
    print(f'Trying {total} combinations')

    attempt = 0
    for baud in bauds:
        for parity in parities:
            for stop in stops:
                for rts_mode in rts_modes:
                    for slave in slaves:
                        for reg in regs:
                            attempt += 1
                            print(f'[{attempt}/{total}] baud={baud} parity={parity} stop={stop} rts={rts_mode} slave={slave} reg={reg}')
                            ser = serial.Serial()
                            ser.port = port
                            ser.baudrate = baud
                            ser.parity = PARITY_MAP[parity]
                            ser.stopbits = STOP_MAP[stop]
                            ser.bytesize = serial.EIGHTBITS
                            ser.timeout = timeout
                            try:
                                ser.open()
                            except Exception as e:
                                print('open failed', e)
                                time.sleep(0.05)
                                continue

                            # configure rs485 when possible
                            if rts_mode.startswith('rs485'):
                                try:
                                    lvl = True if rts_mode == 'rs485_true' else False
                                    ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=lvl, rts_level_for_rx=(not lvl), delay_before_tx=None, delay_before_rx=None)
                                except Exception:
                                    pass

                            frame = make_read(slave, reg, 8 if reg==0 else 4)
                            # manual RTS toggle supports DE line manually
                            try:
                                if rts_mode == 'manual':
                                    # drive RTS high for TX then low for RX
                                    ser.setRTS(True)
                                    time.sleep(0.001)
                                    ser.write(frame)
                                    ser.flush()
                                    time.sleep(0.002)
                                    ser.setRTS(False)
                                else:
                                    ser.reset_input_buffer()
                                    ser.reset_output_buffer()
                                    ser.write(frame)
                                    ser.flush()
                            except Exception as e:
                                print('write failed', e)
                                ser.close()
                                continue

                            time.sleep(0.02)
                            rx = ser.read(256)
                            if rx:
                                ok = valid_modbus_response(rx)
                                print('RX len', len(rx), 'hex', rx.hex(), 'crc_ok', ok)
                                if ok:
                                    found.append({'baud':baud,'parity':parity,'stop':stop,'rts_mode':rts_mode,'slave':slave,'reg':reg,'rx':rx.hex()})
                                    # save and exit
                                    ser.close()
                                    print('Found valid response, stopping sweep')
                                    with open('bruteforce_found.txt','w') as fh:
                                        fh.write(str(found))
                                    raise SystemExit(0)
                                else:
                                    print('invalid CRC or short response')
                            ser.close()
    print('Sweep complete, found entries:', found)
    with open('bruteforce_found.txt','w') as fh:
        fh.write(str(found))
