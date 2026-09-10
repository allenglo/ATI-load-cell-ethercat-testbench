$env:TOOLS_PATH = 'C:/ti'
$env:CCS_PATH = 'C:/ti/ccs2050/ccs'
$env:SYSCFG_PATH = 'C:/ti/ccs2050/ccs/utils/sysconfig_1.27.0'
$env:SDK_PATH = 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26'
$env:MCU_PLUS_SDK_PATH = $env:SDK_PATH

Write-Host "TOOLS_PATH=$env:TOOLS_PATH"
Write-Host "CCS_PATH=$env:CCS_PATH"
Write-Host "SYSCFG_PATH=$env:SYSCFG_PATH"
Write-Host "SDK_PATH=$env:SDK_PATH"
Write-Host "MCU_PLUS_SDK_PATH=$env:MCU_PLUS_SDK_PATH"
