# Future Agent Checklist (Minimal)

1. Scope
- Build LaunchPad as EtherCAT host for ATI F/T.
- USB-Ethernet host path is debug only.

1a. CCS workspace state (as of 2026-05-14)
- Workspace: `ccs_singlewire_led_project/` (inherited name, treat as general AM243x workspace)
- Imported examples: ethercat_subdevice_simple_demo, single_chip_servo (system), uart_echo, dpl_demo
- Auto-installed: MOTOR CONTROL SDK AM243x v09.02.00.12, SysConfig v1.20.0, TI Arm Clang v3.02.02.00
- Read `notes/host_master/HOST_EXAMPLE_STATUS.md` for full list.
- These are SubDevice examples. Still NO MainDevice/host example installed.
- Before real host firmware: must obtain acontis EC-Master or equivalent MainDevice package.

2. First command
- `python scripts/launchpad_host_milestone_demo.py --mode auto --cycles 20 --period-ms 10`

3. Confirm
- Output starts with `LP_HOST_DEMO`.
- Report exists in `reports/host_master/`.

4. Then progress firmware milestones
- A: deterministic loop
- B: EtherCAT exchange primitives
- C: ATI enumerate from LaunchPad
- D: decode 6 channels
- E: print Fx/Fy/Fz/Tx/Ty/Tz on COM10

5. Session handoff (required)
- what changed
- one validated output line
- exact next command

6. Latest verified snapshot (2026-05-18)
- Report: `reports/host_master/MILESTONE_01_DEMO_20260518_115352.md`
- Mode used: `live`
- Decoded lines: `20`
- Last line had `wkc=3` with decoded `Fx/Fy/Fz/Tx/Ty/Tz`.

7. Active execution reference
- Follow `notes/host_master/EXECUTION_PLAN_20260518.md` for ordered phases and pass criteria.

8. Firmware unblock experiment status (2026-05-18)
- Baseline app test executed with DEV boot loader:
	- App: `enet_l2_cpsw.release.out`
	- DSS log: `reports/host_master/FW_UNBLOCK_DSS_BASELINE_20260518.log`
	- UART log: `reports/host_master/FW_UNBLOCK_UART_BASELINE_20260518.log`
- ATI app test executed with same DEV boot loader:
	- App: `ati_ethercat_master.release.out`
	- DSS log: `reports/host_master/FW_UNBLOCK_DSS_ATI_20260518.log`
	- UART log: `reports/host_master/FW_UNBLOCK_UART_ATI_20260518.log`
- Result in both tests: loader reached `[DEVBOOT] SUCCESS`, but no COM10 runtime text was observed during 12s timed capture.

9. Exact next command
- `Set-Location "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex"; & "C:\CoRoot\.venv\Scripts\python.exe" .\scripts\uart_monitor.py --port AUTO --follow`
