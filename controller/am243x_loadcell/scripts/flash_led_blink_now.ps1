param(
    [string]$Port = "COM10",
    [int]$TimeoutSec = 120
)

$ErrorActionPreference = "Stop"

$bootDir = "C:\ti\mcu_plus_sdk_am243x_12_00_00_26\tools\boot"
$pythonExe = "c:\CoRoot\.venv\Scripts\python.exe"
$cfgPath = "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\demo\gpio_led_blink_uart_ospi.cfg"
$cfgTmpPath = Join-Path $env:TEMP "am243x_gpio_led_blink_uart_ospi.cfg"
$logPath = Join-Path $env:TEMP "am243x_led_blink_flash.log"
$outLogPath = Join-Path $env:TEMP "am243x_led_blink_flash.out.log"
$errLogPath = Join-Path $env:TEMP "am243x_led_blink_flash.err.log"

if (-not (Test-Path $pythonExe)) {
    throw "Python venv executable not found: $pythonExe"
}
if (-not (Test-Path $bootDir)) {
    throw "Boot tools folder not found: $bootDir"
}

# Ensure no stale uniflash jobs keep COM port busy.
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match "uart_uniflash.py" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Push-Location $bootDir
try {
    if (Test-Path $logPath) { Remove-Item $logPath -Force }
    if (Test-Path $outLogPath) { Remove-Item $outLogPath -Force }
    if (Test-Path $errLogPath) { Remove-Item $errLogPath -Force }
    Copy-Item $cfgPath $cfgTmpPath -Force

    $args = @("uart_uniflash.py", "-p", $Port, "--cfg", $cfgTmpPath)
    $proc = Start-Process -FilePath $pythonExe -ArgumentList $args -PassThru -NoNewWindow -RedirectStandardOutput $outLogPath -RedirectStandardError $errLogPath

    $finished = $proc.WaitForExit($TimeoutSec * 1000)
    $combined = @()
    if (Test-Path $outLogPath) { $combined += Get-Content $outLogPath }
    if (Test-Path $errLogPath) { $combined += Get-Content $errLogPath }
    if ($combined.Count -gt 0) { $combined | Set-Content $logPath }

    if (-not $finished) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Write-Host "[TIMEOUT] Flashing did not complete in $TimeoutSec seconds."
        Write-Host "Likely cause: board is not in UART boot mode (SW4 should be 1110 0000), or wrong COM port."
        if (Test-Path $logPath) {
            Write-Host "Log: $logPath"
            Get-Content $logPath -Tail 30
        } else {
            Write-Host "No UART output log was captured."
        }
        exit 2
    }

    if (Test-Path $logPath) {
        $output = Get-Content $logPath -Raw
    } else {
        $output = ""
    }
    if ($output -match "\[STATUS\]\s+SUCCESS") {
        Write-Host "[SUCCESS] LED blink image flashed."
        Write-Host "Next: power off, set SW4 to OSPI mode (0100 0100), power on and check LED blink."
        Get-Content $logPath -Tail 30
        exit 0
    }

    Write-Host "[FAIL] Flash command completed but success marker not found."
    Write-Host "Log: $logPath"
    Get-Content $logPath -Tail 50
    exit 1
}
finally {
    if (Test-Path $cfgTmpPath) { Remove-Item $cfgTmpPath -Force -ErrorAction SilentlyContinue }
    Pop-Location
}
