param(
    [switch]$BuildAndLoad,
    [switch]$ShowPreview,
    [switch]$Simulate,
    [int]$CameraIndex = 0,
    [string]$SerialPort = "COM10",
    [double]$DurationSec = 20,
    [string[]]$Roi = @()
)

$ErrorActionPreference = "Stop"

$TaskDir = "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex"
$Python = "C:/CoRoot/.venv/Scripts/python.exe"

Set-Location $TaskDir

if ($BuildAndLoad) {
    Write-Host "[STEP] Build and load firmware..."
    & "$TaskDir/run_ws2812_build.ps1"
}

$cmd = @(
    "$TaskDir/webcam_led_validator.py",
    "--camera-index", "$CameraIndex",
    "--serial-port", "$SerialPort",
    "--duration-sec", "$DurationSec"
)

if ($ShowPreview) {
    $cmd += "--show"
}

if ($Simulate) {
    $cmd += "--simulate"
}

foreach ($r in $Roi) {
    $cmd += "--roi"
    $cmd += $r
}

Write-Host "[STEP] Running validator..."
& $Python @cmd
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "[DONE] Validation PASS"
} else {
    Write-Host "[DONE] Validation FAIL (exit $exitCode)"
}

exit $exitCode
