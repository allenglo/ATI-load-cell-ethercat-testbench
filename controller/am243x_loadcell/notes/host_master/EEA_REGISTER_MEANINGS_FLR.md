# EEA Register Meanings And FLR Live Mapping

Date: 2026-07-01

## Source-backed semantic fields (gateway XML)

Source:
- `external/INR_DEV-main/platform/EFlex/firmware/EthercatModbusRTUGateway/EthercatModbusRTUGateway.xml`
- `external/INR_DEV-main/platform/EFlex/firmware/EthercatModbusRTUGateway/EthercatModbusRTUGateway/_S129/SYCON_net.xml` (decoded embedded netSlave command table)

FromEEA field order includes (non-exhaustive):
- `S3BrightnessBlinkrate`
- `S3LedBlue`
- `S3LedGreen`
- `S3LedRed`
- `S3EncLockingPosition`
- `S3GeneralInfo`
- `S3LatencySQNReturn`
- `S3FrameSQN`
- `S3EncoderSQN`
- `S3EncoderValue`
- `S2...`
- `S2EncoderValue`
- `S1...`
- `S1EncoderValue`

The semantic names above are authoritative for meaning, while serial Modbus address windows on COM18 are lane-specific and not a direct 1:1 copy of EtherCAT bit offsets.

## Decoded Modbus command table (from SYCON project)

Recovered from `_S129/SYCON_net.xml` embedded `BinData` payload (`zlib` + UTF-16 XML fragments).

Configured modules and windows:

- Slave 4:
  - FC4 read: start register 3, quantity 7 words (`moduleType=7 Words In`, `moduleAddress=Register 3`)
  - FC16 write: start register 6, quantity 4 words (`moduleType=4 Words Out`, `moduleAddress=Register 6`)
- Slave 3:
  - FC4 read: start register 0, quantity 10 words (`moduleType=10 Words In`, `moduleAddress=Register 0`)
  - FC16 write: start register 6, quantity 4 words (`moduleType=4 Words Out`, `moduleAddress=Register 6`)
- Slave 2:
  - FC4 read: start register 0, quantity 8 words (`moduleType=8 Words In`, `moduleAddress=Register 0`)
  - FC16 write: start register 6, quantity 1 word (`moduleType=1 Word Out`, `moduleAddress=Register 6`)
- Slave 1:
  - FC4 read: start register 0, quantity 8 words (`moduleType=8 Words In`, `moduleAddress=Register 0`)
  - FC16 write: start register 6, quantity 1 word (`moduleType=1 Word Out`, `moduleAddress=Register 6`)

Decoded signals confirm semantic intent inside those windows:

- S3 read block includes:
  - `S3EncoderValue`, `S3EncoderSQNLSB`, `S3EncoderSQNMSB`, `S3FrameSQNLSB`, `S3FrameSQNMSB`, `S3LatencySQN`, `S3GeneralInfo`, `S3EncLockingPos`, LED feedback fields.
- S2 read block includes:
  - `S2EncoderValue`, `S2EncoderSQNLSB`, `S2EncoderSQNMSB`, `S2FrameSQNLSB`, `S2FrameSQNMSB`, `S2LatencySQN`, `S2GeneralInfo`, `S2EncLockingPosition`.
- S1 read block includes:
  - `S1EncoderValue`, `S1EncoderSQNLSB`, `S1EncoderSQNMSB`, `S1FrameSQNLSB`, `S1FrameSQNMSB`, `S1LatencySQN`, `S1GeneralInfo`, `S1EncLockingPosition`.
- Write blocks include per-station command fields like:
  - `SxLatencySQN` and LED command bytes (`SxLedGreen`, `SxLedRed`, `SxLedBlue`).

## FLR live serial mapping (verified)

Serial settings:
- COM18
- 115200 baud
- even parity
- 1 stop bit
- RS485 RTS TX-enable

Verified one-by-one FC4 read map for all 3 encoder channels:

- S3 encoder channel:
  - slave=1, reg=0, count=1
  - command: `read_modbus_regs.py --slave 1 --fc 4 --reg 0 --count 1`
  - sample: `REGS=[25184]`

- S2 encoder channel:
  - slave=2, reg=0, count=1
  - command: `read_modbus_regs.py --slave 2 --fc 4 --reg 0 --count 1`
  - sample: `REGS=[31]`

- S1 encoder channel:
  - slave=3, reg=0, count=1
  - command: `read_modbus_regs.py --slave 3 --fc 4 --reg 0 --count 1`
  - source-backed meaning: `EncoderValue`

Interpretation:
- All 3 channels are readable with valid CRC.
- All 3 encoder channels live at reg0 of their own slave in the current GENU EEA firmware.
- The earlier slave3/reg4 reading was `LsbFrameSQN`, not encoder position, which is why it only counted upward.
- Live lane behavior aligns with decoded command table: encoder values are inside low FC4 windows on slaves 1/2/3.

## LED control status (FLR lane)

Confirmed writable path:
- FC6 write to slave1/reg6 is accepted and readback matches.
- example write/readback cycle:
  - pre: `REGS=[49393]` (0xC0F1)
  - write 0x0000 -> post `REGS=[0]`
  - write 0x00FF -> post `REGS=[255]`
  - write 0xFF00 -> post `REGS=[65280]`

Rejected path on this lane:
- FC6 to high LED-mapped addresses 4370/4371 returns exception (`0x86 0x02`, illegal data address).

Interpretation with source context:
- The SYCON command table expects LED writes in the slave-local write windows at register 6.
- Attempting high absolute addresses bypasses the configured local command table and is rejected on this lane.

## P4 LED register packing (from page 140411303 graphs + xlsx)

Source assets reviewed:
- `notes/confluence_live_pull/attachments/page_140411303_VnV EEA Firmware.png`
- `notes/confluence_live_pull/attachments/page_140411303_eea_led_indicator_params_mapping_table.xlsx`

Holding register layout per slave (when base is 6):
- `reg7`: high byte `Red`, low byte `Green`
- `reg8`: high byte `Blue`, low byte `(BT << 4) | BR`
- `reg9`: high byte `Terminator`, low byte `Heartbeat`

Code tables from xlsx:
- Blink (`BR`, 4-bit):
  - `0->0x0, 50->0x1, 100->0x2, 150->0x3, 200->0x4, 250->0x5, 500->0x6, 750->0x7, 1000->0x8, 1500->0x9, 2000->0xA`
- Brightness (`BT`, 4-bit used in packed byte):
  - `Off=0x0, Darker=0x1, Dark=0x2, Fade=0x3, Medium=0x4, Light=0x5, Bright=0x6, Brighter=0x7, Full=0x8`

Live proof (slave1):
- `reg7` write `0xFF00` accepted/readback `0xFF00`
- `reg8` write `0x0066` accepted/readback `0x0066` (`BT=Bright(0x6), BR=500ms(0x6)`)
- `reg9` write `0x0001` accepted/readback `0x0001`

## Practical usage for GUI/FLR

- Use explicit 3-channel read map:
  - S3: slave1/reg0 (FC4)
  - S2: slave2/reg0 (FC4)
  - S1: slave3/reg0 (FC4)
- For direct raw EEA control, use slave3 holding regs 7/8/9 for LED color plus heartbeat.
- Gateway field names such as `ToEEA.S3Hearbeat` and `ToEEA.S3LedRed` are the production EtherCAT view of the same bytes, not alternate raw Modbus addresses.
- Do not assume full 20-register block writes are valid on this serial lane.

## SOP: Read all encoder values (safe)

1. Confirm COM18 and RS485 settings.
2. Read exactly these channels one-by-one:
   - `read_modbus_regs.py --slave 1 --fc 4 --reg 0 --count 1`
   - `read_modbus_regs.py --slave 2 --fc 4 --reg 0 --count 1`
  - `read_modbus_regs.py --slave 3 --fc 4 --reg 0 --count 1`
3. Decode and log each response value and CRC status.
4. Treat `0x84 0x02` as map/window issue, not serial noise.

## SOP: LED command path (safe)

1. Read current control word first (`slave 1`, `reg 6`).
2. Write a test value with FC6 and read back immediately.
3. Restore previous value after test.
4. If write echo/readback mismatch, stop and do not continue with broader writes.

## SOP: Latency sequence usage (from naming semantics)

The source names indicate a ping-return flow:

1. Write `SxLatencySQN` in `ToEEA` write window (register 6 block for target slave).
2. Read corresponding `SxLatencySQN`/`SxLatencySQNReturn` field in `FromEEA` read window.
3. Verify returned sequence matches expected update behavior.

This should be validated per slave on this lane before relying on it in production timing checks.
