param(
    [switch]$BuildOnly,
    [switch]$LoadOnly,
    [switch]$RunAfterLoad = $true
)

$proj = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/am243x-lp/r5fss0-0_nortos/ti-arm-clang'
$out = "$proj/mcspi_loopback.release.out"
$ccxml = 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/am2434_xds110_generated.ccxml'
$gmake = 'C:/ti/ccs2050/ccs/utils/bin/gmake.exe'
$loadti = 'C:/ti/ccs2050/ccs/ccs_base/scripting/examples/loadti/loadti.bat'

& "$PSScriptRoot/env_ccs2050.ps1" | Out-Null

if (-not $LoadOnly) {
    Push-Location $proj
    & $gmake all
    $buildCode = $LASTEXITCODE
    Pop-Location

    if ($buildCode -ne 0 -and -not (Test-Path $out)) {
        throw "Build failed and output not found: $out"
    }
}

if ($BuildOnly) { exit 0 }

if ($RunAfterLoad) {
    & $loadti -c="$ccxml" -r "$out"
} else {
    & $loadti -c="$ccxml" -l "$out"
}
