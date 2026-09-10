param()

$devices = Get-PnpDevice -PresentOnly | Where-Object {
    $_.FriendlyName -match 'XDS110|AM243|USB Serial Device|TI' -or $_.InstanceId -match 'VID_0451&PID_BEF3'
}

if (-not $devices) {
    Write-Error 'No LP-AM243 / XDS110 USB devices are visible right now.'
    exit 1
}

$devices |
    Sort-Object Class, FriendlyName |
    Select-Object Status, Class, FriendlyName, InstanceId |
    Format-Table -AutoSize

$ports = $devices | Where-Object { $_.Class -eq 'Ports' }
if ($ports) {
    Write-Host ''
    Write-Host 'Visible COM ports:' -ForegroundColor Cyan
    $ports | Select-Object FriendlyName, InstanceId | Format-Table -AutoSize
}

$bad = $devices | Where-Object { $_.Status -ne 'OK' }
if ($bad) {
    Write-Host ''
    Write-Warning 'Some TI/XDS110 interfaces are in a non-OK state. Install CCS and the AM2x emulation components, then re-run this check.'
}