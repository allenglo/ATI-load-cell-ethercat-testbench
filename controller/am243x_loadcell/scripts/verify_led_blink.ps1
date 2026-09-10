# Verify LED blink after OSPI boot
Write-Host "=== LED Blink Verification ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Set SW4 to: 0100 0100 (left=0100, right=0100)" -ForegroundColor White
Write-Host "   - This selects OSPI boot mode (where we just flashed the code)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Power cycle the board" -ForegroundColor White
Write-Host "   - Unplug USB-C power for 2 seconds, then plug back in" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Look for LED blinks on the board" -ForegroundColor White
Write-Host "   - Should see steady blinking pattern on one of the LEDS" -ForegroundColor Gray
Write-Host ""
Write-Host "Once you see the LEDs blinking, the bring-up is complete!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter after you've set the switch and power cycled"

Write-Host "`nChecking board connectivity..." -ForegroundColor Cyan
try {
    $devices = Get-PnpDevice -FriendlyName "*XDS110*" -ErrorAction SilentlyContinue
    if ($devices) {
        Write-Host "✓ XDS110 debug probe is connected" -ForegroundColor Green
        foreach ($dev in $devices) {
            Write-Host "  - $($dev.FriendlyName): $($dev.Status)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "✗ Could not check devices" -ForegroundColor Red
}

Write-Host "`nIf LEDs are NOT blinking:" -ForegroundColor Yellow
Write-Host "1. Verify SW4 physical position is correct" -ForegroundColor Gray
Write-Host "2. Check that board powered up (USB-C LED indicator should be on)" -ForegroundColor Gray
Write-Host "3. Try power cycling again" -ForegroundColor Gray
