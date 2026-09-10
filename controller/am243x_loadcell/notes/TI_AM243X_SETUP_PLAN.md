# TI AM243x Setup Plan

## Goal

Bring up the LP-AM243 on this Windows machine in a way that is easy to repeat from scripts and easy to inspect from plain files.

## Canonical hardware/boot reference

For current switch/reset/USB/COM behavior and source-backed meanings, use:

- `notes/AM243X_LP_BOOT_RESET_USB_REFERENCE.md`

This file is maintained as the future-agent baseline for SW4 meanings, reset strategy, and power-cycle rules.

## Known-good vendor assumptions from TI docs

- Install the AM243x MCU+ SDK under `C:\ti`.
- Install SysConfig `1.26.0` under `C:\ti`.
- Install TI ARM Clang `4.0.4.LTS` under `C:\ti`.
- Install CCS `20.4.0` and include the AM2x Arm MCU component.
- For CCS target config on this board, use `XDS110 USB Debug Probe` and select `AM243x_LAUNCHPAD`.

## Board-specific points

- LP-AM243 uses onboard XDS110 for debug and UART exposure.
- TI's docs say the board can be powered from the USB-C connector.
- TI's docs also support UART boot, DFU boot, OSPI boot, and DEV boot on the LaunchPad.
- LP-AM243 has no DDR, so any DDR-specific EVM setup steps do not apply.

## Preferred bring-up order

1. Confirm Windows still sees the board.
2. Install the SDK and tools.
3. Set `MCU_PLUS_SDK_AM243X_PATH`.
4. Build `hello_world` from the command line using `gmake`.
5. Use CCS for target configuration and JTAG load.
6. After basic load-and-run works, optionally try UART or DFU flash.

## Why makefile-first

- The makefile build is simple and documented by TI.
- It avoids hiding the first success inside a CCS workspace.
- It keeps the first demo path scriptable.

## First demo build command

From the SDK root, TI documents this flow for LaunchPad hello world:

`gmake -s -C examples/hello_world/am243x-lp/r5fss0-0_freertos/ti-arm-clang`

The expected application artifact is generated under the same example tree and is the input for later flash steps.

## JTAG path

Use CCS when you want the shortest bring-up path for a fresh board:

1. Install CCS and confirm SysConfig and TI Clang are visible in CCS preferences.
2. Create target config with `AM243x_LAUNCHPAD`.
3. Follow TI's one-time SoC init step for the LP board.
4. Load and run the hello world binary.
5. Watch the UART console for output.

## DFU path

DFU is useful later, but it adds Windows driver work:

- Install `dfu-util`.
- Use Zadig to bind the generic WinUSB driver when the board is in DFU mode.
- Use TI's `usb_dfu_uniflash.py` flow after the basic build succeeds.

## Current host status

- Board is connected and enumerating.
- UART interfaces are visible now.
- XDS110 CMSIS-DAP functions show error state now, so CCS or emulation driver install is likely still needed.