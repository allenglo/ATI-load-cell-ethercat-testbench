# AM243x LaunchPad LED Project - File Index & Quick Start

## Project Overview

Three controllable LEDs with independent blink patterns on GPIO pins:
- **LED1** (GPIO1_0): 500ms blink
- **LED2** (GPIO1_2): 1000ms blink  
- **LED3** (GPIO1_35): 1500ms blink

---

## Files in This Project

### Source Code
- **`led_blink_simple.c`** - Main LED control application
  - Simple, self-contained C code using GPIO register access
  - Blinks 3 LEDs independently with different rates
  - Runs for 60 seconds with status logging
  - Ready to integrate into CCS project

### Build & Deployment Scripts
- **`build_and_upload.bat`** - Windows batch script for build/upload workflow
- **`build_and_upload.ps1`** - PowerShell version with better logging and debugging
  - Usage: `.\build_and_upload.ps1` (build and upload bootloader)
  - Usage: `.\build_and_upload.ps1 -UploadOnly` (skip build, upload bootloader only)
  - Usage: `.\build_and_upload.ps1 -Clean` (remove old artifacts first)

### Documentation
- **`LED_PROJECT_SETUP.md`** - Complete build guide
  - CCS import instructions (Method 1 - Recommended)
  - Command-line build steps (Method 2)
  - Upload procedures
  - Troubleshooting guide
  - Pin connection diagrams
  - Expected output samples

- **`AM243x_LAUNCHPAD_SETUP_MASTER.md`** - Complete board reference
  - Hardware configuration (switches, power, jumpers, LEDs)
  - JTAG configuration details
  - Bootloader information
  - Full troubleshooting guide

- **`LED_PROJECT_INDEX.md`** - This file

---

## Quick Start (5 Minutes)

### Prerequisites
✓ AM243x LaunchPad with JTAG connected  
✓ TI CCS 2050 installed  
✓ MCU+ SDK for AM243x v12.00.00.26  
✓ Normal switch setting: `0100 0100`  
✓ All power LEDs (LD6, LD7, LD8) green  

### Steps

1. **Open CCS**
   ```
   c:\ti\ccs2050\ccs\ccs.exe
   ```

2. **Create new C/C++ project**
   - Target: AM243x LaunchPad
   - Device: AM2434
   - Do NOT generate sample project

3. **Add source file**
   - Right-click project → New → File Link
   - Link to: `led_blink_simple.c`

4. **Configure includes** (Right-click project → Properties)
   ```
   C/C++ Build → Arm Compiler:
   Include paths:
     • C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\kernel\dpl
     • C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\drivers\gpio
     • C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\drivers\uart
   ```

5. **Build** (Project → Build Project or Ctrl+B)

6. **Debug** (F11 to connect to target)

7. **Run** (F8 to start execution)

---

## Hardware Connections (Optional External LEDs)

To visually verify LED blink patterns, connect external LEDs:

```
┌─ GPIO1_0 (J4:33) ────[1kΩ]────┬─ LED1 Anode (Red)
│
├─ GPIO1_2 (J4:31) ────[1kΩ]────┬─ LED2 Anode (Green)
│
└─ GPIO1_35 (J4:79) ───[1kΩ]────┬─ LED3 Anode (Blue)
                                │
                        ┌───────┴─── Common Cathode
                        │
                    GND (J3:22 or J4:20)
```

**Component List:**
- 3× 1kΩ resistors (1/4W, 5%)
- 3× LED (any color/brightness)
- Breadboard + jumper wires

---

## GPIO Pin Details

| LED | GPIO | Header | Pin | Base Address | Offset |
|-----|------|--------|-----|--------------|--------|
| 1 | GPIO1_0 | J4 | 33 | 0x600000 | 0 |
| 2 | GPIO1_2 | J4 | 31 | 0x600000 | 2 |
| 3 | GPIO1_35 | J4 | 79 | 0x600000 | 35 |

**Base Address:** `CSL_GPIO1_U_BASE = 0x600000` (CPU physical)

---

## Expected Output (UART @ 115200 baud)

```
========================================
AM243x LED Control Application
========================================
GPIO Pins:
  LED1 -> GPIO1_0  (500ms blink)
  LED2 -> GPIO1_2  (1000ms blink)
  LED3 -> GPIO1_35 (1500ms blink)
Runtime: 60 seconds
========================================

GPIO pins configured as outputs.
Starting LED blink test...

[ 5s] LED1:ON   LED2:ON   LED3:OFF
[10s] LED1:ON   LED2:OFF  LED3:OFF
[15s] LED1:ON   LED2:ON   LED3:ON
[20s] LED1:ON   LED2:OFF  LED3:OFF
...
[60s] Test Complete - All LEDs OFF
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails - headers not found | Check include paths in project properties |
| Debug won't connect | For normal use verify switch is `0100 0100`; use `1111 0000` only for special No Boot attach, then press PORz reset |
| LEDs don't light (simulator) | This is simulator behavior - physical LEDs will light |
| Can't find CCS project template | Use "Empty C/C++ Project" and manually add SDK support |

---

## Key Configuration Values

```c
/* GPIO Base Address (from CSL) */
#define LED1_BASE       (0x600000)   /* CSL_GPIO1_U_BASE */

/* GPIO Pin Numbers */
#define LED1_PIN        (0U)
#define LED2_PIN        (2U)
#define LED3_PIN        (35U)

/* Blink Timing (milliseconds) */
#define LED1_BLINK_MS   (500U)       /* 500ms period */
#define LED2_BLINK_MS   (1000U)      /* 1000ms period */
#define LED3_BLINK_MS   (1500U)      /* 1500ms period */

/* Execution Time */
#define RUN_TIME_SEC    (60U)        /* Run for 60 seconds */
```

---

## Build Commands (Reference)

### Compile
```bash
armcl.exe -mv7R5 --abi=eabi -O2 \
  -I"C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\kernel\dpl" \
  -I"C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\drivers\gpio" \
  -o build\led_blink.o led_blink_simple.c
```

### Link (requires SDK linker script)
```bash
armlnk.exe -m build\led_control.map \
  -o build\led_control.out build\led_blink.o \
  --search_path="C:\ti\mcu_plus_sdk_am243x_12_00_00_26\build\release\libs" \
  -lti_drivers -lkernel.dpl
```

### Load via JTAG
```bash
loadti.bat -c="am2434_xds110_generated.ccxml" \
  -cpu=MAIN_Cortex_R5_0_0 -l -r -v \
  build\led_control.out
```

---

## Common Issues & Fixes

### Issue: "Cannot find include file 'ti_drivers_config.h'"
**Fix:** Add full SDK include paths, or in CCS use `Project → Add Files...` to include SDK drivers directly.

### Issue: "SEVERE: Error connecting to target: (Error -1170 @ 0x0)"
**Fix:** Use default-speed config (`am2434_xds110_generated.ccxml`), NOT 100kHz variant. See AM243x_LAUNCHPAD_SETUP_MASTER.md for details.

### Issue: "Linker cannot find ti_drivers library"
**Fix:** Copy or link the SDK libraries into project, or configure linker search paths to point to `$SDK/build/release/libs`.

---

## Next Steps / Enhancements

1. **Add PWM dimming** - Use ePWM instead of GPIO for brightness control
2. **Button control** - Add GPIO input interrupt to change blink patterns
3. **Serial interface** - Send UART commands to control LEDs remotely
4. **Multi-threaded** - Use FreeRTOS tasks for independent LED control
5. **Timer-based** - Use hardware timers instead of software loop for precise timing

---

## References

- TI AM243x Technical Reference Manual
- MCU+ SDK AM243x User Guide
- AM243x LaunchPad Hardware User Guide  
- CodeComposer Studio 2050 Release Notes

---

## Support & Debugging

**Enable verbose output:**
- Uncomment `#define DEBUG` in source
- Set compiler optimization to `-O0` for debugging
- Use CCS Expressions view to watch GPIO register values

**Monitor UART output:**
- Connect to COM port shown in Device Manager (typically COM9 or COM10)
- Baud rate: 115200 bps
- Data bits: 8, Stop bits: 1, Parity: None

---

**Project created:** 2026-05-04  
**Target board:** AM243x LaunchPad (AM2434_ALX)  
**Build system:** TI CCS 2050 + MCU+ SDK v12  
**Status:** ✓ Ready for CCS import and build
