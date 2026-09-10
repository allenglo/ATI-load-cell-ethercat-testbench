param(
	[switch]$SecondaryWorkspace
)

$ccs = 'C:/ti/ccs2050/ccs/theia/ccstudio.exe'
$projectFolder = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project'
$secondaryWorkspace = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project.secondary.theia-workspace'

$target = if ($SecondaryWorkspace) { $secondaryWorkspace } else { $projectFolder }

$proc = Start-Process -FilePath $ccs -ArgumentList "`"$target`"" -PassThru
if ($SecondaryWorkspace) {
	Write-Host 'CCS started on secondary workspace wrapper.'
} else {
	Write-Host 'CCS started on project workspace.'
}
Write-Host "PID: $($proc.Id)"
Write-Host "Target: $target"
Write-Host 'Next: run build_load_run.ps1 from this folder.'
