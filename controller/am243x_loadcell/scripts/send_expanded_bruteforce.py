#!/usr/bin/env python3
import serial, serial.rs485, time, struct

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


def make_frame(slave, fc, reg, count_or_val):
    if fc in (3,4):
        p = struct.pack('>B B H H', slave, fc, reg, count_or_val)
    elif fc == 6:
        p = struct.pack('>B B H H', slave, fc, reg, count_or_val)
    elif fc == 16:
        # write multiple: we'll send a minimal header and not fill payload (not ideal)
        p = struct.pack('>B B H H', slave, fc, reg, count_or_val)
    else:
        p = struct.pack('>B B H H', slave, fc, reg, count_or_val)
    return p + crc16_bytes(p).to_bytes(2,'little')


def valid_modbus_response(resp: bytes) -> bool:
    if len(resp) < 5:
        return False
    data, crc = resp[:-2], resp[-2:]
    return crc16_bytes(data) == int.from_bytes(crc,'little')


if __name__ == '__main__':
    port = 'COM18'
    bauds = [115200,57600,38400,19200,9600]
    parities = [0,1,2]
    stops = [1,2]
    rts_modes = ['rs485_true','rs485_false','manual','none']
    slaves = list(range(1,21))
    regs = [0,3,6,2880]
    fcs = [3,4,6]
    timeouts = [0.05,0.15,0.3]

    combos = 0
    for baud in bauds:
        for parity in parities:
            for stop in stops:
                for rts in rts_modes:
                    for slave in slaves:
                        for reg in regs:
                            for fc in fcs:
                                for to in timeouts:
                                    combos += 1
    print('Total combos:', combos)
    attempt = 0
    found = []
    logfile = 'expanded_bruteforce.log'

    for baud in bauds:
        for parity in parities:
            for stop in stops:
                for rts in rts_modes:
                    for slave in slaves:
                        for reg in regs:
                            for fc in fcs:
                                for timeout in timeouts:
                                    attempt += 1
                                    print(f'[{attempt}/{combos}] {baud} P={parity} S={stop} RTS={rts} slave={slave} reg={reg} FC={fc} TO={timeout}')
                                    with open(logfile,'a') as fh:
                                        fh.write(f'ATTEMPT {attempt}: {baud} P={parity} S={stop} RTS={rts} slave={slave} reg={reg} FC={fc} TO={timeout}\n')
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
                                        time.sleep(0.01)
                                        continue

                                    if rts.startswith('rs485'):
                                        try:
                                            lvl = True if rts == 'rs485_true' else False
                                            ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=lvl, rts_level_for_rx=(not lvl), delay_before_tx=None, delay_before_rx=None)
                                        except Exception:
                                            pass

                                    frame = make_frame(slave, fc, reg, 1 if fc in (3,4) else 0)
                                    try:
                                        if rts == 'manual':
                                            ser.setRTS(True); time.sleep(0.001)
                                            ser.write(frame); ser.flush(); time.sleep(0.002); ser.setRTS(False)
                                        else:
                                            ser.reset_input_buffer(); ser.reset_output_buffer(); ser.write(frame); ser.flush()
                                    except Exception as e:
                                        print('write failed', e); ser.close(); continue

                                    time.sleep(0.01)
                                    rx = ser.read(512)
                                    if rx:
                                        ok = valid_modbus_response(rx)
                                        s = f'RX len {len(rx)} hex {rx.hex()} crc_ok {ok}'
                                        print(s)
                                        with open(logfile,'a') as fh:
                                            fh.write('RESPONSE: '+s+'\n')
                                        if ok:
                                            found.append({'baud':baud,'parity':parity,'stop':stop,'rts':rts,'slave':slave,'reg':reg,'fc':fc,'timeout':timeout,'rx':rx.hex()})
                                            with open('expanded_found.txt','w') as fh:
                                                fh.write(str(found))
                                            print('Found valid response, exiting')
                                            ser.close()
                                            raise SystemExit(0)
                                    ser.close()
    print('Done. Found:', found)
    with open('expanded_found.txt','w') as fh:
        fh.write(str(found))
