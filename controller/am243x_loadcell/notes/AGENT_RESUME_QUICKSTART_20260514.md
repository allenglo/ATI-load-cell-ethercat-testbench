# Agent Resume Quickstart (2026-05-14)

Goal for this task lane:
- Test ATI F/T EtherCAT slave readouts quickly.
- Avoid re-discovery work.

## Priority Clarification (Host Firmware Target)

- Final architecture target is LaunchPad as EtherCAT host for ATI data reads.
- Current host pysoem path is a debug/verification tool, not final architecture.
- Before any firmware session, run:

```powershell
powershell -ExecutionPolicy Bypass -File ..\scripts\check_launchpad_host_readiness.ps1
```

- Then follow:
  - `notes\host_master\README.md`
  - `notes\host_master\AGENT_NEXT_STEPS.md`
  - `notes\host_master\PITFALLS.md`

## Current Working State (Verified)

- ATI board PDF used:  
  `C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\downloads\6143.3100.0797 Rev 01 PCBA, ETHERCAT, LOAD CELL.pdf`
- ATI slave is visible and stable on adapter:
  - `Realtek Gaming USB 2.5GbE Family Controller`
  - NPF: `\Device\NPF_{1ED1FFF2-29FD-4011-BE9C-06FBE065A56C}`
- Verified ATI identity:
  - Name: `ATI EtherCAT F/T Sensor`
  - Vendor ID: `1842` (`0x00000732`)
  - Product Code: `642265170` (`0x26483052`)
  - Revision: `65809` (`0x00010111`)
- WKC observed during live cyclic traffic: `3`

## Fastest Path To Reproduce Readouts

From:
`C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts`

1) Bus sanity check:

```powershell
python .\ethercat_switch_scan.py --adapter-contains "Realtek Gaming USB 2.5GbE" --json
```

Expected: one ATI slave, WKC around 3.

2) Live F/T readout testbench:

```powershell
python .\ati_ft_testbench.py --adapter-contains "Realtek Gaming USB 2.5GbE" --cycles 200 --period-ms 10
```

Expected:
- CoE identity prints.
- Cyclic lines with decoded channels: `Fx Fy Fz Tx Ty Tz`.
- Summary with min/max/mean.

3) Incremental one-line mode (recommended; avoids large debug files):

```powershell
python .\ati_ft_testbench.py --adapter-contains "Realtek Gaming USB 2.5GbE" --cycles 15 --period-ms 5 --print-every 1 --line-log ".\logs\ati_ft_live.log" --max-log-lines 10
```

Notes:
- Prints one compact line per cycle.
- Appends to a tiny local log and keeps only the latest N lines.
- No CSV is used.

Optional upload snapshot copy (same run):

```powershell
python .\ati_ft_testbench.py --adapter-contains "Realtek Gaming USB 2.5GbE" --cycles 15 --period-ms 5 --print-every 1 --line-log ".\logs\ati_ft_live.log" --max-log-lines 10 --upload-dir "C:\CoRoot\data\ethercat_upload"
```

## Master Stack Setup (Installed)

From:
`C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\scripts`

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_ethercat_master_stack.ps1
```

What this does:
- Installs/pins host EtherCAT master dependencies from `requirements-ethercat-master.txt`.
- Verifies package versions (`pysoem`, `scapy`, `numpy`, `pandas`).
- Runs quick bus scan and short ATI cyclic readout validation.

## Files Added/Used

- Testbench script:
  - `scripts\ati_ft_testbench.py`
- Existing scanner:
  - `scripts\ethercat_switch_scan.py`
- Master stack setup:
  - `scripts\setup_ethercat_master_stack.ps1`
  - `requirements-ethercat-master.txt`
- Prior diagnostics:
  - `notes\ETHERCAT_SWITCH_PATH_DIAG_20260514.md`
  - `notes\ETHERCAT_HEARTBEAT_AGENT_HANDOFF.md`

## Pitfalls To Avoid

- Do not spend time searching more PDFs; ATI board doc is already local and sufficient.
- Do not require dual-slave enumeration for this lane; single ATI slave readout is the immediate objective.
- Do not assume LaunchPad EtherCAT master firmware is available in local SDK examples; installed TI industrial SDK content is subdevice/slave focused.
- If scan fails suddenly, verify the adapter string first (Realtek Gaming NIC), then link/cabling.

## LaunchPad-Master Clarification

- Current working testbench uses host pysoem as EtherCAT master to validate ATI communication.
- LaunchPad-as-master is not yet implemented in local project artifacts.
- If strict LaunchPad-master is required, this needs a separate master-stack integration task.

## One-Line Hand-off Summary

Use `ethercat_switch_scan.py` and `ati_ft_testbench.py` as regression checks, then continue the LaunchPad host firmware lane via `notes\host_master\AGENT_NEXT_STEPS.md`.
