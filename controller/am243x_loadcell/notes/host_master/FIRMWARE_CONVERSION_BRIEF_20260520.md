# Firmware Conversion Brief (2026-05-20)

Purpose:
- Support firmware work replacing the off-the-shelf EtherCAT-to-serial adapter for EEA.
- Summarize what is already known in software, toolchain background, and where to look next.

## 1) Current Software Findings

1. The task repo already has two lanes:
- Host validation lane (Windows + pysoem) for quick EtherCAT proof.
- LaunchPad firmware lane (AM243x, CCS projects) for on-device replacement.

2. Host validation lane is proven and stable:
- `launchpad_host_milestone_demo.py` outputs decoded force/torque style lines and writes reports.
- Typical run currently reports stable WKC=3 in known-good adapter path.

3. Firmware lane has known blocker:
- Existing installed industrial SDK content exposes EtherCAT subdevice/slave examples, not a ready EtherCAT main-device/host example.
- This is explicitly captured by local readiness checks and host notes.

4. Existing custom firmware app exists and is relevant:
- `ati_ethercat_master.c` implements a SOEM-based polling loop, ATI slave detection, tare, and periodic telemetry print.
- This is a good reference for expected runtime loop behavior and UART output contract.

5. Unified GUI exists for reverse engineering and control:
- `launchpad_loadcell_live_gui.py` supports two profiles: ATI Load Cell and EEA Reverse Engineering.
- Includes PDO write + SDO read/write hooks, useful for protocol mapping while firmware is in parallel development.

## 2) Toolchain Background (what is already set up)

1. Core TI stack in use:
- MCU+ SDK AM243x 12.00.00.26
- CCS 20.5.0
- TI ARM Clang (project uses CCS-bundled toolchains)
- SysConfig available

2. Python stack for host/probe tooling:
- `pysoem==1.1.13`
- `scapy==2.7.0`
- `numpy`, `pandas`

3. Board/debug conventions already documented:
- SW4 mode switching and JTAG/UART workflows are captured in setup docs.
- COM10 is used as runtime UART proof path in most notes.

## 3) What This Means For The Firmware Agent

1. Do not assume host support from subdevice examples.
- Local notes are consistent: subdevice/slave examples are present; main-device/host template is not.

2. Keep host pysoem path as regression only.
- Useful for validating ATI/EEA behavior and expected data semantics, but not the final replacement architecture.

3. Reuse runtime output contract early.
- Keep one-line deterministic UART output for Fx/Fy/Fz/Tx/Ty/Tz (or equivalent EEA fields) to simplify bring-up comparisons.

4. Use existing app as reference implementation structure.
- `ati_ethercat_master.c` already has practical patterns for scan/init/cyclic IO/tare/status prints.

## 4) Priority "Where To Look Further"

Priority A (immediate, highest value):
1. `ccs_singlewire_led_project/ati_ethercat_master/app/ati_ecat_master.c`
- Existing app loop and ATI slave handling.
- Use as baseline for firmware architecture and UART telemetry format.

2. `notes/host_master/HOST_EXAMPLE_STATUS.md`
- Fast truth source on why host firmware path is blocked with current installed examples.

3. `scripts/check_launchpad_host_readiness.ps1`
- Quick environment sanity script to avoid repeating false starts.

Priority B (protocol mapping + validation support):
4. `scripts/launchpad_loadcell_live_gui.py`
- EEA reverse-engineering profile, CSV capture, PDO/SDO control hooks.

5. `scripts/ethercat_switch_scan.py` and `scripts/ethercat_raw_probe.py`
- Topology and adapter path diagnostics.

6. `scripts/ati_ft_testbench.py`
- Stable host reference for cyclic data reads and expected timing behavior.

Priority C (toolchain and build flow hygiene):
7. `README.md` and `AM243x_LAUNCHPAD_SETUP_MASTER.md`
- Canonical board mode, flashing, and JTAG process.

8. `scripts/build_ati_ethercat_cli.py`
- Current non-GUI build invocation and expected output artifact checks.

Priority D (adjacent adapter knowledge):
9. `#TI/co2root-wheel-stack/adapter_project/elmo_transport.py`
- Useful pattern for transport abstraction (serial + EtherCAT), error handling, and runtime mode fallback.
- Not EEA-specific, but design pattern is reusable.

## 5) Suggested Next Technical Checks

1. Confirm current firmware app build/run path and UART print at fixed cadence.
2. Freeze a minimal data contract for replacement adapter output (field names, scale, cadence).
3. Use GUI reverse-engineering lane to map any unknown EEA payload fields while firmware lane progresses.
4. Keep a single source-of-truth milestone log under `notes/host_master/` with exact command + expected first proof line.
