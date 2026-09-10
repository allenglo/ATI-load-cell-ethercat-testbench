$ErrorActionPreference = 'Stop'

$taskRoot = Split-Path -Parent $PSScriptRoot
$req = Join-Path $taskRoot 'requirements-ethercat-master.txt'

if (!(Test-Path $req)) {
    throw "Missing requirements file: $req"
}

Write-Host '=== EtherCAT Master Stack Setup ==='
Write-Host "Requirements: $req"

python -m pip install --upgrade pip
python -m pip install -r $req

Write-Host ''
Write-Host '=== Installed Versions ==='
python -m pip show pysoem | Select-String -Pattern 'Name:|Version:|Location:'
python -m pip show scapy | Select-String -Pattern 'Name:|Version:|Location:'
python -m pip show numpy | Select-String -Pattern 'Name:|Version:|Location:'
python -m pip show pandas | Select-String -Pattern 'Name:|Version:|Location:'

Write-Host ''
Write-Host '=== Quick Validation ==='
$scan = Join-Path $PSScriptRoot 'ethercat_switch_scan.py'
$tb = Join-Path $PSScriptRoot 'ati_ft_testbench.py'
if (Test-Path $scan) {
    python $scan --adapter-contains "Realtek Gaming USB 2.5GbE" --json
}
if (Test-Path $tb) {
    python $tb --adapter-contains "Realtek Gaming USB 2.5GbE" --cycles 20 --period-ms 10
}

Write-Host ''
Write-Host 'EtherCAT master stack setup complete.'
