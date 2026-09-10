# LaunchPad Host and Peripheral Evidence

## ATI Load-Cell Host Lane

Goal: observe the ATI F/T EtherCAT lane without changing device state.

Use now (validated host-side entrypoint):
- `python scripts/launchpad_host_milestone_demo.py --mode auto --cycles 20 --period-ms 10`

Primary tools:
- `scripts/ati_ft_testbench.py`: read-oriented CLI capture.
- `scripts/launchpad_loadcell_live_gui.py`: GUI with read views plus write-capable controls. Do not use PDO/SDO write controls for characterization.

Current evidence:
- Host tooling identifies ATI vendor ID `1842` and product code `642265170`.
- Current decoder treats first 24 input bytes as six little-endian signed `int32` values: Fx, Fy, Fz, Tx, Ty, Tz.
- Host-side scale, calibration, tare, object dictionary, and deterministic device ordering remain unverified.

Execution plan:
- `EXECUTION_PLAN_20260518.md`

Operational guardrails:
- `PITFALLS.md`

## EEA / ROI Reference Lane

The EEA and ROI path is not the ATI load-cell path. EEA/ROI uses EtherCAT-to-Modbus gateway mapping plus RS-485 Modbus RTU endpoints.

Start with:
- `MASTERNOTES_EEA_GUI_WORKFLOW.md`: live direct-serial results and command constraints.
- `EEA_COMPLETE_REGISTER_AND_FRAME_CATALOG.md`: recovered gateway PDO, station, and register evidence.
- `../../demo/eea_gateway_bridge/README.md`: hardware-agnostic conversion reference.

Current direct-serial evidence: COM18, 115200/E/1, slaves 1-3 respond. Treat slave 4/ROI availability as unverified on this lane.

## Evidence Rule

Keep dated capture output here. Do not overwrite it. Label all future claims as `live-observed`, `source-derived`, or `unknown`.
