param(
    [int]$Baud = 115200,
    [switch]$NoKill,
    [switch]$NoCleanText,
    [double]$RetryInterval = 1.0,
    [double]$Seconds = 0
)

$ErrorActionPreference = 'Stop'

function Get-XdsPorts {
    $ports = Get-CimInstance Win32_PnPEntity |
        Where-Object { $_.Name -match 'XDS110.*\(COM\d+\)' } |
        Select-Object -ExpandProperty Name

    $app = $null
    $aux = $null

    foreach ($name in $ports) {
        if ($name -match '\(COM\d+\)') {
            $com = $Matches[0].Trim('()')
            if ($name -match 'Application/User UART') { $app = $com }
            if ($name -match 'Auxiliary Data Port') { $aux = $com }
        }
    }

    [PSCustomObject]@{
        Application = $app
        Auxiliary   = $aux
        RawNames    = $ports
    }
}

function Stop-LikelySerialLockers {
    $patterns = @(
        'uart_monitor\.py',
        'serial_monitor_gui\.py',
        'putty',
        'ttermpro',
        'teraterm'
    )

    $joined = ($patterns -join '|')
    $procs = Get-CimInstance Win32_Process |
        Where-Object {
            ($_.Name -match 'python\.exe|putty\.exe|ttermpro\.exe') -and
            ($_.CommandLine -match $joined -or $_.Name -match 'putty\.exe|ttermpro\.exe')
        }

    if (-not $procs) {
        Write-Host '[stable-uart] No likely serial lock holders found.' -ForegroundColor DarkGray
        return
    }

    foreach ($p in $procs) {
        try {
            Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop
            Write-Host "[stable-uart] Stopped lock holder PID $($p.ProcessId): $($p.Name)" -ForegroundColor Yellow
        } catch {
            Write-Host "[stable-uart] Could not stop PID $($p.ProcessId): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

$ports = Get-XdsPorts
if (-not $ports.Application) {
    Write-Host '[stable-uart] ERROR: XDS110 Application/User UART not found. Check cable/power.' -ForegroundColor Red
    if ($ports.RawNames) {
        Write-Host '[stable-uart] Detected XDS ports:' -ForegroundColor DarkYellow
        $ports.RawNames | ForEach-Object { Write-Host "  $_" }
    }
    exit 1
}

Write-Host "[stable-uart] App UART : $($ports.Application)" -ForegroundColor Green
if ($ports.Auxiliary) {
    Write-Host "[stable-uart] Aux Port : $($ports.Auxiliary) (for flashing, not console text)" -ForegroundColor DarkYellow
}

if (-not $NoKill) {
    Stop-LikelySerialLockers
} else {
    Write-Host '[stable-uart] Skipping lock-holder cleanup (--NoKill).' -ForegroundColor DarkGray
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$monitorPy = Join-Path $scriptDir 'uart_monitor.py'
$pythonExe = 'C:\CoRoot\.venv\Scripts\python.exe'

if (-not (Test-Path $monitorPy)) {
    Write-Host "[stable-uart] ERROR: Missing $monitorPy" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $pythonExe)) {
    Write-Host "[stable-uart] ERROR: Missing $pythonExe" -ForegroundColor Red
    exit 1
}

Write-Host "[stable-uart] Starting stable monitor on $($ports.Application) @ $Baud ..." -ForegroundColor Cyan
if ($Seconds -gt 0) {
    Write-Host "[stable-uart] Timed mode: reading for $Seconds seconds" -ForegroundColor DarkCyan
    if ($NoCleanText) {
        & $pythonExe $monitorPy --port $ports.Application --baud $Baud --seconds $Seconds --no-clean-text
    } else {
        & $pythonExe $monitorPy --port $ports.Application --baud $Baud --seconds $Seconds
    }
} else {
    if ($NoCleanText) {
        & $pythonExe $monitorPy --port $ports.Application --baud $Baud --follow --retry-interval $RetryInterval --no-clean-text
    } else {
        & $pythonExe $monitorPy --port $ports.Application --baud $Baud --follow --retry-interval $RetryInterval
    }
}
exit $LASTEXITCODE
