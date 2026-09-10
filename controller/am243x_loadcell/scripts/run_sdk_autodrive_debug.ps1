param(
    [int]$Minutes = 25,
    [string]$InstallerPath = 'c:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\sdk\mcu_plus_sdk_am243x_12_00_00_26-windows-x64-installer.exe',
    [string]$LogPath = 'c:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\sdk\sdk_autodrive_debug.log'
)

Add-Type -AssemblyName System.Windows.Forms
$ws = New-Object -ComObject WScript.Shell

function Log([string]$msg) {
    $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    Add-Content -Path $LogPath -Value "[$ts] $msg"
}

"" | Set-Content -Path $LogPath -Encoding ASCII
Log 'Starting SDK autodrive debug run'

if (-not (Test-Path $InstallerPath)) {
    Log "Installer not found: $InstallerPath"
    exit 1
}

Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match 'mcu_plus_sdk' } | Stop-Process -Force -ErrorAction SilentlyContinue
Log 'Stopped pre-existing SDK installer processes'

$proc = Start-Process -FilePath $InstallerPath -PassThru
Log "Started installer PID=$($proc.Id)"

$deadline = (Get-Date).AddMinutes($Minutes)
$languageKeys = @('{ENTER}','%o','%k','%n')
$genericKeys = @('{ENTER}','%n','%a',' ','%n','%i','%n','%f','%c')

while ((Get-Date) -lt $deadline) {
    $p = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if (-not $p) {
        Log 'Installer process exited'
        exit 0
    }

    $title = $p.MainWindowTitle
    if ([string]::IsNullOrWhiteSpace($title)) {
        Log 'MainWindowTitle empty; waiting'
        Start-Sleep -Milliseconds 600
        continue
    }

    Log "WindowTitle='$title'"

    $activated = $ws.AppActivate($proc.Id)
    Log "AppActivate(pid)=$activated"
    if ($activated) {
        Start-Sleep -Milliseconds 400
        $keys = if ($title -match 'Language Selection') { $languageKeys } else { $genericKeys }
        foreach ($k in $keys) {
            $ws.SendKeys($k)
            Log "SendKeys '$k'"
            Start-Sleep -Milliseconds 750
        }
    }

    Start-Sleep -Milliseconds 800
}

Log 'Timed out waiting for installer completion'
exit 2