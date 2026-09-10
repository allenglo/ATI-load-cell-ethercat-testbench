#Requires -Version 5.0
<#
Ethernet Discovery & Connectivity Test
Scans for connected devices on Ethernet adapters
#>

param(
    [string]$Subnet = "192.168.1",
    [switch]$FullScan,
    [string]$Filter = "*Ethernet*"
)

function Test-ConnectedDevices {
    Write-Host "=== Network Adapter Status ===" -ForegroundColor Cyan
    
    # Get all Ethernet adapters
    $adapters = Get-NetAdapter | Where-Object { $_.Name -like $Filter -and $_.Status -eq 'Up' }
    
    if ($adapters.Count -eq 0) {
        Write-Host "No active Ethernet adapters found!" -ForegroundColor Red
        return
    }
    
    foreach ($adapter in $adapters) {
        Write-Host "`nAdapter: $($adapter.Name)" -ForegroundColor Green
        Write-Host "  Status: $($adapter.Status)"
        Write-Host "  MAC: $($adapter.MacAddress)"
        
        # Get IP configuration
        $ipConfig = Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -ErrorAction SilentlyContinue
        if ($ipConfig) {
            foreach ($ip in $ipConfig) {
                Write-Host "  IP: $($ip.IPAddress) (PrefixLength: $($ip.PrefixLength))"
            }
        } else {
            Write-Host "  IP: NONE (may auto-configure via APIPA)"
        }
    }
    
    Write-Host "`n=== ARP Cache (Current Known Devices) ===" -ForegroundColor Cyan
    $arpTable = arp -a | Select-Object -Skip 3
    if ($arpTable) {
        $arpTable | ForEach-Object {
            if ($_ -match "^\s+([0-9.]+)\s+([0-9a-f-]+)") {
                Write-Host "  $([regex]::Matches($_, '([0-9.]+|[0-9a-f-]+)') | ForEach-Object { $_.Value })" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "  ARP cache empty (no prior connections)" -ForegroundColor Yellow
    }
    
    Write-Host "`n=== Attempting ICMP Echo (Ping) ===" -ForegroundColor Cyan
    
    # Common defaults for industrial equipment
    $targets = @(
        "169.254.1.1",      # APIPA link-local
        "192.168.1.100",    # Common default
        "10.0.0.1",         # Common default
        "10.0.0.100",       # Load cell common range
        "192.168.0.1"       # Router
    )
    
    foreach ($target in $targets) {
        $result = Test-Connection -ComputerName $target -Count 1 -ErrorAction SilentlyContinue
        if ($result) {
            Write-Host "  ✓ $target REACHABLE" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $target unreachable" -ForegroundColor Gray
        }
    }
    
    if ($FullScan) {
        Write-Host "`n=== Full Subnet Scan (this may take 30 sec) ===" -ForegroundColor Cyan
        $baseIP = $Subnet
        1..254 | ForEach-Object {
            $ip = "$baseIP.$_"
            $result = Test-Connection -ComputerName $ip -Count 1 -ErrorAction SilentlyContinue
            if ($result) {
                Write-Host "  ✓ $ip FOUND" -ForegroundColor Green
            }
        }
    }
}

Test-ConnectedDevices

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. If you see 'REACHABLE' IPs above, try: ping <IP>"
Write-Host "2. For full subnet scan: .\discover_ethernet.ps1 -FullScan"
Write-Host "3. If no devices found, check FAULT LED diagnosis first."
