# Retry UART flash after manual boot mode switch to 1110 0000
# This script will attempt flash on both COM ports with extended timeouts

Write-Host "=== UART Flash Retry (Boot Mode: 1110 0000) ===" -ForegroundColor Cyan
Write-Host "Ensure SW4 is set to: 1110 0000 (left=1110, right=0000)" -ForegroundColor Yellow
Write-Host "Ensure board has been power cycled" -ForegroundColor Yellow
Read-Host "Press Enter to continue with flash attempt"

$boot = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26\tools\boot'
$py = 'c:/CoRoot/.venv/Scripts/python.exe'
$cfg = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/demo/gpio_led_blink_uart_ospi.cfg'

$ports = @("COM10", "COM9")
$success = $false

foreach ($port in $ports) {
    Write-Host "`n=== Attempting flash on $port ===" -ForegroundColor Magenta
    
    Push-Location $boot
    try {
        Write-Host "Starting UART flash writer on $port..."
        Write-Host "Command: & $py uart_uniflash.py -p $port --cfg='$cfg'"
        
        # Direct invocation with better argument handling
        & $py uart_uniflash.py -p $port --cfg="$cfg" 2>&1 | Tee-Object -Variable flashOutput | Out-Host
        
        $exitCode = $LASTEXITCODE
        if ($exitCode -eq 0 -or $flashOutput -match "Success|completed|Board booting") {
            Write-Host "✓ Flash succeeded on $port!" -ForegroundColor Green
            $success = $true
            break
        } else {
            Write-Host "✗ Flash failed on $port (exit code: $exitCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    } finally {
        Pop-Location
    }
}

if ($success) {
    Write-Host "`n✓✓✓ Flash completed successfully! Board should boot to LED blink on next cycle." -ForegroundColor Green
} else {
    Write-Host "`n✗ Flash failed on all ports. Diagnostics:" -ForegroundColor Red
    Write-Host "1. Verify SW4 physical switch position matches 1110 0000" -ForegroundColor Yellow
    Write-Host "2. Verify board was power cycled AFTER setting switch" -ForegroundColor Yellow
    Write-Host "3. Check if board is in correct boot mode (run probe_boot_mode.ps1)" -ForegroundColor Yellow
    Write-Host "4. If still failing, consider JTAG/CCS load instead" -ForegroundColor Yellow
}
