param(
    [int]$SdkMinutes = 18,
    [int]$CcsMinutes = 20
)

Add-Type -AssemblyName System.Windows.Forms
$ws = New-Object -ComObject WScript.Shell

function Drive-Installer {
    param(
        [int]$Pid,
        [int]$Minutes
    )

    $deadline = (Get-Date).AddMinutes($Minutes)
    $lang = @('{ENTER}','%o','%k')
    $flow = @('{ENTER}','%n','%a',' ','%n','%i','%n','%f','%c')

    while ((Get-Date) -lt $deadline) {
        $p = Get-Process -Id $Pid -ErrorAction SilentlyContinue
        if (-not $p) { return $true }

        if ($ws.AppActivate($Pid)) {
            Start-Sleep -Milliseconds 500
            $seq = if ($p.MainWindowTitle -match 'Language Selection') { $lang } else { $flow }
            foreach ($k in $seq) {
                $ws.SendKeys($k)
                Start-Sleep -Milliseconds 900
            }
        } else {
            Start-Sleep -Milliseconds 700
        }
    }

    return $false
}

$sdk = 'C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\sdk\mcu_plus_sdk_am243x_12_00_00_26-windows-x64-installer.exe'
$ccs = 'C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\downloads\ccs\CCS_20.5.0.00028_win\ccs_setup_20.5.0.00028.exe'

Write-Host 'Starting unattended installer attempt in elevated context...' -ForegroundColor Cyan

if (Test-Path $sdk) {
    $sdkProc = Start-Process -FilePath $sdk -PassThru
    Write-Host "SDK PID: $($sdkProc.Id)"
    [void](Drive-Installer -Pid $sdkProc.Id -Minutes $SdkMinutes)
} else {
    Write-Host 'SDK installer not found.' -ForegroundColor Yellow
}

if (Test-Path $ccs) {
    $ccsProc = Start-Process -FilePath $ccs -PassThru
    Write-Host "CCS PID: $($ccsProc.Id)"
    [void](Drive-Installer -Pid $ccsProc.Id -Minutes $CcsMinutes)
} else {
    Write-Host 'CCS installer not found.' -ForegroundColor Yellow
}

Write-Host 'Unattended attempt complete.' -ForegroundColor Green