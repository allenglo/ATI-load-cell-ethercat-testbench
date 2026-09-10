# Milestone 01 Demo

Run:

```powershell
Set-Location "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex"
python .\scripts\launchpad_host_milestone_demo.py --mode auto --cycles 20 --period-ms 10
```

Verify:
- Output lines start with `LP_HOST_DEMO`.
- Report file is created in `reports/host_master/`.

Note:
- This is validation/demo only. Real target is LaunchPad firmware host mode.

Latest verified runs:
- `reports/host_master/MILESTONE_01_DEMO_20260518_115352.md`
- `reports/host_master/MILESTONE_01_DEMO_20260518_115634.md`

Latest quick check summary:
- Mode: `live`
- Cycles: `20`
- WKC observed: `3` throughout run
