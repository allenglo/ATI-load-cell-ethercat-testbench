# AM243x LP Boot, Reset, USB, and COM Reference

Date: 2026-05-27
Scope: LP-AM243 board behavior for flash, run, debug, and EtherCAT bring-up.

## Why this note exists

This is a consolidated reference for future agents so we stop re-learning boot switch and reset behavior every session.

It combines:
- Official TI docs (primary authority)
- Local project notes and observed host behavior
- TI E2E/forum clarifications (secondary authority)

## Boot switch SW4 meanings (official)

Board: LP-AM243
Switch block: SW4 (BOOTMODE [1:8])

| Mode | SW4 | Purpose | Confidence |
|---|---|---|---|
| UART boot | 1110 0000 | UART flash/boot via uart_uniflash | High |
| DFU boot | 1010 0000 | USB DFU flash/boot | High |
| OSPI boot | 0100 0100 | Normal retained boot from flash | High |
| DEV boot | 1111 0000 | CCS scripting / special debug init flow | High |

Important:
- 1111 0000 is valid, but it is DEV boot mode, not normal retained OSPI runtime mode.
- If 1111 0000 "historically worked", that usually means a DEV/JTAG load flow worked (not OSPI retained run flow).

## Practical mode guidance for this repo

| Task | SW4 | Power-cycle needed? |
|---|---|---|
| UART flash (uart_uniflash) | 1110 0000 | Yes |
| Run flashed firmware from OSPI | 0100 0100 | Yes |
| DEV scripting/JTAG init flow | 1111 0000 | Yes (on mode change or after cold power) |
| Standard day-to-day retained run | 0100 0100 | Usually no mode change once set |

Arduino-like "single switch for flash and retained run":
- Not supported in this TI flow.
- You flash in UART/DFU mode, then boot/run in OSPI mode.

## Reset controls and how to use them

Documented reset-related controls/signals found in TI references and mirrored board guide:
- PORz reset button/input (power-on-reset style reset)
- MCU warm reset input (MCU_RESETz)
- SoC warm reset request input (SoC_RESET_REQz)
- User interrupt button/input (not a reset)

Practical usage guidance:
- Use PORz when:
  - after cable changes
  - after boot mode switch change
  - board appears powered but software state is stale
- Use warm reset when:
  - you want quick software reset without full unplug/replug
  - boot mode is unchanged and rails are stable
- Use full power-cycle when:
  - changing SW4 mode
  - uart_uniflash says to power-cycle
  - XMODEM/UART handshake state becomes inconsistent
  - debug attach is stuck after repeated PORz attempts

Confidence on exact button naming/quantity: Medium
Reason: exact button labels were confirmed via mirrored user-guide text and TI E2E signal naming, but not extracted directly from TI-hosted PDF in this run.

## USB connectors, power, and COM ports

Local setup and TI docs alignment:
- USB-C power input is used for board power (5V, 3A recommended).
- XDS110 debug/UART path is through the debug USB connector (micro-B in local notes).

Observed Windows COM roles on this host:
- COM10: XDS110 Class Application/User UART (console/runtime logs)
- COM9: XDS110 Class Auxiliary Data Port (often used during flash workflows)

Operational rule used in this repo:
- Keep COM10 for runtime monitoring
- Use COM9/flash port only for flashing operations as needed by script

## Main board chip identity

LP-AM243 board SoC family: AM243x
Primary target in this workspace: AM2434 ALX

## Power and sequencing rules

- Use stable 5V/3A supply, avoid weak host-only USB power.
- Preferred connection order in local notes:
  1) board power
  2) wait rails stabilize
  3) debug USB
  4) PORz once
- If LD core power indicators are wrong, do not continue flashing/debugging.

## Common traps (official + local)

1. Wrong SW4 mode for the action.
2. Trying to run retained OSPI behavior while still in UART mode.
3. COM port held open by terminal during flash.
4. Confusing DEV boot success with retained flash success.
5. CCS v20+ scripting differences (legacy loadJSFile assumptions).

## Source list

Official TI:
- MCU+ SDK EVM setup (AM243x):
  https://software-dl.ti.com/mcu-plus-sdk/esd/AM243X/12_00_00_26/exports/docs/api_guide_am243x/EVM_SETUP_PAGE.html
- TI LP-AM243 tool page:
  https://www.ti.com/tool/LP-AM243

TI E2E (official community clarification):
- DEV boot/load_dmsc_hsfs.js FAQ and CCS v20 behavior:
  https://e2e.ti.com/support/processors-group/processors/f/processors-forum/1636272/faq-am2434-not-able-to-run-load_dmsc_hsfs-js-script-provided-with-the-mcu-sdk
- PORz timing discussion:
  https://e2e.ti.com/support/microcontrollers/arm-based-microcontrollers-group/arm-based-microcontrollers-forum/1067319/lp-am243-i-want-to-know-what-s-mean-about-the-delay-for-porz-is-set-10-41-ms

Local project references:
- AM243x master setup note:
  C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/AM243x_LAUNCHPAD_SETUP_MASTER.md
- Common issues loop:
  C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/notes/LP_AM243_COMMON_ISSUES_AND_AGENTIC_LOOP.md

Unofficial mirror used for extra board-detail hints (secondary confidence only):
- https://www.manualslib.com/manual/3051373/Texas-Instruments-Launchpad-Am243x.html

## Final policy for future agents in this repo

1. Treat official TI MCU+ boot table as source of truth for SW4 meanings.
2. Use 1110 0000 only for UART flash steps.
3. Use 0100 0100 for retained runtime validation.
4. Use 1111 0000 only when intentionally running DEV/JTAG init workflows.
5. Require power-cycle after any SW4 mode change.
