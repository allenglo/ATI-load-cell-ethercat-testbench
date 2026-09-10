param(
    [ValidateSet('auto', 'jtag', 'uart')]
    [string]$Mode = 'auto',
    [string]$ComPorts = 'COM9,COM10',
    [string]$JtagCcxml = 'C:/CoRoot/TASKS/am2434_xds110_generated.ccxml',
    [string]$OutFile = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/am243x-lp/r5fss0-0_nortos/ti-arm-clang/dual_spi_leds.release.out',
    [string]$UartSbl = 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26/examples/drivers/boot/sbl_uart/am243x-lp/r5fss0-0_nortos/ti-arm-clang/sbl_uart.release.hs_fs.tiimage',
    [string]$UartApp = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/am243x-lp/r5fss0-0_nortos/ti-arm-clang/mcspi_loopback.release.mcelf.hs_fs'
)

$ErrorActionPreference = 'Stop'

$loadti = 'C:/ti/ccs2050/ccs/ccs_base/scripting/examples/loadti/loadti.bat'
$xdsdfu = 'C:/ti/ccs2050/ccs/ccs_base/common/uscif/xds110/xdsdfu.exe'
$uartBoot = 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26/tools/boot/uart_bootloader.py'
$pythonExe = 'C:/CoRoot/.venv/Scripts/python.exe'

function Invoke-JtagLoad {
    Write-Host '=== JTAG path ===' -ForegroundColor Cyan

    if (-not (Test-Path $xdsdfu)) { throw "Missing: $xdsdfu" }
    if (-not (Test-Path $loadti)) { throw "Missing: $loadti" }
    if (-not (Test-Path $JtagCcxml)) { throw "Missing: $JtagCcxml" }
    if (-not (Test-Path $OutFile)) { throw "Missing: $OutFile" }

    $probeLog = & $xdsdfu -e 2>&1
    $probeLog | ForEach-Object { Write-Host $_ }

    $probeText = ($probeLog | Out-String)
    if ($probeText -notmatch 'Found 1 device|Found [2-9]') {
        Write-Host 'JTAG skip: XDS110 not visible.' -ForegroundColor Yellow
        return $false
    }

    $loadLog = & $loadti -c="$JtagCcxml" -r "$OutFile" 2>&1
    $loadLog | ForEach-Object { Write-Host $_ }

    $loadText = ($loadLog | Out-String)
    $loadHasErrors = ($loadText -match 'SEVERE:') -or
        ($loadText -match 'load failed') -or
        ($loadText -match 'Error code #')

    if ($LASTEXITCODE -ne 0 -or $loadHasErrors) {
        Write-Host 'JTAG load failed.' -ForegroundColor Yellow
        return $false
    }

    Write-Host 'JTAG load OK.' -ForegroundColor Green
    return $true
}

function Invoke-UartLoad {
    Write-Host '=== UART path ===' -ForegroundColor Cyan

    if (-not (Test-Path $pythonExe)) { throw "Missing: $pythonExe" }
    if (-not (Test-Path $uartBoot)) { throw "Missing: $uartBoot" }
    if (-not (Test-Path $UartSbl)) { throw "Missing: $UartSbl" }
    if (-not (Test-Path $UartApp)) { throw "Missing: $UartApp" }

    Write-Host 'Before UART boot:' -ForegroundColor Yellow
    Write-Host '1) Board in UART boot mode (1110 0000)' -ForegroundColor Yellow
    Write-Host '2) Power cycle board (not only reset)' -ForegroundColor Yellow
    Write-Host '3) UART terminal must be closed' -ForegroundColor Yellow

    $ports = $ComPorts.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    foreach ($port in $ports) {
        Write-Host "Trying UART on $port ..." -ForegroundColor Cyan

        Push-Location 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26/tools/boot'
        $uartLog = & $pythonExe $uartBoot -p $port --soc am64x_am243x -b $UartSbl -f $UartApp 2>&1
        $uartCode = $LASTEXITCODE
        Pop-Location

        $uartLog | ForEach-Object { Write-Host $_ }
        $uartText = ($uartLog | Out-String)

        $uartHasErrors = ($uartText -match '\[ERROR\]') -or
            ($uartText -match 'XMODEM send failed') -or
            ($uartText -match 'no response OR incorrect response')

        if ($uartCode -eq 0 -and -not $uartHasErrors) {
            Write-Host "UART load OK on $port." -ForegroundColor Green
            return $true
        }

        Write-Host "UART load failed on $port." -ForegroundColor Yellow
    }

    return $false
}

$success = $false

switch ($Mode) {
    'jtag' {
        $success = Invoke-JtagLoad
    }
    'uart' {
        $success = Invoke-UartLoad
    }
    default {
        $success = Invoke-JtagLoad
        if (-not $success) {
            Write-Host 'Falling back to UART...' -ForegroundColor Yellow
            $success = Invoke-UartLoad
        }
    }
}

if ($success) {
    Write-Host 'TURNKEY_UPLOAD_RUN: SUCCESS' -ForegroundColor Green
    exit 0
}

Write-Host 'TURNKEY_UPLOAD_RUN: FAILED' -ForegroundColor Red
exit 1
