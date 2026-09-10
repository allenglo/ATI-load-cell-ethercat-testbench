param(
    [string]$OutDir = (Join-Path $PSScriptRoot '..\sdk')
)

$sdkUrl = 'https://dr-download.ti.com/software-development/software-development-kit-sdk/MD-ouHbHEm1PK/12.00.00.26/mcu_plus_sdk_am243x_12_00_00_26-windows-x64-installer.exe'
$installerPath = Join-Path $OutDir 'mcu_plus_sdk_am243x_12_00_00_26-windows-x64-installer.exe'

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

if (Test-Path $installerPath) {
    Write-Host "SDK installer already present: $installerPath"
    exit 0
}

Write-Host "Downloading SDK installer to $installerPath"
Invoke-WebRequest -Uri $sdkUrl -OutFile $installerPath
Write-Host 'Download complete.'
Write-Host 'Next: run the installer and target C:\ti as the install root.'