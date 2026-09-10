# LP-AM243 Common Issues and Agentic Development Loop

## Source references used

- TI LP-AM243 product page
- AM243x MCU+ SDK docs: EVM setup, CCS setup, flash tools
- TI E2E FAQ threads:
  - AM2434 UART Uniflash and OSPI flash programming
  - AM2434 load_dmsc_hsfs.js not working in CCS v20+
  - AM2434 custom flash attach database

## What repeatedly breaks on LP-AM243

1. Wrong SW4 boot setting for the current action.
2. UART flashing attempted while board is not in UART boot mode.
3. UART flashing attempted while COM port is held by terminal app.
4. JTAG load attempts before one-time SoC init (SBL NULL), causing memory write errors.
5. Using old loadJSFile flow in CCS Theia where loadJSFile is no longer supported.
6. Confusion between XDS110 Application/User UART and Auxiliary Data COM ports.
7. Custom flash parts not matching default flash config assumptions.

## Known-good switch settings (SW4)

- UART flash mode: 1110 0000
- OSPI normal run mode: 0100 0100
- DEV mode (special CCS init path): 1111 0000
- DFU mode (optional): 1010 0000

Power-cycle after each switch change.

## Correct one-time bring-up flow

1. Set SW4 to 1110 0000.
2. Power cycle.
3. Flash SBL NULL through UART.
4. Set SW4 to 0100 0100.
5. Power cycle.
6. Verify UART shows NULL bootloader banner.
7. Use JTAG load for day-to-day development.

## CCS v20+ note (important)

The E2E FAQ confirms loadJSFile in scripting console is not supported in latest CCS Theia releases. If you need DEV-mode SoC init, use the sciclient_ccs_init.out load-and-run method in DEV boot mode.

## Agentic loop commands in this repo

Use the loop script:

- Status only:
  - .\scripts\agentic_dev_loop.ps1 -Action status
- One-time SBL NULL flash:
  - .\scripts\agentic_dev_loop.ps1 -Action flash-sbl-null
- Full build/load/verify loop:
  - .\scripts\agentic_dev_loop.ps1 -Action loop
- UART verification only:
  - .\scripts\agentic_dev_loop.ps1 -Action monitor-uart -ExpectText "Hello World"

## Notes on expected failures

- If JTAG load fails with Error -1065 writing memory at 0x0:
  - Verify SW4 is 0100 0100 for normal mode.
  - Power cycle board.
  - Reconnect/debug again.
  - If still failing, re-run one-time SBL NULL flash path.

- If UART flash stalls at 0%:
  - SW4 is not in UART mode, or wrong COM port, or COM port is busy.
  - Close serial terminals and retry.

## Custom flash users

For non-default flash devices, use TI E2E custom flash attach database values and validate with the OSPI flash IO example before production flashing.
