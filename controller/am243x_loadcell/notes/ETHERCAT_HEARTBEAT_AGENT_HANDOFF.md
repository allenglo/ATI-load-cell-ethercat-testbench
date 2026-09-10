# EtherCAT Heartbeat Handoff (AM243x LP)

Purpose: get from zero to "LED blinks + UART heartbeat proof" with minimum wasted time.

## Non-obvious baseline that must be true

- Board mode for this flow is DEV Boot: SW4 = 1111 0000.
- In DEV Boot, app-only load is fake-success often. Always do 2-step DSS load:
  1) sciclient_ccs_init.release.out
  2) ethercat_subdevice_simple_demo.release.out
- Use COM10 only for runtime UART proof. COM9 is XDS110 auxiliary and not for app logs.

## Code location and final behavior

- Main change file:
  C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/ecSubDeviceSimple.c
- Function changed: EC_SLV_APP_SS_applicationRun().
- Heartbeat output format:
  [HEARTBEAT #N] EC_State=0x1 LED=ON/OFF
- LED call used:
  EC_SLV_APP_SS_appBoardStatusLed(pApplicationInstace, hbLedState, false)

## Pitfalls that already cost time

- Do not trust "DSS success" alone; verify UART runtime banner and state change logs.
- Do not start UART monitor after load if you need startup evidence; start monitor first, then reload firmware.
- ESL_OS_clockGet() unit trap:
  - It returns whole seconds (ClockP_getTimeUsec()/1000000), not ms and not ns.
  - Threshold 500 or 500000000 is wrong for this API in this app context.
  - Working threshold used: (clock_t)1 (~1 second toggle).
- If heartbeat lines are missing but startup banner exists, likely timing threshold/unit bug, not transport bug.
- .appimage cp-step failures in this project are not blocking for JTAG+DSS run; .out is the required artifact.

## "Do NOT do" list

- Do not chase TI GitHub for a better heartbeat demo first; local SDK already has all required hooks.
- Do not rework LED driver layer; app-level callback is enough and already proven.
- Do not debug EtherCAT OP-state yet for this task; no TwinCAT master is installed, INIT-state proof is expected.
- Do not use a one-shot UART read command as proof source; use follow mode and capture multiple heartbeat lines.

## Fast re-validation steps

1) Build from:
   C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/am243x-lp/r5fss0-0_freertos/ti-arm-clang

2) Start monitor first:
   python C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/scripts/uart_monitor.py --port COM10 --baud 115200 --follow

3) Load step 1 then step 2 via DSS using:
   C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/scripts/dss_load_run_generic.js

4) Pass criteria:
   - state log: State change: 0x0 -> 0x1
   - repeated heartbeat logs with incrementing counter and ON/OFF alternation
   - visible status LED toggling on board

## Current known-good outcome snapshot

- Firmware loaded successfully with 2-step DEV boot.
- UART showed State change 0x0 -> 0x1.
- UART showed continuous heartbeat lines up to #56 in captured run.
- LED toggled continuously while EtherCAT stack stayed in INIT.
