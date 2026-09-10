# AM243x LaunchPad Setup & JTAG Configuration Master Guide

## Quick Reference

| Setting | Value | Status |
|---------|-------|--------|
| **Normal Dev Switch (SW4)** | `0100 0100` (OSPI boot) | ✓ Recommended |
| **One-Time Flash Switch (SW4)** | `1110 0000` (UART boot) | ✓ Verified |
| **Raw JTAG Attach Switch (SW4)** | `1111 0000` (No Boot / DEV) | Special case only |
| **JTAG Config File** | `am2434_xds110_generated.ccxml` | ✓ Verified |
| **JTAG Clock Speed** | **5.5 MHz (DEFAULT)** | ✓ Verified |
| **Power Supply** | 5V / 3A USB Type-C | ✓ Verified |
| **Board Status** | Fully Operational | ✓ Verified |

---

## Hardware Configuration

### DIP Switch Settings (SW4)

SW4.8 is unused. The practical 8-position settings are:

| Mode | SW4 setting | Use |
|------|-------------|-----|
| **UART boot** | `1110 0000` | One-time flash via `uart_uniflash.py` |
| **OSPI boot** | `0100 0100` | Normal development after SBL NULL is flashed |
| **No Boot / DEV** | `1111 0000` | Raw JTAG attach or CCS scripting only |
| **USB-DFU** | `1010 0000` | Special-case DFU recovery |

**Recommended now: `0100 0100`** for normal bring-up and UART-visible development.

**Use `1110 0000` only when flashing SBL NULL or other images over UART.**

**Use `1111 0000` only when you intentionally want No Boot / raw JTAG attach.** It is not the normal runtime setting.

```
OSPI boot (`0100 0100`)
SW4.1: OFF (0)
SW4.2: ON  (1)
SW4.3: OFF (0)
SW4.4: OFF (0)
SW4.5: OFF (0)
SW4.6: ON  (1)
SW4.7: OFF (0)
SW4.8: OFF (unused)
```

The earlier `1111000` note corresponds to No Boot on SW4.1-7. That mode is valid for special JTAG cases, but it should not be treated as the default board setting for this project.

### Power Supply

- **Connector**: Type-C (J1)
- **Voltage**: 5V DC
- **Current**: Minimum 3A sustained
- **Important**: Use a quality power adapter or USB hub with 5V/3A capacity. **Do not use weak USB ports.**

### Connections

| Connector | Purpose | Cable |
|-----------|---------|-------|
| **J20** | XDS110 Debug Probe (micro-B) | Micro-B USB cable |
| **J1** | Board Power (Type-C) | Type-C USB cable (5V/3A) |

**Connection sequence:**
1. Connect Type-C power **first**
2. Wait 2 seconds for rails to stabilize
3. Connect micro-B J20 (hot-plug is OK)
4. Press power-on reset button (`PORz`) once
5. Wait 1 second before JTAG operations

### LED Status Indicators

| LED | Rail | Status |
|-----|------|--------|
| **LD6** | VDD | Should be green |
| **LD7** | VDDA | Should be green |
| **LD8** | VDDCORE (critical) | Should be green |

**If LD8 is OFF:** The SoC core rail is not powered. Check Type-C power supply quality or board power regulators.

### Jumpers

| Jumper | Purpose | Setting |
|--------|---------|---------|
| **J2** | JTAG VREF termination | **Must be installed** |
| **J18** | JTAG VREF alt | Install if present |

**If J2 is missing, JTAG will fail.** This provides the 1.8V termination voltage for the JTAG chain.

---

## Software Configuration

### TI Tools Required

- **CCS 2050** (CodeComposer Studio)
- **MCU+ SDK for AM243x** (version 12.00.00.26 or later)
- **UniFlash** (included with CCS)
- **loadti** (included with CCS scripting tools)

### Recommended Development Workflow

Use **VS Code as the main control surface** until a task actually needs CCS-only debug features.

**Normal workflow for this board:**

1. Edit source, notes, and scripts in VS Code.
2. Build with the checked-in PowerShell wrappers from this task folder.
3. Load and run over JTAG with `loadti`.
4. Watch UART on **COM10** and observe board behavior.
5. Only switch to CCS when low-level debug is needed.

**Use VS Code for:**

- source edits
- notes and runbooks
- build and load scripts
- UART monitoring
- repeated test loops

**Use CCS only for:**

- stepping through code
- breakpoints
- memory/register inspection
- multi-core target debug
- SysConfig or target config tasks that are easier in TI UI

**Current project-first path:**

```powershell
cd C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex

./ccs_control_center.ps1 -Action build-project
./ccs_control_center.ps1 -Action load-project
./ccs_control_center.ps1 -Action follow-uart
```

**Current LED driver workspace:**

- `C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project`
- active app: `mcspi_loopback.c`
- active output pin: **board pin 55 = SPI0_D0**

**Rule for this project:**

- If build/load/observe can be done from VS Code scripts, do it there first.
- If the problem goes past normal build/load/observe, move into CCS debug.

### JTAG Configuration File

**File Location:**
```
C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\am2434_xds110_generated.ccxml
```

**Key Properties:**
- JTAG Clock: 5.5 MHz (default, stable for this board)
- XDS110 Debug Probe connection
- AM2434_ALX device definition
- All 23 cores enumerated (R5F, PRU, M3, M4, debug cells)

**Do NOT use the 100 kHz config** (`am2434_xds110_100khz_usci.ccxml`). It is incompatible with this board revision and will cause Error -1170.

---

## Loading Bootloader & Code

### Recommended board flow

1. **One-time board prep:** set SW4 to `1110 0000` and flash SBL NULL over UART.
2. **Normal use after that:** set SW4 to `0100 0100` and power-cycle.
3. **Then** use JTAG/CCS or `loadti` to load applications.

### Via JTAG with loadti

**Command Template:**
```powershell
cd "C:/ti/ccs2050/ccs/ccs_base/scripting/examples/loadti"

.\loadti.bat `
  -c="C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/am2434_xds110_generated.ccxml" `
  -cpu=MAIN_Cortex_R5_0_0 `
  -l -r -v `
  "C:/ti/mcu_plus_sdk_am243x_12_00_00_26/examples/drivers/boot/sbl_jtag_uniflash/am243x-lp/r5fss0-0_nortos/ti-arm-clang/sbl_jtag_uniflash.release.out"
```

**Expected Output:**
```
TARGET: Texas Instruments XDS110 USB Debug Probe
Connecting to target...
...
log: Target has halted at 0x700061B4
Done
```

### Via CCS GUI

1. Open CCS 2050
2. Create new target configuration:
   - Board: AM243x LaunchPad
   - Connection: Texas Instruments XDS110 USB Debug Probe
   - Config: Select `am2434_xds110_generated.ccxml`
3. Connect to target
4. Load your binary via CCS Project → Load Program

---

## Troubleshooting

### Error -1170: Unable to access the DAP

**Cause 1: Using 100 kHz config (WRONG)**
- **Solution**: Use default-speed config (`am2434_xds110_generated.ccxml`)

**Cause 2: Power not stable**
- **Solution**: Verify LD8 is green; use quality 5V/3A power supply

**Cause 3: J2 VREF jumper missing**
- **Solution**: Install J2 jumper

**Cause 4: JTAG connector not properly seated**
- **Solution**: Reseat micro-B cable, try different USB port, test cable with multimeter

### Cores not enumerated

- Check JTAG cable connection
- Verify XDS110 drivers present in Device Manager
- Confirm `am2434_xds110_generated.ccxml` is being used

### Board not responsive at all

- Check Type-C power: measure 5V at board connector
- Check LD6, LD7, LD8 LED status
- Press PORz reset button after power connections
- If LEDs stay off after power cycle, board may be faulty (DOA)

---

## Key Lessons Learned

### What WORKED ✓
- Default 5.5 MHz JTAG clock (auto-generated config)
- Switch `0100 0100` (OSPI boot) for normal development
- Switch `1111 0000` only for raw No Boot / DEV attach when specifically needed
- Quality 5V/3A USB power supply
- Proper connection sequence: power first, then JTAG hot-plug
- Standard TI JTAG tools (loadti, uniflash)

### What DIDN'T WORK ✗
- 100 kHz JTAG config (incompatible with board, causes Error -1170)
- Weak USB power sources
- Other boot modes (USB-DFU, UART) for normal debug workflow
- Weak or damaged JTAG cables

---

## Verification Checklist

Before attempting JTAG operations:

- [ ] SW4 set to `0100 0100` for normal development
- [ ] If flashing over UART, temporarily set SW4 to `1110 0000`
- [ ] LD6, LD7, LD8 all green after power on
- [ ] Type-C power cable connected to quality 5V/3A source
- [ ] Micro-B J20 cable connected (after power stable)
- [ ] J2 VREF jumper installed
- [ ] CCS/TI tools configured
- [ ] `am2434_xds110_generated.ccxml` selected (NOT 100kHz variant)
- [ ] PORz reset pressed after connections stable

---

## File References

**Switch summary:**

- `1110 0000` = UART boot for flashing
- `0100 0100` = OSPI boot for normal work
- `1111 0000` = No Boot / DEV for special JTAG cases

**JTAG Configuration:**
- `am2434_xds110_generated.ccxml` (DEFAULT - 5.5 MHz) ← **USE THIS**
- `am2434_xds110_100khz_usci.ccxml` (DO NOT USE - incompatible)

**Bootloader Binary:**
```
C:\ti\mcu_plus_sdk_am243x_12_00_00_26\examples\drivers\boot\sbl_jtag_uniflash\
    am243x-lp\r5fss0-0_nortos\ti-arm-clang\sbl_jtag_uniflash.release.out
```

**TI Reference:**
- Stock CCS Board Definition: `C:\ti\ccs2050\ccs\ccs_base\common\targetdb\boards\AM243x_LP.xml`
- Device Definition: `C:\ti\ccs2050\ccs\ccs_base\common\targetdb\devices\AM2434_ALX.xml`
- XDS110 Connection Spec: `C:\ti\ccs2050\ccs\ccs_base\common\targetdb\connections\TIXDS110_Connection.xml`

---

## Last Updated
**Date**: 2026-05-04  
**Status**: ✓ Board verified operational, all tests passing  
**Resolution**: JTAG connectivity restored using default 5.5 MHz config

---

## UART Serial Monitor

### Ports
- **COM10** = XDS110 Application/User UART → use for console/monitoring
- **COM9** = XDS110 Auxiliary Data Port → use for UART flashing ONLY

### uart_monitor.py — timed mode (one-shot)
```powershell
# read 20s, exit 0
python scripts\uart_monitor.py --port COM10 --seconds 20

# pass/fail check (exit 2 if text not found)
python scripts\uart_monitor.py --port COM10 --seconds 20 --expect "BLINK"
```

### uart_monitor.py — follow mode (non-blocking, auto-reconnect)
```powershell
# runs until Ctrl-C; reconnects automatically if board resets or power-cycles
python scripts\uart_monitor.py --follow
python scripts\uart_monitor.py --follow --retry-interval 3.0

# from agentic loop:
.\scripts\agentic_dev_loop.ps1 -Action follow-uart
```

`--follow` mode **never** grabs the Auxiliary/flash port (COM9). Flash operations can proceed uninterrupted while follow-uart is watching COM10.

---

## GPIO Pin-Blink Demo (Blink-All-Pins)

Drives **all 10 available GPIO pins HIGH for 200 ms then LOW for 200 ms**, with UART print on every transition, running forever.

### GPIO Pins Used

| GPIO SDK Name | GPIO Num | Pad / Signal          | AM2434 Ball | Location on Board |
|---------------|----------|-----------------------|-------------|-------------------|
| GPIO_SWEEP0   | GPIO1_3  | PRG0_PRU0_GPO3        | H1          | J4 BoosterPack header |
| GPIO_SWEEP1   | GPIO1_4  | PRG0_PRU0_GPO4        | K2          | J4 BoosterPack header |
| GPIO_SWEEP2   | GPIO1_5  | PRG0_PRU0_GPO5        | F2          | J4 BoosterPack header |
| GPIO_SWEEP3   | GPIO1_6  | PRG0_PRU0_GPO6        | H2          | J4 BoosterPack header |
| GPIO_SWEEP4   | GPIO1_7  | PRG0_PRU0_GPO7        | E2          | J4 BoosterPack header |
| GPIO_SWEEP5   | GPIO1_38 | PRG0_PRU1_GPO18       | D1          | LD3 RED (on-board)  |
| GPIO_SWEEP6   | GPIO1_39 | PRG0_PRU1_GPO19       | F3          | LD3 GREEN (on-board)|
| GPIO_SWEEP7   | GPIO0_22 | GPMC0_AD7             | U19         | LD1 (on-board)     |
| GPIO_SWEEP8   | GPIO0_26 | GPMC0_AD11            | W20         | LD5 (on-board)     |
| GPIO_SWEEP9   | GPIO0_27 | GPMC0_AD12            | Y20         | LD4 (on-board)     |

**Pins skipped (by design):**
- EtherCAT / ICSSG PRU signals (J3 header SGMII / EtherCAT area)
- OSPI flash pins
- Boot/BOOTMODE pins
- JTAG/XDS110 interface pins
- Power and ground
- UART console pins (USART0 TXD/RXD used by the demo itself)

For exact J3/J4 connector pin numbers (physical silkscreen numbers), see **LP-AM243 User Guide SPRUJ12F**, Table 5-x (Connector J3/J4 Signal Descriptions) or the  
design package schematic at https://www.ti.com/lit/zip/SPRR433.

### Source location
```
C:\ti\mcu_plus_sdk_am243x_12_00_00_26\examples\drivers\gpio\gpio_led_blink\gpio_led_blink.c
```
Original backed up as `gpio_led_blink.c.orig`.

### Build
```powershell
.\scripts\agentic_dev_loop.ps1 -Action build-pin-blink
# or directly:
.\scripts\build-pin-blink.ps1
```

### Load and Monitor
```powershell
# full loop: build -> JTAG load -> print hint
.\scripts\agentic_dev_loop.ps1 -Action loop-pin-blink

# load only (skip build)
.\scripts\agentic_dev_loop.ps1 -Action load-pin-blink -SkipBuild

# then follow UART (auto-reconnect, non-blocking on COM9)
.\scripts\agentic_dev_loop.ps1 -Action follow-uart
```

### Expected UART output
```
============================================================
  LP-AM243 Blink-All-Pins Demo   (UART 115200 8N1)
============================================================
  10 pins configured as outputs:
    [ 0] GPIO1_3  PRG0_PRU0_GPO3       J4 header
    [ 1] GPIO1_4  PRG0_PRU0_GPO4       J4 header
    ...
  Phase: 200 ms HIGH / 200 ms LOW  (forever)
============================================================

[00001] HIGH  (5 header + LD1 LD3r LD3g LD4 LD5)
[00001] LOW
[00002] HIGH  (5 header + LD1 LD3r LD3g LD4 LD5)
[00002] LOW
```

---

## 2026-05-04 LED Pin Validation + Key Learnings

### Requested external LED pins (validation result)

- Dev board pin 23: `ADC0_AIN2` -> **not recommended** for WS2812 data output in this setup.
- Dev board pin 63: `PRG1_IEP0_EDC_SYNC_OUT0` -> **not recommended** for generic RGB LED drive.

These two pin choices were tested/checked and are not the stable demo path for this board workflow.

### Valid working demo path used

- 16x WS2812B chain: driven via SPI encoded waveform on `SPI0_D0` (J6 pin 55).
- 6x discrete RGB LEDs (parallel RGB lines): driven on `GPIO1_3`, `GPIO1_4`, `GPIO1_5`
  using `PRG0_PRU0_GPO3/4/5` (mapped in SysConfig as `CONFIG_GPIO_RGB_R/G/B`).

### Verified runtime behavior

- Pin sweep UART print demo now outputs:
  - `pin 1 high` ... `pin 80 high`
  - `all pins low`
- Verified on COM10 with timed UART capture (expect check passed).

### Switch/mode learning

- `0101 0000` may still allow JTAG load but can produce no useful UART runtime logs.
- `0100 0100` + power-cycle is the reliable normal mode for this development flow.

### Build/load caveat

- Some `gmake all` paths fail in signing stage if `openssl` is not in PATH.
- Building `*.release.out` directly and JTAG loading that `.out` remains a reliable fallback.
