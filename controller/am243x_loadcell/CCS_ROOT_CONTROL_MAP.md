# CCS Root Control Map

This is the local control surface for CCS on this machine.

## CCS Root Files

- CCS app: `C:/ti/ccs2050/ccs/theia/ccstudio.exe`
- Build tool: `C:/ti/ccs2050/ccs/utils/bin/gmake.exe`
- JTAG load tool: `C:/ti/ccs2050/ccs/ccs_base/scripting/examples/loadti/loadti.bat`
- DSS debug tool: `C:/ti/ccs2050/ccs/ccs_base/scripting/bin/dss.bat`

## Current AM243 Control Workspace

- Task root: `C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex`
- CCS workspace: `C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project`
- Unified controller: `C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_control_center.ps1`

## Main Actions

```powershell
cd 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex'

./ccs_control_center.ps1 -Action status
./ccs_control_center.ps1 -Action open-ccs
./ccs_control_center.ps1 -Action open-ccs-secondary
./ccs_control_center.ps1 -Action prepare-ccs-shadow
./ccs_control_center.ps1 -Action open-ccs-shadow
./ccs_control_center.ps1 -Action build-project
./ccs_control_center.ps1 -Action load-project
./ccs_control_center.ps1 -Action build-load-project
./ccs_control_center.ps1 -Action follow-uart
./ccs_control_center.ps1 -Action dss-pin-blink
./ccs_control_center.ps1 -Action open-gpio-source
./ccs_control_center.ps1 -Action open-mcspi-source
```

## Example Source Files

- SDK hello world: `C:/ti/mcu_plus_sdk_am243x_12_00_00_26/examples/hello_world/hello_world.c`
- SDK GPIO blink: `C:/ti/mcu_plus_sdk_am243x_12_00_00_26/examples/drivers/gpio/gpio_led_blink/gpio_led_blink.c`
- Workspace MCSPI app: `C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/mcspi_loopback.c`

## Notes

- `open-*` actions open Explorer on the target file/folder. This is reliable from the shell even when CCS file-open CLI behavior is limited.
- `open-ccs-secondary` starts CCS on a separate `.theia-workspace` wrapper that points at the same project folder. Use this when CCS says the main workspace is already in use.
- `open-ccs-shadow` creates or refreshes `ccs_singlewire_led_project_shadow` and launches CCS on that copied folder. This is the stronger workaround when CCS still refuses the main workspace.
- `build-load-project` uses the copied CCS workspace project, not in-place SDK edits.
- UART watch uses the existing agentic loop and prefers the XDS110 Application/User UART.