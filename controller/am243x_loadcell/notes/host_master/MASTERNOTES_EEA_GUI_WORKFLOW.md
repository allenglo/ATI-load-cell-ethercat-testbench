# MasterNotes: EEA GUI Live Workflow And Pitfalls

Date: 2026-07-01
Scope: command-by-command live validation on COM18 (115200/E/1, RS485 RTS TX-enable)

## 2026-07-13 correction for direct EEA session

- Current source-backed direct EEA mapping is not the same as the older FLR lane guesses below.
- All three encoder channels use FC4 reg0 on their own slave:
  - S3 = slave1/reg0
  - S2 = slave2/reg0
  - S1 = slave3/reg0
- The old slave3/reg4 reading was not encoder position. It was `LsbFrameSQN`, so it simply counted upward with bus traffic.
- Direct raw EEA LED control is on slave3 holding regs 7/8/9:
  - reg7 = `(Red << 8) | Green`
  - reg8 = `(Blue << 8) | ((BrightnessCode << 4) | BlinkCode)`
  - reg9 = `(Terminator << 8) | Heartbeat`
- Firmware `heartbeatCheck()` forces purple fallback `0xFF00 / 0xFF50` whenever the heartbeat byte repeats for one 500 ms watchdog interval.
- EtherCAT gateway config uses the same semantics but split fields:
  - `ToEEA.S3Hearbeat`, `ToEEA.S3Terminator`, `ToEEA.S3BrightnessBlinkrate`, `ToEEA.S3LedBlue`, `ToEEA.S3LedGreen`, `ToEEA.S3LedRed`
- For the current Tk testbench talking directly over COM18, use the raw EEA registers above, not gateway symbolic field names.

## Verified Commands (one-by-one)

1) FC3 direct read, slave 1
- Command:
  - `& c:/CoRoot/.venv/Scripts/python.exe "##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts\send_configured_modbus.py" --port COM18 --baud 115200 --parity 1 --stopbits 1 --slave 1 --reg 0 --count 8`
- TX: `010300000008440c`
- RX: `010310000000000000000000000000c0f1000089aa`
- Decode:
  - addr=1, fc=3, bytecount=16
  - regs: `[0, 0, 0, 0, 0, 0, 0xC0F1, 0]`
  - CRC valid

2) Multi-FC probe (interrupted manually after sufficient capture)
- Command:
  - `& c:/CoRoot/.venv/Scripts/python.exe "##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts\send_multi_fc_probe.py"`
- Decoded behavior (stable):
  - FC1 -> exception frame `addr, 0x81, 0x01` (illegal function)
  - FC2 -> exception frame `addr, 0x82, 0x01` (illegal function)
  - FC3 -> valid reads for low windows; higher windows return `0x83, 0x02` (illegal data address)
  - FC4 -> valid reads for low windows; higher windows return `0x84, 0x02` (illegal data address)

3) All-function non-destructive test (slave 1)
- Command:
  - `& c:/CoRoot/.venv/Scripts/python.exe "##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts\test_eea_gui_functions_live.py" --port COM18 --baud 115200 --parity E --stopbits 1 --slave 1 --reg 0 --count 8 --out-base 6 --single-reg 6`
- Result file:
  - `notes/host_master/EEA_GUI_LIVE_TEST_RESULTS.json`
- Decode summary:
  - `poll_fc4_ok=true`
  - `poll_fc3_ok=true`
  - `profile_ok_count=3/4` (slave 4 profile no response)
  - `single_write_ok=true` (FC6 echo matched)
  - output block read at base 6 returns only one register then illegal-data-address behavior
  - LED mapped writes at reg 4370/4371 return exception `0x86,0x02`

4) Same all-function test (slave 2)
- Command:
  - `& c:/CoRoot/.venv/Scripts/python.exe "##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts\test_eea_gui_functions_live.py" --port COM18 --baud 115200 --parity E --stopbits 1 --slave 2 --reg 0 --count 8 --out-base 6 --single-reg 6 --out "c:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\notes\host_master\EEA_GUI_LIVE_TEST_RESULTS_slave2.json"`
- Result decode:
  - poll FC3/FC4 valid
  - single-writeback valid
  - LED writes return `0x86,0x02`
  - output block base6 still not a writable 20-register area

5) Same all-function test (slave 3)
- Command:
  - `& c:/CoRoot/.venv/Scripts/python.exe "##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts\test_eea_gui_functions_live.py" --port COM18 --baud 115200 --parity E --stopbits 1 --slave 3 --reg 0 --count 8 --out-base 6 --single-reg 6 --out "c:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\notes\host_master\EEA_GUI_LIVE_TEST_RESULTS_slave3.json"`
- Result decode:
  - poll FC3/FC4 valid
  - single-writeback valid
  - LED writes return `0x86,0x02`
  - output block base6 still not a writable 20-register area

6) Direct slave 4 check
- Command:
  - `& c:/CoRoot/.venv/Scripts/python.exe "##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts\send_configured_modbus.py" --port COM18 --baud 115200 --parity 1 --stopbits 1 --slave 4 --reg 0 --count 8`
- Decode:
  - TX valid
  - RX len 0 (no response)

## What Is Plausible And Confirmed

- Serial link and CRC are healthy.
- Slaves 1/2/3 respond consistently to FC3 and FC4 for low register windows.
- FC6 single-register writeback works on tested single registers (echo exact match).
- FC1 and FC2 are unsupported (exception 0x01), consistent and valid.
- Some register regions are explicitly blocked/invalid (exception 0x02), not random failures.
- Slave 4 currently appears absent/offline on this bus lane.

## Source Decode Addendum (SYCON netSlave)

Decoded from `external/INR_DEV-main/platform/EFlex/firmware/EthercatModbusRTUGateway/EthercatModbusRTUGateway/_S129/SYCON_net.xml` embedded BinData:

- Command table has explicit station windows:
  - slave4: FC4 reg3 qty7, FC16 reg6 qty4
  - slave3: FC4 reg0 qty10, FC16 reg6 qty4
  - slave2: FC4 reg0 qty8, FC16 reg6 qty1
  - slave1: FC4 reg0 qty8, FC16 reg6 qty1
- Signal names in those windows include:
  - `SxEncoderValue`, `SxEncoderSQN*`, `SxFrameSQN*`, `SxLatencySQN`, `SxGeneralInfo`, `SxEncLockingPosition`, `SxLed*`.

Practical decode:
- This explains why low FC4 windows are stable and why reg6 writes are accepted.
- It also explains why out-of-window addresses return legal `0x02` exceptions.

## Major Pitfalls For Future Agents

1) Do not interpret `0x83/0x84/0x86 + 0x02` as line noise.
- It is a valid Modbus exception (`illegal data address`) and means the target map/window is wrong for that node.

2) Do not assume the full 20-register converter output block is writable at `base=6` for this physical lane.
- Live tests show only narrow windows are accepted; broad block writes are rejected.

3) Do not assume slave 4 is active.
- Treat it as optional/offline unless proven by direct reply.

4) Always run commands one-by-one while debugging live hardware.
- Parallel probes hide causality and can collide on COM18.

5) Never mutate unknown control registers in exploratory runs.
- Use non-destructive write-back (read current value, write same value) first.

## Clean Directory Layout Standard

Use this exact structure for this lane:

- `scripts/`
  - only executable probe/test/gui scripts
- `notes/host_master/`
  - handoff notes, pitfalls, command logs, test result JSON
- `notes/gateway_reverse_engineering/`
  - raw probe logs and CSV captures

Naming rules:
- Test result JSON: `EEA_GUI_LIVE_TEST_RESULTS*.json`
- Operational notes: `MASTERNOTES_*.md`, `PITFALLS*.md`
- Avoid temporary files at repository root.

## Standard Agent Workflow (Do Not Skip)

1) Verify COM port is free.
2) Run one direct FC3 command first (`send_configured_modbus.py`).
3) Run one structured multi-function test (`test_eea_gui_functions_live.py`).
4) Decode exceptions explicitly:
   - `0x01` illegal function
   - `0x02` illegal data address
5) Save result JSON under `notes/host_master/`.
6) Update this master note with:
   - exact command(s)
   - TX/RX highlights
   - decoded outcome
   - one-line next action
