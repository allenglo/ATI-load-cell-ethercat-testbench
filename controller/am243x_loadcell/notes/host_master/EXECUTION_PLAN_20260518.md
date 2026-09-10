# Execution Plan (2026-05-18)

Purpose:
- Continue development professionally with clear, testable steps.
- Keep host verification stable while unblocking LaunchPad firmware host lane.

Scope:
- In scope: development sequencing, validation commands, documentation hygiene.
- Out of scope: large framework rewrites or long new scripts.

## Current Facts

1. Proven path today:
- Host pysoem communication to ATI sensor is stable.
- Recent run produced 20/20 decoded lines with `wkc=3`.

2. Active blocker:
- LaunchPad firmware host lane remains blocked by CPSW/RM initialization path.
- Installed industrial SDK content currently exposes subdevice/slave examples, not a ready main-device host example.

3. Risk control:
- Keep host pysoem lane as regression/proof only.
- Do not treat host pysoem result as final firmware completion.

## Execution Sequence

### Phase A - Daily Sanity Gate (2-3 minutes)

Run:

```powershell
Set-Location "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex"
powershell -ExecutionPolicy Bypass -File .\scripts\check_launchpad_host_readiness.ps1
```

Pass criteria:
- Command runs cleanly.
- Output clearly states whether host artifacts are present or absent.

### Phase B - Regression Proof Snapshot (1-2 minutes)

Run:

```powershell
Set-Location "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex"
& "C:\CoRoot\.venv\Scripts\python.exe" .\scripts\launchpad_host_milestone_demo.py --mode auto --cycles 20 --period-ms 10
```

Pass criteria:
- Output lines start with `LP_HOST_DEMO`.
- `wkc` remains stable (expected `3` on known-good adapter path).
- A new report is generated under `reports/host_master/`.

### Phase C - Firmware Unblock Work (Focused)

Target:
- Rebuild and validate the SOC init path with correct board config assumptions before re-running ENET baseline and custom app tests.

Steps:
1. Keep baseline-first strategy:
- Validate stock ENET app startup behavior before ATI app.

2. Confirm loader contract:
- Keep 2-step DEV boot flow and verify step-1 completion timing behavior.

3. Capture minimal proof:
- One short UART snippet for baseline result.
- One short UART snippet for ATI app result.

Pass criteria:
- Baseline ENET app no longer fails at the known CPSW assert point.
- Then ATI firmware lane is eligible for cyclic F/T print verification.

### Phase D - Documentation Hygiene (same day)

Update only these:
- `notes/host_master/AGENT_NEXT_STEPS.md`
- `notes/host_master/MILESTONE_01_DEMO.md`
- Add one latest report path and one exact next command.

Rules:
- Keep updates short and operational.
- Do not duplicate old narrative.

## Definition Of Done (This Stage)

Stage done when all are true:
1. Sanity gate executed and recorded for current day.
2. Milestone demo report generated for current day.
3. Firmware lane has one explicit unblock experiment result documented.
4. Handoff contains one next command and expected first proof line.

## Immediate Next Command

```powershell
Set-Location "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex"
& "C:\CoRoot\.venv\Scripts\python.exe" .\scripts\launchpad_host_milestone_demo.py --mode auto --cycles 20 --period-ms 10
```
