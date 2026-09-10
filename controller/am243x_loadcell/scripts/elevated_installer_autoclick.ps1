param(
    [int]$Minutes = 30
)

# This script must run in an elevated PowerShell session.
# It repeatedly focuses likely TI installer windows and sends keyboard shortcuts
# commonly used by installer UIs: Next, Install, and Finish.

Add-Type -AssemblyName System.Windows.Forms
$ws = New-Object -ComObject WScript.Shell

$targets = @(
    'Language Selection',
    'mcu_plus_sdk_am243x',
    'Code Composer Studio Setup',
    'Code Composer Studio',
    'Texas Instruments',
    'Setup'
)

$languageSequence = @(
    '{ENTER}',
    '%o',
    '%k'
)

$installSequence = @(
    '{ENTER}',
    '%n',  # Alt+N (Next)
    '%a',  # Alt+A (Accept)
    ' ',   # Space (toggle checkbox)
    '%n',
    '%i',  # Alt+I (Install)
    '%n',
    '%f',  # Alt+F (Finish)
    '%c'   # Alt+C (Close)
)

$deadline = (Get-Date).AddMinutes($Minutes)
Write-Host "Autoclicker started for $Minutes minute(s)." -ForegroundColor Cyan

while ((Get-Date) -lt $deadline) {
    $focused = $false
    foreach ($title in $targets) {
        if ($ws.AppActivate($title)) {
            $focused = $true
            Start-Sleep -Milliseconds 400
            $sequence = if ($title -eq 'Language Selection') { $languageSequence } else { $installSequence }
            foreach ($k in $sequence) {
                $ws.SendKeys($k)
                Start-Sleep -Milliseconds 800
            }
            break
        }
    }

    if (-not $focused) {
        Start-Sleep -Milliseconds 700
    }
}

Write-Host 'Autoclicker finished.' -ForegroundColor Green