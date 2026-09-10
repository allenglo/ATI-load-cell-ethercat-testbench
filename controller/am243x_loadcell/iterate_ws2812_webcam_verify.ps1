param(
    [int]$MaxAttempts = 5,
    [int]$CameraIndex = 0,
    [string]$SerialPort = "COM10",
    [double]$DurationSec = 18,
    [double]$SampleIntervalSec = 0.2,
    [string[]]$Roi = @("strip:180,120,360,220"),
    [switch]$ShowPreview
)

$ErrorActionPreference = "Stop"

$TaskDir = "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex"
$Sdk = "C:/ti/mcu_plus_sdk_am243x_12_00_00_26"
$Example = "$Sdk/examples/drivers/mcspi/mcspi_loopback/am243x-lp/r5fss0-0_nortos/ti-arm-clang"
$Gmake = "C:/ti/ccs2050/ccs/utils/bin/gmake.exe"
$CcsPath = "C:/ti/ccs2050/ccs"
$Python = "C:/CoRoot/.venv/Scripts/python.exe"
$Ccxml = "$TaskDir/am2434_xds110_generated.ccxml"
$Out = "$Example/mcspi_loopback.release.out"
$Validator = "$TaskDir/webcam_led_validator.py"
$UartMon = "$TaskDir/scripts/uart_monitor.py"

$syscfgCandidates = @(
    Get-ChildItem -Path "C:/ti" -Directory -Filter "sysconfig_*" -ErrorAction SilentlyContinue
    Get-ChildItem -Path "C:/ti/ccs2050/ccs/utils" -Directory -Filter "sysconfig_*" -ErrorAction SilentlyContinue
)
$SyscfgDir = $syscfgCandidates | Sort-Object FullName -Descending | Select-Object -First 1
if (-not $SyscfgDir) {
    throw "No SysConfig install found under C:/ti"
}

function Invoke-LoadTi {
    param(
        [string]$CcxmlPath,
        [string]$OutPath
    )

    Set-Location "C:/ti/ccs2050/ccs/ccs_base/scripting/examples/loadti"
    $loadOutput = & .\loadti.bat "-c=$CcxmlPath" "-cpu=MAIN_Cortex_R5_0_0" "-l" "-r" "-a" "$OutPath" 2>&1
    $loadOutput | ForEach-Object { Write-Host $_ }

    foreach ($line in $loadOutput) {
        if ($line -match "Error code #4011" -or
            $line -match "Load failed" -or
            $line -match "Trouble Writing Memory Block" -or
            $line -match "Verification failed") {
            return $false
        }
    }

    return ($LASTEXITCODE -eq 0)
}

function Build-McspiOut {
    Set-Location $Example
    & $Gmake -s mcspi_loopback.release.out PYTHON=$Python CCS_PATH=$CcsPath SYSCFG_PATH=$($SyscfgDir.FullName)
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed"
    }
}

Set-Location $TaskDir

for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
    Write-Host "[ITERATE] Attempt $attempt of $MaxAttempts"

    Build-McspiOut

    if (-not (Invoke-LoadTi -CcxmlPath $Ccxml -OutPath $Out)) {
        Write-Warning "[ITERATE] loadti failed on attempt $attempt"
        continue
    }

    # Serial-first debugging: capture a short UART snippet each attempt.
    $serialLog = Join-Path $TaskDir ("reports/serial_debug_attempt_{0:00}.log" -f $attempt)
    Set-Location $TaskDir
    & $Python $UartMon --port $SerialPort --baud 115200 --seconds 6 2>&1 | Tee-Object -FilePath $serialLog
    Write-Host "[ITERATE] Serial debug log: $serialLog"

    $cmd = @(
        $Validator,
        "--camera-index", "$CameraIndex",
        "--serial-port", "$SerialPort",
        "--duration-sec", "$DurationSec",
        "--sample-interval-sec", "$SampleIntervalSec",
        "--save-images",
        "--expected-colors", "RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE", "OFF"
    )

    foreach ($r in $Roi) {
        $cmd += "--roi"
        $cmd += $r
    }

    if ($ShowPreview) {
        $cmd += "--show"
    }

    Set-Location $TaskDir
    & $Python @cmd
    $validatorExit = $LASTEXITCODE

    if ($validatorExit -eq 0) {
        Write-Host "[ITERATE] PASS on attempt $attempt"
        exit 0
    }

    Write-Warning "[ITERATE] Validator did not pass on attempt $attempt"
}

throw "WS2812 webcam verification did not pass after $MaxAttempts attempts"
