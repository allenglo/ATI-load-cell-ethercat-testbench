param(
    [ValidateSet(
        'status',
        'open-ccs',
        'open-ccs-secondary',
        'prepare-ccs-shadow',
        'open-ccs-shadow',
        'build-project',
        'load-project',
        'build-load-project',
        'follow-uart',
        'monitor-uart',
        'dss-pin-blink',
        'autopilot-nohuman',
        'show-examples',
        'open-project-folder',
        'open-gpio-source',
        'open-mcspi-source',
        'open-hello-source'
    )]
    [string]$Action = 'status',
    [int]$MonitorSeconds = 20,
    [string]$ExpectText = '',
    [switch]$RunAfterLoad = $true
)

$ErrorActionPreference = 'Stop'

$taskRoot = $PSScriptRoot
$sdkRoot = 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26'
$ccsRoot = 'C:/ti/ccs2050/ccs'
$ccsExe = Join-Path $ccsRoot 'theia/ccstudio.exe'
$gmake = Join-Path $ccsRoot 'utils/bin/gmake.exe'
$loadti = Join-Path $ccsRoot 'ccs_base/scripting/examples/loadti/loadti.bat'
$dss = Join-Path $ccsRoot 'ccs_base/scripting/bin/dss.bat'

$workspaceRoot = Join-Path $taskRoot 'ccs_singlewire_led_project'
$shadowWorkspaceRoot = Join-Path $taskRoot 'ccs_singlewire_led_project_shadow'
$projectBuildScript = Join-Path $workspaceRoot 'build_load_run.ps1'
$projectStartScript = Join-Path $workspaceRoot 'START_CCS.ps1'
$agentLoopScript = Join-Path $taskRoot 'scripts/agentic_dev_loop.ps1'
$dssPinBlinkScript = Join-Path $taskRoot 'scripts/run_pin_blink_dss.js'
$noHumanAutopilotScript = Join-Path $taskRoot 'scripts/launchpad_nohuman_autopilot.ps1'

$examplePaths = [ordered]@{
    hello_world = Join-Path $sdkRoot 'examples/hello_world/hello_world.c'
    gpio_led_blink = Join-Path $sdkRoot 'examples/drivers/gpio/gpio_led_blink/gpio_led_blink.c'
    mcspi_loopback_sdk = Join-Path $sdkRoot 'examples/drivers/mcspi/mcspi_loopback/mcspi_loopback.c'
    mcspi_loopback_workspace = Join-Path $workspaceRoot 'mcspi_loopback.c'
}

function Assert-Path([string]$path, [string]$label) {
    if (-not (Test-Path $path)) {
        throw "Missing ${label}: $path"
    }
}

function Write-Section([string]$text) {
    Write-Host "`n=== $text ===" -ForegroundColor Cyan
}

function Write-ItemLine([string]$name, [string]$value) {
    Write-Host ("{0,-24} {1}" -f $name, $value)
}

function Show-Status {
    Write-Section 'CCS Control Surface'
    Write-ItemLine 'CCS EXE' $ccsExe
    Write-ItemLine 'GMAKE' $gmake
    Write-ItemLine 'LOADTI' $loadti
    Write-ItemLine 'DSS' $dss
    Write-ItemLine 'Workspace' $workspaceRoot
    Write-ItemLine 'Build Script' $projectBuildScript
    Write-ItemLine 'Agent Loop' $agentLoopScript

    Write-Section 'Example Sources'
    foreach ($entry in $examplePaths.GetEnumerator()) {
        $exists = if (Test-Path $entry.Value) { 'OK' } else { 'MISSING' }
        Write-ItemLine $entry.Key ("[$exists] $($entry.Value)")
    }

    Write-Section 'Board And Port Status'
    & $agentLoopScript -Action status
}

function Open-InExplorer([string]$path) {
    Assert-Path $path 'target path'
    if ((Get-Item $path) -is [System.IO.DirectoryInfo]) {
        Start-Process explorer.exe $path | Out-Null
    }
    else {
        Start-Process explorer.exe "/select,`"$path`"" | Out-Null
    }
}

function Sync-ShadowWorkspace {
    Assert-Path $workspaceRoot 'primary workspace root'
    if (-not (Test-Path $shadowWorkspaceRoot)) {
        New-Item -ItemType Directory -Path $shadowWorkspaceRoot | Out-Null
    }

    $robocopyArgs = @(
        $workspaceRoot,
        $shadowWorkspaceRoot,
        '/MIR',
        '/XD', '.theia', '.git', 'migration_snapshot',
        '/XF', '*.theia-workspace'
    )

    & robocopy @robocopyArgs | Out-Null
    $rc = $LASTEXITCODE
    if ($rc -ge 8) {
        throw "robocopy failed while preparing shadow workspace (exit code $rc)"
    }

    Write-Host 'Shadow workspace synced.' -ForegroundColor Green
    Write-Host "Shadow path: $shadowWorkspaceRoot"
}

function Open-CcsOnPath([string]$target, [string]$label) {
    Assert-Path $ccsExe 'CCS executable'
    Assert-Path $target $label
    Start-Process -FilePath $ccsExe -ArgumentList "`"$target`"" | Out-Null
    Write-Host "CCS launch requested on $label."
    Write-Host "Target: $target"
}

function Run-Build([bool]$buildOnly, [bool]$loadOnly, [bool]$runAfterLoad) {
    Assert-Path $projectBuildScript 'project build/load script'
    if ($buildOnly) {
        & $projectBuildScript -BuildOnly
        return
    }

    if ($loadOnly) {
        & $projectBuildScript -LoadOnly -RunAfterLoad:$runAfterLoad
        return
    }

    & $projectBuildScript -RunAfterLoad:$runAfterLoad
}

function Run-AgentLoop([string]$loopAction) {
    Assert-Path $agentLoopScript 'agentic loop script'
    if ($loopAction -eq 'monitor-uart' -and $ExpectText) {
        & $agentLoopScript -Action $loopAction -MonitorSeconds $MonitorSeconds -ExpectText $ExpectText
    }
    elseif ($loopAction -eq 'monitor-uart') {
        & $agentLoopScript -Action $loopAction -MonitorSeconds $MonitorSeconds
    }
    else {
        & $agentLoopScript -Action $loopAction
    }
}

Assert-Path $ccsExe 'CCS executable'
Assert-Path $gmake 'gmake'
Assert-Path $loadti 'loadti'
Assert-Path $dss 'dss'
Assert-Path $workspaceRoot 'workspace root'

switch ($Action) {
    'status' {
        Show-Status
    }
    'open-ccs' {
        Assert-Path $projectStartScript 'CCS start script'
        & $projectStartScript
    }
    'open-ccs-secondary' {
        Assert-Path $projectStartScript 'CCS start script'
        & $projectStartScript -SecondaryWorkspace
    }
    'prepare-ccs-shadow' {
        Sync-ShadowWorkspace
    }
    'open-ccs-shadow' {
        Sync-ShadowWorkspace
        Open-CcsOnPath -target $shadowWorkspaceRoot -label 'shadow workspace'
    }
    'build-project' {
        Run-Build -buildOnly $true -loadOnly $false -runAfterLoad $RunAfterLoad
    }
    'load-project' {
        Run-Build -buildOnly $false -loadOnly $true -runAfterLoad $RunAfterLoad
    }
    'build-load-project' {
        Run-Build -buildOnly $false -loadOnly $false -runAfterLoad $RunAfterLoad
    }
    'follow-uart' {
        Run-AgentLoop -loopAction 'follow-uart'
    }
    'monitor-uart' {
        Run-AgentLoop -loopAction 'monitor-uart'
    }
    'dss-pin-blink' {
        Assert-Path $dssPinBlinkScript 'DSS pin blink script'
        & $dss $dssPinBlinkScript
    }
    'autopilot-nohuman' {
        Assert-Path $noHumanAutopilotScript 'no-human autopilot script'
        & $noHumanAutopilotScript
    }
    'show-examples' {
        Write-Section 'Example Sources'
        foreach ($entry in $examplePaths.GetEnumerator()) {
            Write-ItemLine $entry.Key $entry.Value
        }
    }
    'open-project-folder' {
        Open-InExplorer $workspaceRoot
    }
    'open-gpio-source' {
        Open-InExplorer $examplePaths['gpio_led_blink']
    }
    'open-mcspi-source' {
        Open-InExplorer $examplePaths['mcspi_loopback_workspace']
    }
    'open-hello-source' {
        Open-InExplorer $examplePaths['hello_world']
    }
}