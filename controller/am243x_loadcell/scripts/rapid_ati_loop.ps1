param(
    [ValidateSet('flash-ati', 'monitor', 'follow', 'loop')]
    [string]$Action = 'loop',
    [string]$Port = 'COM10',
    [int]$Seconds = 15
)

$ErrorActionPreference = 'Stop'

$python = 'c:/CoRoot/.venv/Scripts/python.exe'
$uartScript = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/scripts/uart_monitor.py'
$loadti = 'C:/ti/ccs2050/ccs/ccs_base/scripting/examples/loadti/loadti.bat'
$ccxml = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/am2434_xds110_generated.ccxml'

# Primary ATI binary path (confirmed to contain [ECAT]/[ATI] strings)
$atiOutPrimary = 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26/source/networking/enet/core/examples/enet_layer2_cpsw/am243x-lp/r5fss0-0_freertos/ti-arm-clang/ati_ethercat_master.release.out'
# Optional local build output path
$atiOutLocal = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ati_ethercat_master/Debug/ati_ethercat_master.out'

function Pick-AtiOut {
    if (Test-Path $atiOutLocal) { return $atiOutLocal }
    if (Test-Path $atiOutPrimary) { return $atiOutPrimary }
    throw "ATI .out file not found. Checked:`n  $atiOutLocal`n  $atiOutPrimary"
}

function Flash-Ati {
    $out = Pick-AtiOut
    Write-Host "[rapid-ati] Flashing: $out" -ForegroundColor Cyan
    & $loadti -c="$ccxml" -cpu=MAIN_Cortex_R5_0_0 -r -a -v "$out"
    if ($LASTEXITCODE -ne 0) {
        throw "loadti failed with exit code $LASTEXITCODE"
    }
    Write-Host "[rapid-ati] Flash/load done" -ForegroundColor Green
}

function Monitor-Ati {
    Write-Host "[rapid-ati] Reading $Port for $Seconds seconds..." -ForegroundColor Cyan
    & $python $uartScript --port $Port --baud 115200 --seconds $Seconds
    if ($LASTEXITCODE -ne 0) {
        throw "UART monitor failed with exit code $LASTEXITCODE"
    }
}

function Follow-Ati {
    Write-Host "[rapid-ati] Following $Port (Ctrl-C to stop)..." -ForegroundColor Cyan
    & $python $uartScript --port $Port --baud 115200 --follow
}

switch ($Action) {
    'flash-ati' { Flash-Ati }
    'monitor'   { Monitor-Ati }
    'follow'    { Follow-Ati }
    'loop'      {
        Flash-Ati
        Start-Sleep -Seconds 1
        Monitor-Ati
    }
}
