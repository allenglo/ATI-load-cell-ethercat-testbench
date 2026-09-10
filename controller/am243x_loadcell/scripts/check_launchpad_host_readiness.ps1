param(
    [string]$SdkRoot = "C:\ti\ind_comms_sdk_am243x_11_00_00_08"
)

$ErrorActionPreference = "Stop"

Write-Host "=== LaunchPad EtherCAT Host Readiness ==="
Write-Host "SDK Root: $SdkRoot"
Write-Host ""

$examplesPath = Join-Path $SdkRoot "examples\industrial_comms"
$sourcePath = Join-Path $SdkRoot "source\industrial_comms"
$docsPath = Join-Path $SdkRoot "docs\am243x"

$exampleDirs = if (Test-Path $examplesPath) { Get-ChildItem $examplesPath -Directory | Select-Object -ExpandProperty Name } else { @() }
$sourceDirs = if (Test-Path $sourcePath) { Get-ChildItem $sourcePath -Directory | Select-Object -ExpandProperty Name } else { @() }
$docDirs = if (Test-Path $docsPath) { Get-ChildItem $docsPath -Directory | Select-Object -ExpandProperty Name } else { @() }

$exampleMasterHits = $exampleDirs | Where-Object { ($_ -match "ethercat") -and ($_ -match "master|maindevice|main_device|host") }
$sourceMasterHits = $sourceDirs | Where-Object { ($_ -match "ethercat") -and ($_ -match "master|maindevice|main_device|host") }
$docMasterHits = $docDirs | Where-Object { ($_ -match "ethercat") -and ($_ -match "master|maindevice|main_device|host") }

$docSubdeviceHits = $docDirs | Where-Object { $_ -match "ethercat" }

Write-Host "Examples industrial_comms:"
$exampleDirs | ForEach-Object { Write-Host "  - $_" }
Write-Host ""
Write-Host "Source industrial_comms:"
$sourceDirs | ForEach-Object { Write-Host "  - $_" }
Write-Host ""
Write-Host "Docs am243x (EtherCAT-related):"
$docSubdeviceHits | ForEach-Object { Write-Host "  - $_" }
Write-Host ""

$hasMasterArtifacts = ($exampleMasterHits.Count -gt 0) -or ($sourceMasterHits.Count -gt 0) -or ($docMasterHits.Count -gt 0)

if ($hasMasterArtifacts) {
    Write-Host "RESULT: Potential master-capable artifacts found." -ForegroundColor Yellow
    Write-Host "  Example hits: $($exampleMasterHits -join ', ')"
    Write-Host "  Source hits : $($sourceMasterHits -join ', ')"
    Write-Host "  Docs hits   : $($docMasterHits -join ', ')"
    Write-Host "ACTION: Inspect those directories before assuming missing support."
}
else {
    Write-Host "RESULT: No explicit EtherCAT master/main-device artifact found in this SDK install." -ForegroundColor Cyan
    Write-Host "ACTION:"
    Write-Host "  1) Keep USB-Ethernet + host pysoem path for validation only."
    Write-Host "  2) Start LaunchPad host firmware lane as a dedicated porting effort."
    Write-Host "  3) Use notes/host_master/AGENT_NEXT_STEPS.md to drive implementation order."
}
