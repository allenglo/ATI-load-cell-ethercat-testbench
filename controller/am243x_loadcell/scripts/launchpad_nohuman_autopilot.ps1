param(
    [int]$MaxAttempts = 6,
    [int]$DelaySeconds = 2,
    [string]$Ccxml = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/am2434_xds110_generated.ccxml',
    [string]$Cpu = 'MAIN_Cortex_R5_0_0',
    [string]$OutFile = 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26/examples/drivers/gpio/gpio_led_blink/am243x-lp/r5fss0-0_nortos/ti-arm-clang/gpio_led_blink.release.out',
    [int]$RunDelayMs = 2000
)

$ErrorActionPreference = 'Stop'

$xdsdfu = 'C:/ti/ccs2050/ccs/ccs_base/common/uscif/xds110/xdsdfu.exe'
$xdsreset = 'C:/ti/ccs2050/ccs/ccs_base/common/uscif/xds110/xds110reset.exe'
$dss = 'C:/ti/ccs2050/ccs/ccs_base/scripting/bin/dss.bat'
$dssScript = Join-Path $PSScriptRoot 'dss_load_run_generic.js'

function Assert-Path([string]$path) {
    if (-not (Test-Path $path)) {
        throw "Missing required file: $path"
    }
}

function Test-XdsVisible {
    $probeLog = & $xdsdfu -e 2>&1
    $probeText = ($probeLog | Out-String)
    $probeLog | ForEach-Object { Write-Host $_ }
    return ($probeText -match 'Found 1 device|Found [2-9]')
}

function Invoke-AutopilotAttempt([int]$attempt) {
    Write-Host "`n=== AUTOPILOT ATTEMPT $attempt/$MaxAttempts ===" -ForegroundColor Cyan

    if (-not (Test-XdsVisible)) {
        Write-Host '[AUTO] XDS110 not visible. Toggling probe...' -ForegroundColor Yellow
        & $xdsreset -a toggle -d 120 | Out-Null
        Start-Sleep -Seconds $DelaySeconds
        return $false
    }

    Write-Host '[AUTO] Toggling probe reset for clean connect...' -ForegroundColor Gray
    & $xdsreset -a toggle -d 120 | Out-Null

    $args = @(
        $dssScript,
        $Ccxml,
        $Cpu,
        $OutFile,
        "$RunDelayMs"
    )

    $dssLog = & $dss @args 2>&1
    $dssText = ($dssLog | Out-String)
    $dssLog | ForEach-Object { Write-Host $_ }

    $hasFailure = ($dssText -match 'SEVERE:') -or
        ($dssText -match '\[DSS\] FAILURE') -or
        ($dssText -match 'Error code #') -or
        ($dssText -match 'load failed')

    $hasSuccess = $dssText -match '\[DSS\] SUCCESS'

    if (-not $hasFailure -and $hasSuccess -and $LASTEXITCODE -eq 0) {
        Write-Host '[AUTO] Target program loaded and running.' -ForegroundColor Green
        return $true
    }

    Write-Host '[AUTO] Attempt failed; retrying...' -ForegroundColor Yellow
    return $false
}

Assert-Path $xdsdfu
Assert-Path $xdsreset
Assert-Path $dss
Assert-Path $dssScript
Assert-Path $Ccxml
Assert-Path $OutFile

$success = $false
for ($i = 1; $i -le $MaxAttempts; $i++) {
    if (Invoke-AutopilotAttempt -attempt $i) {
        $success = $true
        break
    }
    Start-Sleep -Seconds $DelaySeconds
}

if ($success) {
    Write-Host 'AUTOPILOT_RESULT=SUCCESS' -ForegroundColor Green
    exit 0
}

Write-Host 'AUTOPILOT_RESULT=FAILED' -ForegroundColor Red
exit 1
