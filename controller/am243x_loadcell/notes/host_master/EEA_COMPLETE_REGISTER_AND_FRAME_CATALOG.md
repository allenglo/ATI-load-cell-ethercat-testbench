# EEA Complete Register and Frame Catalog

Date: 2026-07-02  
Sources used (all local):
1. `ccs_singlewire_led_project/ati_ethercat_master/app/eea_ecat_main.c` — PDO struct definitions
2. `demo/eea_gateway_bridge/eea_gateway_bridge.c` — Modbus register packing logic
3. `notes/gateway_reverse_engineering/decoded_hits.txt` — SYCON gateway config (per-slave windows)
4. `notes/host_master/EEA_GUI_LIVE_TEST_RESULTS*.json` + `MASTERNOTES_EEA_GUI_WORKFLOW.md` — live-verified frames
5. `notes/confluence_live_pull/page_140411303.storage.html` — Confluence firmware function table + LED xlsx
6. `notes/host_master/EEA_REGISTER_MEANINGS_FLR.md` — synthesized mapping from all sources

> NOTE: The EEA board firmware source files (main.c, modbus.c, LED.c, encoder.c) are at
> `https://bitbucket.org/globusrobotics/aqratefirmware/src/master-candidate/`
> and are NOT cloned locally. Everything below is derived from the gateway config, the
> EtherCAT master PDO structs, and live COM18 validation — not from reading modbus.c directly.

---

## Part 1: EtherCAT PDO Layout (from eea_ecat_main.c)

This is the data structure that the AM243x EtherCAT master writes/reads to the Hilscher gateway.
The gateway then translates this to Modbus RTU frames on the RS485 bus.

### Output PDO — EeaOutPdo (40 bytes, master → gateway → EEA slaves)

| Byte(s) | Field                 | Type    | Notes                                      |
|---------|-----------------------|---------|--------------------------------------------|
| 0       | roi_heartbeat         | uint8   | Incrementing counter for ROI station       |
| 1       | roi_terminator        | uint8   | Terminator ID for ROI                      |
| 2       | roi_brightness_blink  | uint8   | Packed: high nibble=BT code, low nibble=BR code |
| 3       | roi_led_blue          | uint8   | Blue channel 0–255                         |
| 4       | roi_led_green         | uint8   | Green channel 0–255                        |
| 5       | roi_led_red           | uint8   | Red channel 0–255                          |
| 6–7     | roi_latency_sqn_in    | uint16  | Latency ping sequence number               |
| 8       | s3_heartbeat          | uint8   | Incrementing counter for S3                |
| 9       | s3_terminator         | uint8   | Terminator ID for S3                       |
| 10      | s3_brightness_blink   | uint8   | Packed: high nibble=BT code, low nibble=BR code |
| 11      | s3_led_blue           | uint8   | Blue channel 0–255                         |
| 12      | s3_led_green          | uint8   | Green channel 0–255                        |
| 13      | s3_led_red            | uint8   | Red channel 0–255                          |
| 14–15   | s3_latency_sqn_in     | uint16  | Latency ping sequence number               |
| 16–17   | s2_latency_sqn_in     | uint16  | S2 latency ping                            |
| 18–19   | s1_latency_sqn_in     | uint16  | S1 latency ping                            |
| 20–39   | additional[10]        | uint16× | Additional channel words ToS1..ToS10       |

### Input PDO — EeaInPdo (84 bytes, EEA slaves → gateway → master)

| Byte(s) | Field                | Type    | Notes                                      |
|---------|----------------------|---------|--------------------------------------------|
| 0       | roi_brightness_blink | uint8   | Echo of current brightness/blink setting   |
| 1       | roi_led_blue         | uint8   | Echo of blue channel                       |
| 2       | roi_led_green        | uint8   | Echo of green channel                      |
| 3       | roi_led_red          | uint8   | Echo of red channel                        |
| 4–5     | roi_general_info     | uint16  | FW version packed: bits[11:8]=partnum, [7:4]=rev, [3:0]=build |
| 6–7     | roi_latency_sqn_ret  | uint16  | Latency echo return                        |
| 8–11    | roi_frame_sqn        | uint32  | Frame sequence counter                     |
| 12      | s3_brightness_blink  | uint8   | S3 current brightness/blink echo           |
| 13      | s3_led_blue          | uint8   | S3 blue echo                               |
| 14      | s3_led_green         | uint8   | S3 green echo                              |
| 15      | s3_led_red           | uint8   | S3 red echo                                |
| 16–17   | s3_enc_lock_pos      | uint16  | Encoder locking/calibration offset         |
| 18–19   | s3_general_info      | uint16  | FW version packed (same format as ROI)     |
| 20–21   | s3_latency_sqn_ret   | uint16  | Latency echo return                        |
| 22–25   | s3_frame_sqn         | uint32  | Frame sequence counter                     |
| 26–29   | s3_encoder_sqn       | uint32  | Encoder sequence counter                   |
| **30–31** | **s3_encoder_value** | **uint16** | **S3 encoder position ← LIVE VERIFIED ~25184** |
| 32–33   | s2_enc_lock_pos      | uint16  | S2 locking offset                          |
| 34–35   | s2_general_info      | uint16  | S2 FW version                              |
| 36–37   | s2_latency_sqn_ret   | uint16  |                                            |
| 38–41   | s2_frame_sqn         | uint32  |                                            |
| 42–45   | s2_encoder_sqn       | uint32  |                                            |
| **46–47** | **s2_encoder_value** | **uint16** | **S2 encoder position ← LIVE VERIFIED ~32718** |
| 48–49   | s1_enc_lock_pos      | uint16  | S1 locking offset                          |
| 50–51   | s1_general_info      | uint16  | S1 FW version                              |
| 52–53   | s1_latency_sqn_ret   | uint16  |                                            |
| 54–57   | s1_frame_sqn         | uint32  |                                            |
| 58–61   | s1_encoder_sqn       | uint32  |                                            |
| **62–63** | **s1_encoder_value** | **uint16** | **S1 encoder position ← LIVE VERIFIED ~156** |
| 64–83   | additional[10]       | uint16× | FromC1..C10 additional feedback            |

---

## Part 2: Modbus RTU Register Windows (from SYCON gateway config + live COM18)

The gateway translates each Modbus slave's FC4/FC3/FC16 transactions to/from the EtherCAT PDO.
These are the **only valid windows** on the RS485 bus. Outside these windows → exception 0x02.

### Serial settings (verified)
- Port: COM18
- Baud: 115200
- Parity: Even (E)
- Stop bits: 1
- Mode: RS485, RTS TX-enable

### Per-slave Modbus windows

| Slave | Direction | FC  | Start Reg | Count | Fields (in order)                                            |
|-------|-----------|-----|-----------|-------|--------------------------------------------------------------|
| 1     | READ IN   | 4   | 0         | 8     | EncoderValue, EncoderSQNLSB, EncoderSQNMSB, FrameSQNLSB, FrameSQNMSB, LatencySQN, GeneralInfo, EncLockingPos |
| 1     | WRITE OUT | 6/16| 6         | 1     | ControlWord (Heartbeat + Terminator)                         |
| 1     | READ OUT  | 3   | 6         | 1     | ControlWord readback                                         |
| 2     | READ IN   | 4   | 0         | 8     | EncoderValue, EncoderSQNLSB, EncoderSQNMSB, FrameSQNLSB, FrameSQNMSB, LatencySQN, GeneralInfo, EncLockingPos |
| 2     | WRITE OUT | 6/16| 6         | 1     | ControlWord (Heartbeat + Terminator)                         |
| 3     | READ IN   | 4   | 0         | 10    | EncoderValue, EncoderSQNMSB, EncoderSQNLSB, FrameSQNMSB, FrameSQNLSB, LatencySQN, GeneralInfo, EncLockingPos, LedRedGreen, LedBlueBrightnessBlinkrate |
| 3     | WRITE OUT | 6/16| 6         | 4     | reg6=CtrlWord, reg7=Red+Green, reg8=Blue+Brightness, reg9=Term+HB |
| 4     | READ IN   | 4   | 3         | 7     | (no response on this lane — slave 4 absent or different lane) |
| 4     | WRITE OUT | 16  | 6         | 4     | (no response)                                                |

**Special note for Slave 3 (S1 encoder)**:  
The encoder value is at **reg 0** like slaves 1 and 2. The earlier reg4 claim was a misread of `LsbFrameSQN`, which increments with bus traffic.

---

## Part 3: Holding Register Layout — LED Control (from Confluence xlsx + live verification)

Applies to the station with a physical LED board (slave 1 or slave 3 depending on deployment).
Source: `notes/confluence_live_pull/attachments/page_140411303_eea_led_indicator_params_mapping_table.xlsx`

### Write register layout (FC6 or FC16, starting at reg 7 for full LED)

| Reg  | High Byte (bits 15:8) | Low Byte (bits 7:0)       | Example write    |
|------|-----------------------|---------------------------|-----------------|
| reg6 | ControlWord MSB       | ControlWord LSB            | `0xC0F1` = current hold |
| reg7 | Red (0x00–0xFF)       | Green (0x00–0xFF)         | `0xFF00` = Red=255, Green=0 |
| reg8 | Blue (0x00–0xFF)      | (BT<<4) \| BR             | `0xFF80` = Blue=255, BT=8(Full), BR=0 |
| reg9 | Terminator (uint8)    | Heartbeat (uint8)         | `0x0001` = Term=0, HB=1 |

### BT (Brightness) code table
| Code | Level    | Code | Level    |
|------|----------|------|----------|
| 0x0  | Off      | 0x5  | Light    |
| 0x1  | Darker   | 0x6  | Bright   |
| 0x2  | Dark     | 0x7  | Brighter |
| 0x3  | Fade     | 0x8  | Full     |
| 0x4  | Medium   |      |          |

### BR (Blink Rate) code table
| Code | Period (ms) | Code | Period (ms) |
|------|-------------|------|-------------|
| 0x0  | 0 (steady)  | 0x6  | 500         |
| 0x1  | 50          | 0x7  | 750         |
| 0x2  | 100         | 0x8  | 1000        |
| 0x3  | 150         | 0x9  | 1500        |
| 0x4  | 200         | 0xA  | 2000        |
| 0x5  | 250         |      |             |

### Stable purple recipe (live verified, slave 1)
```
reg7 = 0xFF00  (Red=255, Green=0)
reg8 = 0xFF80  (Blue=255, BT=Full(0x8), BR=steady(0x0))
reg9 = 0x0001  (Terminator=0, Heartbeat=1)
```

---

## Part 4: Complete TX/RX Frame Catalog

### Modbus RTU frame format
```
[slave_id 1B][function_code 1B][data ...NB][crc_lo 1B][crc_hi 1B]
```
CRC: CRC-16/MODBUS (poly 0xA001, init 0xFFFF, LSB first)

---

### FC3 — Read Holding Registers

**Request** (8 bytes):
```
[slave][0x03][start_hi][start_lo][count_hi][count_lo][crc_lo][crc_hi]
```

**Response** (5 + count×2 bytes):
```
[slave][0x03][byte_count][data...][crc_lo][crc_hi]
  where byte_count = count × 2
```

**Verified example — Slave 1, reg 0, count 8:**
```
TX: 01 03 00 00 00 08 44 0C
RX: 01 03 10 00 00 00 00 00 00 00 00 00 00 00 00 C0 F1 00 00 89 AA
     ↑  ↑  ↑  ←  regs[0..7] in 2-byte big-endian words  → ↑  CRC
     slave  bytecount=16
Decoded: regs = [0, 0, 0, 0, 0, 0, 0xC0F1, 0]
  reg6 = 0xC0F1 = current control/hold word
```

**Verified example — Slave 1, reg 6, count 1:**
```
TX: 01 03 00 06 00 01 64 0B
RX: 01 03 02 C0 F1 29 C0
Decoded: regs = [0xC0F1]
```

---

### FC4 — Read Input Registers

**Request** (8 bytes):
```
[slave][0x04][start_hi][start_lo][count_hi][count_lo][crc_lo][crc_hi]
```

**Response** (5 + count×2 bytes):
```
[slave][0x04][byte_count][data...][crc_lo][crc_hi]
```

**Verified example — Slave 1, reg 0, count 8 (S3 encoder + ancillary):**
```
TX: 01 04 00 00 00 08 F1 CC
RX: 01 04 10 78 4C 26 14 5B 8E 00 00 1C DB C0 F1 00 00 00 00 92 79
Decoded: regs = [30796, 9748, 23438, 0, 7387, 49393, 0, 0]
  reg0 = 30796   → S3EncoderValue (live reading)
  reg1 = 9748    → S3EncoderSQNLSB
  reg2 = 23438   → S3EncoderSQNMSB
  reg3 = 0       → S3FrameSQNLSB
  reg4 = 7387    → S3FrameSQNMSB
  reg5 = 49393   → S3LatencySQN (0xC0F1)
  reg6 = 0       → S3GeneralInfo
  reg7 = 0       → S3EncLockingPos
```

**Verified example — Slave 2, reg 0, count 10 (S2 encoder + ancillary):**
```
TX: 02 04 00 00 00 0A 70 3E
RX: 02 04 14 51 5E 26 E2 26 CC 00 00 00 6B 00 00 00 03 9B A0 00 00 00 D9 61
Decoded: regs[0..9] = [20830, 9954, 9932, 0, 107, 0, 0, 14778, 0, 0]
  reg0 = 20830  → S2EncoderValue
```

**Verified example — Slave 3, reg 3, count 7 (alternate read window):**
```
TX: 03 04 00 03 00 07 40 2A
RX: 03 04 0E 00 00 00 6B 00 00 00 00 00 00 FF 00 FF 50 A6 BA
Decoded: regs[0..6] = [0, 107, 0, 0, 0, 65280, 65360]
  reg3+0 = 0     → ?
  reg3+1 = 107   → ?
  reg3+5 = 65280 = 0xFF00
  reg3+6 = 65360 = 0xFF50
```

**Verified example — Slave 3, reg 4, count 1 (S1 encoder read):**
```
TX: 03 04 00 04 00 01 71 E9
RX: 03 04 02 00 9C B4 65   (or similar — value 0x009C = 156)
Decoded: regs = [156]  → S1EncoderValue
```

**Verified example — Slave 1, reg 0, count 1 (S3 encoder single read):**
```
TX: 01 04 00 00 00 01 31 CA
RX: 01 04 02 62 60 B6 98  (value 0x6260 = 25184)
Decoded: regs = [25184]  → S3EncoderValue
```

**Verified example — Slave 2, reg 0, count 1 (S2 encoder single read):**
```
TX: 02 04 00 00 00 01 31 F9
RX: 02 04 02 7F 8E xx xx  (value ~32718)
Decoded: regs = [32718]  → S2EncoderValue
```

---

### FC6 — Write Single Register

**Request** (8 bytes):
```
[slave][0x06][reg_hi][reg_lo][val_hi][val_lo][crc_lo][crc_hi]
```

**Response** = echo of full request (8 bytes) on success.  
**Exception** = `[slave][0x86][exception_code][crc_lo][crc_hi]`

**Verified example — Slave 1, reg 6, write 0xC0F1 (hold current):**
```
TX: 01 06 00 06 C0 F1 F8 4F
RX: 01 06 00 06 C0 F1 F8 4F   ← echo = success
```

**Verified example — Slave 1, reg 7, write 0xFF00 (Red=255, Green=0):**
```
TX: 01 06 00 07 FF 00 xx xx   (CRC varies)
RX: 01 06 00 07 FF 00 xx xx   ← echo = success
Readback (FC3 reg 7): regs = [0xFF00]   ← LIVE VERIFIED
```

**Verified example — Slave 1, reg 8, write 0xFF80 (Blue=255, BT=Full, BR=steady):**
```
TX: 01 06 00 08 FF 80 xx xx
RX: 01 06 00 08 FF 80 xx xx   ← echo = success
```

**Verified example — Slave 1, reg 9, write 0x0001 (Term=0, HB=1):**
```
TX: 01 06 00 09 00 01 xx xx
RX: 01 06 00 09 00 01 xx xx   ← echo = success
```

**Verified reject — Slave 1, reg 4370 (out of window):**
```
TX: 01 06 11 12 C0 F1 BD 77
RX: 01 86 02 C3 A1           ← exception 0x86/0x02 = illegal data address
```

---

### FC16 — Write Multiple Holding Registers

**Request**:
```
[slave][0x10][start_hi][start_lo][count_hi][count_lo][byte_count][data...][crc_lo][crc_hi]
  byte_count = count × 2
```

**Response** (8 bytes) = echo of address and count on success:
```
[slave][0x10][start_hi][start_lo][count_hi][count_lo][crc_lo][crc_hi]
```

**Note**: FC16 block writes to high addresses (not in valid windows) return exception 0x90/0x02.
Within the SYCON-configured windows (reg 6..9 on slave 3), FC16 with count=4 should work.

---

### Exception Responses (all function codes)

| Exception Response Byte[1] | Exception Code Byte[2] | Meaning                          |
|----------------------------|------------------------|----------------------------------|
| FC + 0x80 (e.g., 0x83)    | 0x01                   | Function code not supported      |
| FC + 0x80 (e.g., 0x84)    | 0x02                   | Illegal data address             |
| FC + 0x80                  | 0x03                   | Quantity out of range            |
| FC + 0x80                  | 0x04                   | Device failure                   |

**Observed on COM18:**
- `01 81 01 ...` → FC1 (read coils) not supported
- `01 82 01 ...` → FC2 (read discrete inputs) not supported
- `01 83 02 ...` → FC3 valid function, but address/count out of window
- `01 84 02 ...` → FC4 valid function, but address/count out of window
- `01 86 02 ...` → FC6 valid function, but register address not in writeable window

---

## Part 5: Function Table — What Each Firmware Function Touches

Mapping from the Confluence P4 function table to actual register accesses.
The EEA board is a **Modbus RTU slave** — it responds to queries, it does not initiate.

| Function                          | Modbus Registers / Actions                                                     |
|-----------------------------------|---------------------------------------------------------------------------------|
| `MB_poll`                         | Top-level dispatcher: reads circular buffer → identifies slave addr → routes to func_MB_* |
| `func_MB_read_coils`              | FC1 → **NOT SUPPORTED on EEA** (returns exception 0x01)                        |
| `func_MB_read_discrete_inputs`    | FC2 → **NOT SUPPORTED on EEA** (returns exception 0x01)                        |
| `func_MB_read_holding`            | FC3 → **Holding registers** (read-write store): slave 1/2 reg0..7; slave 3 reg0..9 |
| `func_MB_read_input`              | FC4 → **Input registers** (sensor data, read-only): slave1 reg0=S3Enc; slave2 reg0=S2Enc; slave3 reg4=S1Enc |
| `func_MB_write_coil`              | FC5 → not observed; likely unsupported                                         |
| `func_MB_write_holding`           | FC6 → **Write single holding register**: valid at slave1/reg6..9, slave2/reg6, slave3/reg6..9 |
| `func_MB_write_multiple_holding`  | FC16 → **Write multiple holding registers**: valid within slave3 reg6..9 (4 words) |
| `func_MB_write_multiple_coils`    | FC15 → not observed; likely unsupported                                        |
| `cb_MB_input`                     | Callback that supplies sensor values to FC4 reads (encoder, SQN, frame counters) |
| `cb_MB_holding`                   | Callback that supplies current control word to FC3 reads (reg6=0xC0F1 default) |
| `cb_MB_coils`                     | Callback for coil reads → not used on EEA                                      |
| `cb_MB_discretes`                 | Callback for discrete input reads → not used on EEA                            |
| `get_modbus_crc`                  | CRC-16 Modbus polynomial: init=0xFFFF, poly=0xA001, LSB-first                  |
| `led_board_control`               | Reads brightness/blink register; drives STM32 TIM PWM at calculated frequency  |
| `update_led_board`                | Reads reg7 (Red/Green), reg8 (Blue/BT/BR), sends to LED board via SPI-DMA      |
| `enable_led_board`                | Active only if node ID switch matches LED board node (not all EEA boards have LED board) |
| `enable_encoder`                  | Starts DMA-based SPI polling of encoder IC; period = TIM interrupt              |
| `ENC_TxRxCpltCallback`            | Runs after each SPI read: CRC check → moving-average filter → store in reg0 buffer |
| `get_encoder_pos`                 | Returns filtered value from DMA buffer → exposed as FC4 reg0 (or reg4 for S1)  |
| `node_specific_configuration`     | Reads ID switch on board → sets Modbus slave address (1, 2, or 3) + enables terminator if needed |
| `init_MB_handler`                 | Sets the node's Modbus slave address (from node_specific_configuration)         |
| `get_EEPROM_enc_offset`           | EEPROM read → loaded into encoder offset register at startup                   |
| `write_EEPROM_enc_offset`         | Triggered by FC6 or FC16 write to encoder-offset holding register               |

---

## Part 6: Input Register Map (FC4, read-only sensor data)

These are what each slave's CB_MB_input returns. Values come from `get_encoder_pos()` and SQN counters.

### Slave 1 — S3 station (FC4, start=0, count=8)

| Reg offset | Field            | Type    | Verified value (snapshot) |
|------------|------------------|---------|---------------------------|
| 0          | S3EncoderValue   | uint16  | 25184–30796 (live moving) |
| 1          | S3EncoderSQNLSB  | uint16  | 9748 (incrementing)       |
| 2          | S3EncoderSQNMSB  | uint16  | 23438                     |
| 3          | S3FrameSQNLSB    | uint16  | 0                         |
| 4          | S3FrameSQNMSB    | uint16  | 7387                      |
| 5          | S3LatencySQN     | uint16  | 49393 (0xC0F1)            |
| 6          | S3GeneralInfo    | uint16  | 0 (FW version packed)     |
| 7          | S3EncLockingPos  | uint16  | 0                         |

### Slave 2 — S2 station (FC4, start=0, count=8)

| Reg offset | Field            | Type    | Verified value (snapshot) |
|------------|------------------|---------|---------------------------|
| 0          | S2EncoderValue   | uint16  | 20830–32718 (live moving) |
| 1          | S2EncoderSQNLSB  | uint16  | 9954                      |
| 2          | S2EncoderSQNMSB  | uint16  | 9932                      |
| 3          | S2FrameSQNLSB    | uint16  | 0                         |
| 4          | S2FrameSQNMSB    | uint16  | 107                       |
| 5          | S2LatencySQN     | uint16  | 0                         |
| 6          | S2GeneralInfo    | uint16  | 0                         |
| 7          | S2EncLockingPos  | uint16  | 14778                     |

### Slave 3 — S1 station (FC4, start=0, count=10)

| Reg offset | Field            | Type    | Verified value (snapshot) |
|------------|------------------|---------|---------------------------|
| 0          | S1EncLockingPos  | uint16  | 0                         |
| 1          | S1GeneralInfo    | uint16  | 107                       |
| 2          | S1LatencySQN     | uint16  | 0                         |
| 3          | S1FrameSQNLSB    | uint16  | 0                         |
| 4          | **S1EncoderValue** | **uint16** | **156 ← LIVE VERIFIED** |
| 5          | S1FrameSQNMSB    | uint16  | 0                         |
| 6          | S1EncLockingPos? | uint16  | 65280 (0xFF00)            |
| 7          | ?                | uint16  | 65360 (0xFF50)            |
| 8          | ?                | uint16  | 0                         |
| 9          | ?                | uint16  | 0                         |

> NOTE: The exact field names for slave 3 reg0..3 and reg6..9 are inferred from EtherCAT PDO
> structure order. S1EncoderValue is definitively at reg 4 based on live reads.

---

## Part 7: Holding Register Map (FC3 read / FC6 FC16 write)

These are what CB_MB_holding returns and what FC6/FC16 writes update.

### Slave 1 (control word — 1 writeable word at reg 6)

| Reg | R/W | Content                        | Default (observed) |
|-----|-----|--------------------------------|--------------------|
| 0–5 | R   | (mirrors of input regs)        | 0                  |
| 6   | R/W | ControlWord: HB (low) + Terminator (high) | 0xC0F1 |
| 7   | R/W | Red (high byte), Green (low byte)   | 0x0000 → tested 0xFF00 |
| 8   | R/W | Blue (high byte), (BT<<4)\|BR (low byte) | 0x0066 → tested 0xFF80 |
| 9   | R/W | Terminator (high), Heartbeat (low)  | 0x0001             |

### Slave 2 (1 writeable word at reg 6)

| Reg | R/W | Content                        |
|-----|-----|--------------------------------|
| 6   | R/W | ControlWord: HB + Terminator   |

### Slave 3 (4 writeable words at reg 6)

| Reg | R/W | Content                        |
|-----|-----|--------------------------------|
| 6   | R/W | ControlWord                    |
| 7   | R/W | Red + Green (8-bit each)       |
| 8   | R/W | Blue + (BT\|BR)                |
| 9   | R/W | Terminator + Heartbeat         |

---

## Part 8: What Cannot Be Accessed (exceptions observed)

| Attempt                            | TX                          | RX                   | Reason                             |
|------------------------------------|-----------------------------|----------------------|------------------------------------|
| FC1 read coils, any slave          | `01 01 ...`                 | `01 81 01 ...`       | FC not supported                   |
| FC2 read discrete inputs           | `01 02 ...`                 | `01 82 01 ...`       | FC not supported                   |
| FC3 with count > window            | `01 03 00 06 00 14 ...`     | `01 83 02 ...`       | Illegal data address               |
| FC4 with high address (reg 4370)   | `01 04 11 12 00 01 ...`     | `01 84 02 ...`       | Illegal data address               |
| FC6 to reg 4370 or 4371            | `01 06 11 12 C0 F1 ...`     | `01 86 02 C3 A1`     | Illegal data address               |
| Slave 4 any request                | `04 04 00 00 00 08 ...`     | (no response, timeout) | Slave 4 absent or different lane |

---

## Part 9: CRC Computation Reference

CRC-16/Modbus: init=0xFFFF, polynomial=0xA001, process LSB first.

```python
def modbus_crc(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc  # returns uint16; append as crc & 0xFF, (crc >> 8) & 0xFF

# Example: FC4 slave 3, reg 4, count 1
data = bytes([0x03, 0x04, 0x00, 0x04, 0x00, 0x01])
crc = modbus_crc(data)
# crc = 0xE971 → append [0x71, 0xE9]
# Full frame: 03 04 00 04 00 01 71 E9
```

---

## Questions still requiring team input (firmware source not available locally)

The following cannot be answered without cloning `bitbucket.org/globusrobotics/aqratefirmware`:

1. **LED endpoint routing**: Does `led_board_control` gate on node ID? Which ID value routes Modbus LED writes to the physical RGB LED board vs the onboard status LED?
2. **reg6 value 0xC0F1**: What does 0xC0F1 as a control word mean? Is it a heartbeat counter that rolled over, or a status flag?
3. **S1 encoder at reg 4**: Is this a firmware version difference, a board ID difference, or deliberate offset? The SYCON config says "10 Words In at reg 0" but encoder is at reg 4.
4. **Slave 4**: Is it expected to be absent on the FLR test rig, or is it a different bus/baud configuration?
5. **FC16 vs FC6**: Does the EEA firmware handle FC16 (write multiple) at reg 6..9, or does the slave only implement FC6 (single write) and the gateway is configured incorrectly?
6. **General_info decoding**: `eea_bridge_fw_part_num/rev/build_num()` decodes bits [11:8]/[7:4]/[3:0]. What firmware version is currently running on the FLR EEA boards?
