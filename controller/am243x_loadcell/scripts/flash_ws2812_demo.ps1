param(
    [string]$Port = "COM10",
    [int]$TimeoutSec = 180
)

$boot = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26\tools\boot'
$py = 'c:/CoRoot/.venv/Scripts/python.exe'
$cfg = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/demo/ws2812_16_spi_uart_ospi.cfg'

Write-Host "Set SW4 to UART boot: 1110 0000, then power cycle." -ForegroundColor Yellow
Read-Host "Press Enter to start flashing"

Push-Location $boot
try {
    $job = Start-Job -ScriptBlock {
        param($pythonExe, $configPath, $comPort)
        & $pythonExe uart_uniflash.py -p $comPort --cfg="$configPath" 2>&1 | Out-String -Width 260
    } -ArgumentList $py, $cfg, $Port

    if (-not (Wait-Job $job -Timeout $TimeoutSec)) {
        Write-Host "Flash timed out after $TimeoutSec seconds. Stopping job..." -ForegroundColor Red
        Stop-Job $job | Out-Null
        Receive-Job $job -Keep | Write-Host
        throw "UART flash timeout"
    }

    $output = Receive-Job $job
    $output | Write-Host

    if ($output -match "100%|All tests have passed|flash-mcelf-xip") {
        Write-Host "WS2812 demo flash completed." -ForegroundColor Green
    } else {
        Write-Host "Flash finished but success pattern not found. Please review output." -ForegroundColor Yellow
    }
}
finally {
    Pop-Location
}
