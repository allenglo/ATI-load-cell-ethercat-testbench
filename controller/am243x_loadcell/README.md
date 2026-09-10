# TI AM243x LaunchPad — Knowledge Base

Complete bring-up guide and knowledge base for the **LP-AM243** (AM2434 LaunchPad) board. Covers toolchain install, build, flash, and JTAG load — all from the command line on Windows.

## EFlex Peripheral State: Start Here

This folder contains both active EFlex interface work and older board/LED experiments. Use this table before selecting a tool or interpreting a result.

| Lane | Current state | Start here | Do not assume |
|---|---|---|---|
| EEA direct interface | Locally live-validated serial lane: RS-485 Modbus RTU on COM18, 115200/E/1; slaves 1-3 respond. | `notes/host_master/MASTERNOTES_EEA_GUI_WORKFLOW.md`, `scripts/eea_testbench_gui.py` | Slave 4/ROI is present on this direct lane; unknown register writes are safe. |
| EEA/ROI gateway model | Local gateway XML and bridge code map EtherCAT PDO fields to EEA/ROI Modbus windows. | `notes/host_master/EEA_COMPLETE_REGISTER_AND_FRAME_CATALOG.md`, `demo/eea_gateway_bridge/README.md` | Recovered packing, endpoint availability, or gateway identity is a released production contract. |
| ATI load cell | Local host-side EtherCAT tools have observed the ATI lane and decode a tentative six-channel input frame. | `notes/host_master/README.md`, `scripts/ati_ft_testbench.py`, `scripts/launchpad_loadcell_live_gui.py` | Host-side scale/calibration, tare, object dictionary, or device ordering is production truth. |
| ROI / status LEDs | Gateway-level ROI fields are documented; AM243x WS2812/Dialight and ESP32-S3 work are useful reference experiments. | `notes/host_master/EEA_COMPLETE_REGISTER_AND_FRAME_CATALOG.md`, `LED_PROJECT_INDEX.md`, `firmware_snapshots/ESP32S3-WROOM-OLED-W25Q128-Test_20260610_121028/` | Any local LED experiment is the released Ring of Information firmware or hardware interface. |

### Directory Rules

- `scripts/`: executable probes, GUIs, and host tools. Check each script header before use.
- `notes/host_master/`: current EEA/ATI facts, captures, and operating pitfalls.
- `demo/eea_gateway_bridge/`: hardware-agnostic EEA/ROI conversion reference.
- `ccs_singlewire_led_project/`: AM243x CCS workspace with mixed LED, EtherCAT, and copied experiments; inspect its local README before changes.
- `firmware_snapshots/`: point-in-time imported reference code. It is not an active release branch.
- `reports/`: dated outputs; do not edit prior evidence.
- `external/`: imported source mirrors; do not modify as part of a local experiment.

For controller modernization, preserve the distinction between **current-state evidence**, **reference experiments**, and **unverified production interfaces**. Do not use these materials to change KRC5, PLC/PROFIsafe, power, battery, or motion behavior without a separate approved assignment.

---

## Board

| Item | Value |
|---|---|
| Board | LP-AM243 (AM2434, 11×11 package) |
| Debug probe | Onboard XDS110 |
| UART via | XDS110 USB CDC (Application/User UART, plus Auxiliary Data port on many Windows hosts) |
| USB VID/PID | `0451:BEF3` |
| Windows COM ports | Usually two ports: Application/User UART and Auxiliary Data; names vary by host |
| No DDR | LP has no DDR memory — EVM DDR steps do not apply |

---

## Installed toolchain (Windows, `C:\ti`)

| Tool | Version | Path |
|---|---|---|
| AM243x MCU+ SDK | 12.00.00.26 | `C:\ti\mcu_plus_sdk_am243x_12_00_00_26` |
| CCS | 20.5.0.00028 | `C:\ti\ccs2050` |
| TI ARM Clang | 4.0.4.LTS | `C:\ti\ccs2050\ccs\tools\compiler\ti-cgt-armllvm_4.0.4.LTS` |
| SysConfig | 1.27.0 | `C:\ti\ccs2050\ccs\utils\sysconfig_1.27.0` |
| gmake | (bundled with CCS) | `C:\ti\ccs2050\ccs\utils\bin\gmake.exe` |
| DSLite | (bundled with CCS) | `C:\ti\ccs2050\ccs\ccs_base\DebugServer\bin\DSLite.exe` |
| OpenSSL | Git-bundled | `C:\Program Files\Git\usr\bin\openssl.exe` |
| Python | 3.14 venv | `c:\CoRoot\.venv\Scripts\python.exe` |
| Python packages | construct, pyelftools, xmodem | in the venv |

### SysConfig fix (required once)

CCS ships SysConfig without a `nodejs` subfolder. Copy the bundled node:

```powershell
Copy-Item 'C:\ti\ccs2050\ccs\tools\node\node.exe' `
    'C:\ti\ccs2050\ccs\utils\sysconfig_1.27.0\nodejs\node.exe' -Force
```

---

## SDK installer download

```
https://dr-download.ti.com/software-development/software-development-kit-sdk/MD-ouHbHEm1PK/12.00.00.26/mcu_plus_sdk_am243x_12_00_00_26-windows-x64-installer.exe
```

---

## Boot mode switch (SW4 on LP-AM243)

SW4 bits are numbered 1–8 left to right. `1` = ON, `0` = OFF.

| Mode | SW4 setting | When to use |
|---|---|---|
| **UART boot** | `1110 0000` | Flashing via `uart_uniflash.py` |
| **OSPI boot** | `0100 0100` | Running apps previously flashed to OSPI |
| **DEV boot** | `1111 0000` | CCS scripting SOC init (`load_dmsc_hsfs.js`) |
| DFU boot | `1010 0000` | USB DFU flashing (optional) |

> **Board must be power-cycled after changing any switch.**

---

## Build any example (command line)

```powershell
$env:PATH = 'C:\Program Files\Git\usr\bin;' + $env:PATH   # for OpenSSL

$sdk  = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26'
$make = 'C:\ti\ccs2050\ccs\utils\bin\gmake.exe'

& $make -s -C <example_path> `
    CCS_PATH=C:/ti/ccs2050/ccs `
    TOOLS_PATH=C:/ti `
    SYSCFG_PATH=C:/ti/ccs2050/ccs/utils/sysconfig_1.27.0 `
    PYTHON=c:/CoRoot/.venv/Scripts/python.exe
```

Replace `<example_path>` with the example folder relative to the SDK root.

### Built examples

| Example | Example path (under SDK `examples/`) | Output |
|---|---|---|
| hello_world | `hello_world/am243x-lp/r5fss0-0_freertos/ti-arm-clang` | `hello_world.release.out` |
| gpio_led_blink | `drivers/gpio/gpio_led_blink/am243x-lp/r5fss0-0_nortos/ti-arm-clang` | `gpio_led_blink.release.out` |
| adc_singleshot | `drivers/adc/adc_singleshot/am243x-lp/r5fss0-0_freertos/ti-arm-clang` | `adc_singleshot.release.out` |

Build produces `.out` (ELF), `.mcelf` (MulticoreELF), and `.mcelf.hs_fs` (signed, flashable).

### Manual signing (if the makefile hs_fs target fails)

```powershell
$sdk = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26'
$py  = 'c:\CoRoot\.venv\Scripts\python.exe'

& $py "$sdk\tools\boot\signing\appimage_x509_cert_gen.py" `
    --bin   <example>.release.mcelf `
    --key   "$sdk\tools\boot\signing\rom_degenerateKey.pem" `
    --output <example>.release.mcelf.hs_fs `
    --swrv 1 --loadaddr 0x70000000 --sign_key_id 0 --imageType APPIMAGE
```

---

## One-time SOC init (flash SBL NULL) — required before CCS JTAG loading

This must be done **once** per board. It puts a null bootloader in OSPI flash so CCS can connect without running the DMSC JS script every time.

1. Power OFF board
2. Set **SW4 = `1110 0000`** (UART boot)
3. Power ON board — you should see `C` printed on the serial terminal every 2–3 s
4. Run:
   ```powershell
   .\scripts\flash_and_test.ps1 -Action flash-sbl-null -Port COM9
   ```
5. Wait for `[STATUS] SUCCESS` and `All commands from config file are executed!`
6. Power OFF board
7. Set **SW4 = `0100 0100`** (OSPI boot)
8. Power ON board — UART terminal should show `Starting NULL Bootloader ...`

After this, you do **not** need to change switches again for normal CCS development.

---

## Load and run via CCS JTAG (recommended dev flow)

### Target configuration

The file `am243x_lp_xds110.ccxml` in this repo is the CCS target config for the LP-AM243 with XDS110.

In CCS:
1. **View → Target Configurations**
2. Right-click in the panel → **Import** → select `am243x_lp_xds110.ccxml`
3. Right-click the config → **Launch Selected Configuration**

### Load a program

1. In the Debug window, right-click `MAIN_Cortex_R5_0_0` → **Connect Target**
2. Right-click → **Reset**
3. Right-click → **Load** → **Load Program** → browse to the `.out` file
4. Click **Resume (F8)**
5. Watch output on UART terminal (COM9, 115200, 8N1)

### Expected outputs

| Program | UART output |
|---|---|
| hello_world | `Hello World! - over UART` |
| gpio_led_blink | LED blinks; no UART (nortos, no console init) |
| adc_singleshot | ADC conversion results printed every second |

---

## Flash an app to OSPI (run standalone without CCS)

Use `scripts\flash_and_test.ps1`:

```powershell
# Flash SBL NULL (one-time setup):
.\scripts\flash_and_test.ps1 -Action flash-sbl-null -Port COM9

# Flash gpio_led_blink:
.\scripts\flash_and_test.ps1 -Action flash-led-blink -Port COM9

# Flash hello_world:
.\scripts\flash_and_test.ps1 -Action flash-hello-world -Port COM9

# Build adc_singleshot:
.\scripts\flash_and_test.ps1 -Action build-adc
```

Board must be in **UART boot mode** for any flash action.
After flashing, switch to **OSPI boot mode** and power cycle to run the app.

---

## UART terminal settings

| Setting | Value |
|---|---|
| Port | Application/User UART COM port (check Device Manager) |
| Baud | 115200 |
| Data | 8 bits |
| Parity | None |
| Stop | 1 bit |
| Flow | None |

---

## Agentic Development Loop (Automated)

This repo now includes an automation loop script that performs preflight checks, JTAG load, and UART verification in one flow:

```powershell
# Status / detection only
.\scripts\agentic_dev_loop.ps1 -Action status

# One-time SoC init flash (board must be SW4=1110 0000)
.\scripts\agentic_dev_loop.ps1 -Action flash-sbl-null

# Full development loop: build hello_world, JTAG load, verify UART prints
.\scripts\agentic_dev_loop.ps1 -Action loop

# UART-only check
.\scripts\agentic_dev_loop.ps1 -Action monitor-uart -ExpectText "Hello World"
```

Supporting script improvements:

- `scripts\uart_monitor.py` now supports `--port AUTO` and `--expect` for pass/fail automation.
- `scripts\agentic_dev_loop.ps1` auto-detects XDS110 COM ports and gives explicit recovery hints for common failures.

---

## Common Online-Reported Issues (TI Docs + E2E FAQ)

1. Wrong boot-mode switch for the current operation.
2. UART flash hanging at 0% because board is not in UART mode or COM is busy.
3. JTAG load memory write failures (for example Error -1065) due to missing SoC init / wrong mode / stale power state.
4. `loadJSFile` flow no longer supported in latest CCS Theia releases; use supported SoC init flow instead.
5. Custom flash parts requiring explicit flash parameter tuning (QE/protocol/dummy clocks/etc.).

See details in:

- `notes\LP_AM243_COMMON_ISSUES_AND_AGENTIC_LOOP.md`

---

## Environment variable

Set once so TI CCS scripting tools can find the SDK:

```powershell
[System.Environment]::SetEnvironmentVariable(
    'MCU_PLUS_SDK_AM243X_PATH',
    'C:\ti\mcu_plus_sdk_am243x_12_00_00_26',
    'User'
)
```

---

## Repo structure

```
am243x_lp_xds110.ccxml     CCS target configuration (XDS110 + AM243x_LAUNCHPAD)
README.md                  This file
demo/
  gpio_led_blink_uart_ospi.cfg   UART flash config for gpio_led_blink
scripts/
  flash_and_test.ps1       Main automation script (build, sign, flash)
  build-hello-world.ps1    Quick hello world build
  check-ti-launchpad.ps1   Check board USB/COM port visibility
  set-am243x-env.ps1       Set MCU_PLUS_SDK_AM243X_PATH env var
notes/
  TI_AM243X_SETUP_PLAN.md  Original setup plan
  CONFLUENCE_EFLEX_OVERVIEW.md  eFlex system context
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `uart_uniflash.py` hangs at 0% | Board is not in UART boot mode — check SW4 |
| `Serial port not accessible` | Another process owns the COM port — close terminal apps |
| SysConfig fails `node not found` | Copy node.exe shim (see SysConfig fix above) |
| JTAG connect fails | Power cycle the board, reconnect JTAG cable after power-on |
| `construct` / `pyelftools` import error | `pip install construct pyelftools xmodem` in the venv |
| Signing step fails (hs_fs target) | Run manual signing command above with `rom_degenerateKey.pem` |

---

## References

- [AM243x MCU+ SDK 12.00 docs](https://software-dl.ti.com/mcu-plus-sdk/esd/AM243X/12_00_00_26/exports/docs/api_guide_am243x/index.html)
- [EVM Setup (boot modes, cables)](https://software-dl.ti.com/mcu-plus-sdk/esd/AM243X/12_00_00_26/exports/docs/api_guide_am243x/EVM_SETUP_PAGE.html)
- [CCS Setup (target config)](https://software-dl.ti.com/mcu-plus-sdk/esd/AM243X/12_00_00_26/exports/docs/api_guide_am243x/CCS_SETUP_PAGE.html)
- [CCS Launch, Load and Run](https://software-dl.ti.com/mcu-plus-sdk/esd/AM243X/12_00_00_26/exports/docs/api_guide_am243x/CCS_LAUNCH_PAGE.html)
- [Flash tools](https://software-dl.ti.com/mcu-plus-sdk/esd/AM243X/12_00_00_26/exports/docs/api_guide_am243x/TOOLS_FLASH.html)

---

## Webcam Validation Plan (Functions + Colors)

Use this plan to verify firmware behavior with camera evidence and auto-generated reports.

1. Build and load the LED demo firmware.
2. Start webcam + UART validator.
3. Detect firmware activity from UART logs (`[DEMO]`, `[RGBx6] Step ...`).
4. Detect color states from webcam ROI(s).
5. Generate PASS/FAIL report files.

### New files

- `webcam_led_validator.py` - Core validator (camera + serial + report writer)
- `run_webcam_validation.ps1` - One-command launcher

### Quick run

From this task folder:

```powershell
# Simulation test (no hardware required)
.\run_webcam_validation.ps1 -Simulate

# Real hardware validation, run build+load first
.\run_webcam_validation.ps1 -BuildAndLoad -CameraIndex 0 -SerialPort COM10 -DurationSec 25 -ShowPreview
```

### ROI setup

If you want explicit regions for strip and discrete LEDs, pass repeatable `-Roi` args:

```powershell
.\run_webcam_validation.ps1 -BuildAndLoad -Roi "rgb:80,120,180,180" -Roi "strip:320,100,260,200"
```

Format: `name:x,y,w,h`

### Report output

Every run writes a timestamped folder under:

- `reports\webcam_validation_YYYY-MM-DD_HH-MM-SS\validation_report.json`
- `reports\webcam_validation_YYYY-MM-DD_HH-MM-SS\validation_report.txt`

PASS requires:

- UART function markers detected (start + enough RGB steps)
- Expected colors detected in each ROI
- Webcam opened and frames captured
