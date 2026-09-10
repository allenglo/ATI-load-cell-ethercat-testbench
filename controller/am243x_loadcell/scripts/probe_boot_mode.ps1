param(
    [string[]]$Ports = @("COM10", "COM9"),
    [int]$Seconds = 6,
    [int]$Baud = 115200
)

$results = @()

foreach ($p in $Ports) {
    $sample = ""
    $status = "no-data"

    try {
        $sp = New-Object System.IO.Ports.SerialPort $p,$Baud,None,8,one
        $sp.ReadTimeout = 300
        $sp.Open()

        $sw = [Diagnostics.Stopwatch]::StartNew()
        while ($sw.Elapsed.TotalSeconds -lt $Seconds) {
            try {
                $sample += [char]$sp.ReadByte()
            } catch {
                # timeout, keep sampling
            }
        }
        $sw.Stop()

        if ($sample.Length -gt 0) {
            if ($sample -match "C{2,}|C") {
                $status = "uart-boot-signature"
            } else {
                $status = "data-present-non-uartboot"
            }
        }

        $sp.Close()
    } catch {
        $status = "port-error"
    }

    $results += [pscustomobject]@{
        Port = $p
        Status = $status
        Bytes = $sample.Length
        Preview = ($sample -replace "`r|`n", " " ).Substring(0, [Math]::Min(40, $sample.Length))
    }
}

$results | Format-Table -AutoSize

if ($results.Status -contains "uart-boot-signature") {
    Write-Host "LIKELY_MODE=UART_BOOT"
    exit 0
}

Write-Host "LIKELY_MODE=NOT_UART_BOOT"
exit 1
