param(
    [string]$SdkPath = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26'
)

if (-not (Test-Path $SdkPath)) {
    Write-Error "SDK path not found: $SdkPath"
    exit 1
}

[Environment]::SetEnvironmentVariable('MCU_PLUS_SDK_AM243X_PATH', $SdkPath, 'User')
[Environment]::SetEnvironmentVariable('TI_AM243X_SDK_PATH', $SdkPath, 'User')

Write-Host 'Updated user environment variables:' -ForegroundColor Cyan
Write-Host "MCU_PLUS_SDK_AM243X_PATH=$SdkPath"
Write-Host "TI_AM243X_SDK_PATH=$SdkPath"
Write-Host 'Open a new terminal or restart CCS before relying on the updated values.'