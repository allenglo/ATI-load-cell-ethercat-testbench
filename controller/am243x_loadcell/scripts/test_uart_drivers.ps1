# Test UART driver functionality (more aggressive than device check)
Write-Host "Testing UART driver functionality..." -ForegroundColor Cyan

$ports = @("COM9", "COM10")

foreach ($port in $ports) {
    Write-Host "`n=== Testing $port ===" -ForegroundColor Magenta
    
    try {
        # Try to open the port with proper settings
        $serialPort = New-Object System.IO.Ports.SerialPort
        $serialPort.PortName = $port
        $serialPort.BaudRate = 115200
        $serialPort.DataBits = 8
        $serialPort.StopBits = 1
        $serialPort.Parity = "None"
        $serialPort.ReadTimeout = 500
        $serialPort.WriteTimeout = 500
        
        Write-Host "Attempting to open $port..."
        $serialPort.Open()
        Write-Host "✓ Port opened successfully" -ForegroundColor Green
        
        # Try to read (should timeout but proves port is responsive)
        Write-Host "Attempting to read from port (waiting 500ms)..."
        try {
            $data = $serialPort.ReadLine()
            if ($data) {
                Write-Host "✓ Received data: $data" -ForegroundColor Green
            }
        } catch {
            Write-Host "✓ Read timeout (expected) - port is responsive" -ForegroundColor Green
        }
        
        # Check if we can write (this is what flash script needs)
        Write-Host "Attempting to write test byte..."
        $serialPort.Write(@(0x43), 0, 1)  # Send 'C' like boot ROM expects
        Write-Host "✓ Write succeeded - port is functional" -ForegroundColor Green
        
        $serialPort.Close()
    } catch {
        Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($serialPort -and $serialPort.IsOpen) { $serialPort.Close() }
    }
}

Write-Host "`n=== Driver Status Check ===" -ForegroundColor Cyan
try {
    $devices = Get-PnpDevice -FriendlyName "*XDS110*" -ErrorAction SilentlyContinue
    if ($devices) {
        foreach ($dev in $devices) {
            Write-Host "$($dev.FriendlyName): $($dev.Status)" -ForegroundColor Green
        }
    } else {
        Write-Host "No XDS110 devices found - checking COM ports..." -ForegroundColor Yellow
        Get-PnpDevice -Class Ports | Where-Object { $_.FriendlyName -match "COM[0-9]+" } | Select-Object FriendlyName, Status
    }
} catch {
    Write-Host "Error checking drivers: $($_.Exception.Message)" -ForegroundColor Red
}
