param(
    [ValidateSet('status', 'flash-sbl-null',
                 'build-hello', 'load-hello',
                 'build-pin-blink', 'load-pin-blink',
                 'monitor-uart', 'follow-uart',
                 'loop', 'loop-pin-blink')]
    [string]$Action = 'loop',
    [string]$UartPort = 'AUTO',
    [string]$FlashPort = 'AUTO',
    [int]$MonitorSeconds = 20,
    [string]$ExpectText = 'Hello World',
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$sdk = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26'
$python = 'c:\CoRoot\.venv\Scripts\python.exe'
$loadti = 'C:\ti\ccs2050\ccs\ccs_base\scripting\examples\loadti\loadti.bat'
$ccxml = Join-Path $root 'am2434_xds110_generated.ccxml'
$helloOut = Join-Path $sdk 'examples\hello_world\am243x-lp\r5fss0-0_freertos\ti-arm-clang\hello_world.release.out'
$pinBlinkOut = Join-Path $sdk 'examples\drivers\gpio\gpio_led_blink\am243x-lp\r5fss0-0_nortos\ti-arm-clang\gpio_led_blink.release.out'
$flashScript = Join-Path $PSScriptRoot 'flash_and_test.ps1'
$buildScript = Join-Path $PSScriptRoot 'build-hello-world.ps1'
$buildPinBlinkScript = Join-Path $PSScriptRoot 'build-pin-blink.ps1'
$uartScript = Join-Path $PSScriptRoot 'uart_monitor.py'

function Write-Step([string]$msg) {
    Write-Host "`n[STEP] $msg" -ForegroundColor Cyan
}

function Write-Info([string]$msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Gray
}

function Write-Ok([string]$msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-WarnMsg([string]$msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

function Write-Fail([string]$msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
}

function Resolve-XdsPorts {
    $ports = Get-PnpDevice -Class Ports -PresentOnly -ErrorAction SilentlyContinue |
        Where-Object { $_.FriendlyName -match 'XDS110' }

    $result = [ordered]@{
        Application = $null
        Auxiliary   = $null
    }

    foreach ($p in $ports) {
        if ($p.FriendlyName -match 'Application/User UART \(COM(\d+)\)') {
            $result.Application = "COM$($Matches[1])"
        }
        elseif ($p.FriendlyName -match 'Auxiliary Data Port \(COM(\d+)\)') {
            $result.Auxiliary = "COM$($Matches[1])"
        }
    }

    return $result
}

function Resolve-PortChoice([string]$requested, [string]$kind, $ports) {
    if ($requested -and $requested.ToUpper() -ne 'AUTO') {
        return $requested
    }

    if ($kind -eq 'uart') {
        if ($ports.Application) { return $ports.Application }
        if ($ports.Auxiliary) { return $ports.Auxiliary }
    }

    if ($kind -eq 'flash') {
        if ($ports.Auxiliary) { return $ports.Auxiliary }
        if ($ports.Application) { return $ports.Application }
    }

    throw "Unable to auto-detect XDS110 COM ports."
}

function Assert-File([string]$path) {
    if (-not (Test-Path $path)) {
        throw "Missing required file: $path"
    }
}

function Show-ModeReminders {
    Write-Info 'Boot mode reminders (SW4):'
    Write-Info '  UART flash mode: 1110 0000'
    Write-Info '  Normal OSPI mode: 0100 0100'
    Write-Info '  DEV mode (special): 1111 0000'
    Write-Info 'Power-cycle board after any switch change.'
}

function Do-Status {
    Write-Step 'Checking board/port visibility'
    & (Join-Path $PSScriptRoot 'check-ti-launchpad.ps1')
    Show-ModeReminders
}

function Do-BuildHello {
    Write-Step 'Building hello_world example'
    Assert-File $buildScript
    & $buildScript
    if ($LASTEXITCODE -ne 0) {
        throw "hello_world build script failed with exit code $LASTEXITCODE"
    }
    Write-Ok 'Build step completed'
}

function Do-BuildPinBlink {
    Write-Step 'Building gpio_led_blink (Blink-All-Pins) example'
    Assert-File $buildPinBlinkScript
    & $buildPinBlinkScript
    if ($LASTEXITCODE -ne 0) {
        throw "build-pin-blink failed with exit code $LASTEXITCODE"
    }
    Write-Ok 'Pin-blink build completed'
}

function Do-FlashSblNull([string]$port) {
    Write-Step "Flashing SBL NULL on $port"
    Write-WarnMsg 'Board must be in UART boot mode (SW4=1110 0000), UART terminals closed.'
    Assert-File $flashScript
    & $flashScript -Action flash-sbl-null -Port $port
    if ($LASTEXITCODE -ne 0) {
        throw "SBL NULL flash failed with exit code $LASTEXITCODE"
    }
    Write-Ok 'SBL NULL flash command completed. If success was shown, switch back to OSPI mode (0100 0100) and power-cycle.'
}

function Do-LoadHello {
    Write-Step 'Loading hello_world via JTAG'
    Assert-File $loadti
    Assert-File $ccxml
    Assert-File $helloOut

    $tmp = Join-Path $env:TEMP ("am243x_loadti_{0}.log" -f ([guid]::NewGuid().ToString('N')))

    try {
        & $loadti -c="$ccxml" -cpu=MAIN_Cortex_R5_0_0 -r -a -v "$helloOut" 2>&1 | Tee-Object -FilePath $tmp
        $log = if (Test-Path $tmp) { Get-Content $tmp -Raw } else { '' }

        if ($LASTEXITCODE -ne 0 -or $log -match 'load failed|Error code #4011|SEVERE') {
            if ($log -match 'Error -1065') {
                throw 'JTAG load failed with Error -1065 (memory write). Usually caused by wrong boot mode, missing SoC init, or stale power state. Set SW4=0100 0100 for normal mode, power-cycle, reconnect JTAG, retry. If still failing, run one-time SBL NULL flash in UART mode.'
            }
            throw 'JTAG load failed. Check loadti log for target/connect/load errors.'
        }
    }
    finally {
        if (Test-Path $tmp) {
            Remove-Item $tmp -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Ok 'hello_world loaded and run requested'
}

function Do-MonitorUart([string]$port, [int]$seconds, [string]$expect) {
    Write-Step "Monitoring UART on $port for $seconds second(s)"
    Assert-File $python
    Assert-File $uartScript

    if ($expect) {
        & $python $uartScript --port $port --baud 115200 --seconds $seconds --expect $expect
    }
    else {
        & $python $uartScript --port $port --baud 115200 --seconds $seconds
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Ok 'UART monitor completed'
    }
    elseif ($LASTEXITCODE -eq 2) {
        throw "UART opened but expected text was not found: $expect"
    }
    else {
        throw "UART monitor failed with exit code $LASTEXITCODE"
    }
}

function Do-FollowUart([string]$port) {
    Write-Step "Following UART on $port (Ctrl-C to stop, auto-reconnects on board reset)"
    Write-Info "Flash port (COM9 Auxiliary) is not touched."
    Assert-File $python
    Assert-File $uartScript
    & $python $uartScript --port $port --baud 115200 --follow
    # follow exits 0 on Ctrl-C
}

function Do-LoadPinBlink {
    Write-Step 'Loading gpio_led_blink (Blink-All-Pins) via JTAG'
    Assert-File $loadti
    Assert-File $ccxml
    Assert-File $pinBlinkOut

    $tmp = Join-Path $env:TEMP ("am243x_loadti_{0}.log" -f ([guid]::NewGuid().ToString('N')))

    try {
        & $loadti -c="$ccxml" -cpu=MAIN_Cortex_R5_0_0 -r -a -v "$pinBlinkOut" 2>&1 | Tee-Object -FilePath $tmp
        $log = if (Test-Path $tmp) { Get-Content $tmp -Raw } else { '' }

        if ($LASTEXITCODE -ne 0 -or $log -match 'load failed|Error code #4011|SEVERE') {
            if ($log -match 'Error -1065') {
                throw 'JTAG load failed with Error -1065. Set SW4=0100 0100, power-cycle, retry.'
            }
            throw 'JTAG load failed. Check loadti log.'
        }
    }
    finally {
        if (Test-Path $tmp) {
            Remove-Item $tmp -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Ok 'gpio_led_blink (Blink-All-Pins) loaded and running'
}

Assert-File $python
Assert-File $uartScript

$detected = Resolve-XdsPorts
$uart = Resolve-PortChoice -requested $UartPort -kind 'uart' -ports $detected
$flash = Resolve-PortChoice -requested $FlashPort -kind 'flash' -ports $detected

Write-Info "Detected UART port: $uart"
Write-Info "Detected Flash port: $flash"

switch ($Action) {
    'status' {
        Do-Status
    }
    'flash-sbl-null' {
        Do-FlashSblNull -port $flash
    }
    'build-hello' {
        Do-BuildHello
    }
    'load-hello' {
        Do-LoadHello
    }
    'build-pin-blink' {
        Do-BuildPinBlink
    }
    'load-pin-blink' {
        Do-LoadPinBlink
    }
    'monitor-uart' {
        Do-MonitorUart -port $uart -seconds $MonitorSeconds -expect $ExpectText
    }
    'follow-uart' {
        Do-FollowUart -port $uart
    }
    'loop' {
        Do-Status

        if (-not $SkipBuild) {
            Do-BuildHello
        }

        Do-LoadHello
        Do-MonitorUart -port $uart -seconds $MonitorSeconds -expect $ExpectText

        Write-Ok 'Agentic dev loop finished: build/load/verify completed'
    }
    'loop-pin-blink' {
        Do-Status

        if (-not $SkipBuild) {
            Do-BuildPinBlink
        }

        Do-LoadPinBlink
        Write-Ok 'Pin-blink loaded. Run follow-uart to watch output, or monitor-uart for timed check.'
        Write-Info "  Example: .\agentic_dev_loop.ps1 -Action follow-uart"
    }
}
