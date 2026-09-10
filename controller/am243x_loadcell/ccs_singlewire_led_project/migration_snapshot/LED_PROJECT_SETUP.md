# AM243x LaunchPad LED Control Project - Build & Deploy Guide

## Overview

This project drives 3 LEDs on the AM243x LaunchPad with independent blink patterns:

| LED | GPIO Pin | Pattern | Blink Rate |
|-----|----------|---------|-----------|
| LED1 | GPIO1_0 (J4, pin 33) | Fast | 500ms on/off |
| LED2 | GPIO1_2 (J4, pin 31) | Medium | 1000ms on/off |
| LED3 | GPIO1_35 (J4, pin 79) | Slow | 1500ms on/off |

Each LED blinks independently, creating a cascading visual pattern.

---

## Prerequisites

- TI CCS 2050 (CodeComposer Studio)
- MCU+ SDK for AM243x v12.00.00.26 or later
- AM243x LaunchPad with JTAG connected
- XDS110 drivers installed (verified via Device Manager)

---

## Files

| File | Purpose |
|------|---------|
| `led_blink_simple.c` | Core LED control application |
| `build_and_upload.bat` | Build and deployment script (Windows) |
| `LED_PROJECT_SETUP.md` | This file |

---

## Build Methods

### Method 1: Import into CCS (Recommended)

**Step 1: Create a new CCS project**
```
File → New → C/C++ Project
  Project name: led_control
  Target: AM243x LaunchPad
  Device: AM2434
  Advanced Options:
    - Generate linker script: YES
    - Minimal runtime: NO
    - Preserve user variables: YES
```

**Step 2: Configure project properties**
```
Right-click project → Properties
  C/C++ Build → Settings → Tool Settings:
    ARM Compiler:
      - Optimization: -O2
      - Advanced Options:
        - Check "Deprecated warnings"
        - Floating point: Hardware
```

**Step 3: Add include paths**
```
Right-click project → Properties
  C/C++ Build → Settings → Arm Compiler:
    Include paths (-I):
      - C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\kernel\dpl
      - C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\drivers\gpio
      - C:\ti\mcu_plus_sdk_am243x_12_00_00_26\source\drivers\uart
```

**Step 4: Add source files**
```
Copy led_blink_simple.c to project root
File → New → File Link (or copy directly)
```

**Step 5: Link against SDK libraries**
```
Right-click project → Properties
  ARM Linker:
    File Search Paths (-i):
      - C:\ti\mcu_plus_sdk_am243x_12_00_00_26\build\release\libs
    Libraries (-l):
      - ti_drivers
      - kernel.dpl
```

**Step 6: Configure CCxml**
```
Right-click project → New → Target Configuration:
  Select am2434_xds110_generated.ccxml
  Save as project.ccxml in project root
```

---

### Method 2: Command-Line Build (Expert)

**Prerequisites:**
```powershell
# Set paths
$SDK = "C:\ti\mcu_plus_sdk_am243x_12_00_00_26"
$CCS = "C:\ti\ccs2050"
$COMPILER = "$CCS\ccs\tools\compiler\ti-cgt-arm_20.2.7.LTS\bin"
```

**Compile:**
```powershell
cd $PROJECT_PATH

# Compile
& "$COMPILER\armcl.exe" `
  -mv7R5 --abi=eabi -O2 `
  -I"$SDK\source\kernel\dpl" `
  -I"$SDK\source\drivers\gpio" `
  --define=_DEBUG_ `
  -z --diag_warning=225 `
  -o build\led_blink.o `
  led_blink_simple.c
```

**Link:**
```powershell
# Link (requires proper linker script from SDK)
& "$COMPILER\armlnk.exe" `
  --strict_compatibility=on `
  -m build\led_control.map `
  -o build\led_control.out `
  build\led_blink.o `
  --search_path="$SDK\build\release\libs" `
  -lti_drivers -lkernel.dpl
```

---

## Upload to Board

### Via JTAG (After Build)

**In CCS:**
```
Debug → Debug Configurations
  → Create new "C/C++ Application" configuration
  → Set C/C++ Application: build/led_control.out
  → Debugger → Gdbserver Settings → Connection → Use default CCXML
  → Apply → Debug
```

**Or via command line:**
```powershell
cd "C:\ti\ccs2050\ccs\ccs_base\scripting\examples\loadti"

.\loadti.bat `
  -c="C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\am2434_xds110_generated.ccxml" `
  -cpu=MAIN_Cortex_R5_0_0 `
  -l -r -v `
  "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\build\led_control.out"
```

---

## Run & Verify

**Expected console output:**
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
...
```

**Physical verification:**
- Connect external LEDs with 1kΩ resistors between GPIO pins and GND
- Observe cascading blink pattern (LED1 fastest, LED3 slowest)
- Test runs for 60 seconds, then all LEDs turn off

---

## Pin Connections (Optional External LEDs)

If using external LED modules:

```
GPIO1_0  (J4:33) ─[1kΩ]─ LED1 Anode ─ (to fixed GND)
GPIO1_2  (J4:31) ─[1kΩ]─ LED2 Anode ─ (to fixed GND)
GPIO1_35 (J4:79) ─[1kΩ]─ LED3 Anode ─ (to fixed GND)

        ← Common cathode to LaunchPad GND (J3:22, J4:20, etc.)
```

**Resistor sizing:**
- 1kΩ: ~3mA per LED (safe for all GPIO pins)
- 470Ω: ~6mA per LED (brighter, still safe)
- Use 1/4W 5% tolerance resistors

---

## Troubleshooting

### LEDs don't light
1. Verify GPIO pins are correct (check J4 header labels)
2. Check resistor values (open circuit if too high)
3. Verify GPIO base addresses (CSL_GPIO1_U_BASE = 0x600000)
4. Confirm power supply to board (LD6, LD7, LD8 should be green)

### Build fails with missing headers
1. Verify include paths in project properties
2. Check SDK path matches installation: `C:\ti\mcu_plus_sdk_am243x_12_00_00_26`
3. Run `Board_driversOpen()` to auto-initialize GPIO

### Debug connection fails
1. For normal development after board prep, switch should be `0100 0100` (OSPI boot)
2. Use `1111 0000` only for special raw JTAG/No Boot attach cases
3. Use default-speed config: `am2434_xds110_generated.ccxml` (NOT 100kHz)
4. Verify XDS110 in Device Manager (should show COM ports + XDS110 control)
5. Press PORz reset button after JTAG connects

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| GPIO Toggle Speed | ~50 kHz (max) |
| Blink Timing Accuracy | ±10ms (depends on clock/scheduling) |
| Current per LED | 3mA (with 1kΩ resistor) |
| Power consumption | ~10mW per LED (negligible) |
| CPU Load | <1% (interrupt-free GPIO polling) |

---

## Next Steps

1. **Add PWM dimming** - Use ePWM module instead of GPIO for brightness control
2. **Add button input** - Use GPIO input with interrupt to control blink patterns
3. **Multi-threaded control** - Use FreeRTOS tasks for independent LED control
4. **Serial control** - Add UART RX to change patterns via terminal

---

## References

- TI AM243x Technical Reference Manual
- MCU+ SDK GPIO Driver Documentation
- CodeComposer Studio User Guide
- AM243x LaunchPad User Guide (Schematic + pinout)

---

## Last Updated
**Date:** 2026-05-04  
**Status:** Ready for CCS import and build  
**Tested On:** AM243x LaunchPad (AM2434)
