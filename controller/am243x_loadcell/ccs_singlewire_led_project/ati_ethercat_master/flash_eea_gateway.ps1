#!/usr/bin/env pwsh
# flash_eea_gateway.ps1
# Build and flash eea_ecat_main.c to AM243x LaunchPad (UART boot mode required).
# Uses the same UART uniflash infrastructure as the mcspi/ATI project.
#
# USAGE:
#   .\flash_eea_gateway.ps1            # build then flash
#   .\flash_eea_gateway.ps1 -BuildOnly # build only, no flash
#   .\flash_eea_gateway.ps1 -FlashOnly # flash last .mcelf.hs_fs without build
#
# PRE-CONDITIONS:
#   1. Set LaunchPad SW4 boot mode to UART: 1110 0000
#   2. Power-cycle the board after changing boot mode
#   3. Board must be visible on COM port (default COM10 - override with -ComPort)

param(
    [switch]$BuildOnly,
    [switch]$FlashOnly,
    [string]$ComPort = "COM9"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSCommandPath
$CCS_ROOT    = "C:/ti/ccs2050/ccs"
$SDK_PATH    = "C:/ti/mcu_plus_sdk_am243x_12_00_00_26"
$BRIDGE_SRC  = "$ProjectRoot/../../demo/eea_gateway_bridge"
$SOEM_ROOT   = "$ProjectRoot/../../sdk/soem"

$gmake         = "$CCS_ROOT/utils/bin/gmake.exe"
$uartUniflash  = "$SDK_PATH/tools/boot/uart_uniflash.py"
$flashWriter   = "$SDK_PATH/tools/boot/sbl_prebuilt/am243x-lp/sbl_uart_uniflash.release.hs_fs.tiimage"
$ospiSbl       = "$SDK_PATH/tools/boot/sbl_prebuilt/am243x-lp/sbl_ospi.release.hs_fs.tiimage"

# Build target directory (reuse ati_ethercat_master build machinery)
$buildDir      = "$ProjectRoot/../am243x-lp/r5fss0-0_nortos/ti-arm-clang"
$flashStageDir = "C:/CoRoot/flash_stage_eea_gw"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " EEA Gateway - Build + Flash               " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ─── Environment ─────────────────────────────────────────────────────
& "$ProjectRoot/../env_ccs2050.ps1" | Out-Null
$env:Path = "C:/CoRoot/.venv/Scripts;C:/Program Files/Git/usr/bin;$env:Path"

function Assert-Exists {
    param($Path, $Label)
    if (-not (Test-Path $Path)) {
        Write-Host "  MISSING $Label : $Path" -ForegroundColor Red
        throw "Missing prerequisite: $Label"
    }
    Write-Host "  OK $Label" -ForegroundColor Green
}

Write-Host "[Check] Prerequisites..."
Assert-Exists $gmake          "gmake"
Assert-Exists $uartUniflash   "uart_uniflash.py"
Assert-Exists $flashWriter    "sbl_uart_uniflash"
Assert-Exists $ospiSbl        "sbl_ospi"
Assert-Exists "$BRIDGE_SRC/eea_gateway_bridge.c"  "eea_gateway_bridge.c"
Assert-Exists "$BRIDGE_SRC/eea_gateway_bridge.h"  "eea_gateway_bridge.h"
Assert-Exists "$SOEM_ROOT/include/soem/soem.h"    "soem.h"
Assert-Exists "$SOEM_ROOT/src/ec_main.c"          "soem core sources"
Write-Host ""

# ─── Build ───────────────────────────────────────────────────────────
if (-not $FlashOnly)
{
    Write-Host "[Build] Copying sources to build directory..." -ForegroundColor Yellow

    New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

    # Bridge module
    Copy-Item "$BRIDGE_SRC/eea_gateway_bridge.c" -Destination "$buildDir/eea_gateway_bridge.c" -Force
    Copy-Item "$BRIDGE_SRC/eea_gateway_bridge.h" -Destination "$buildDir/eea_gateway_bridge.h" -Force

    # SOEM headers and core sources
    Copy-Item "$SOEM_ROOT/include/soem" -Destination "$buildDir/soem" -Recurse -Force
    # SOEM headers reference "soem/..." from inside soem/soem.h; mirror one nested level.
    New-Item -ItemType Directory -Force -Path "$buildDir/soem/soem" | Out-Null
    Copy-Item "$SOEM_ROOT/include/soem/*" -Destination "$buildDir/soem/soem" -Recurse -Force
    Copy-Item "$SOEM_ROOT/osal/osal.h" -Destination "$buildDir/osal.h" -Force
    Copy-Item "$SOEM_ROOT/osal/osal.h" -Destination "$buildDir/soem/soem/osal.h" -Force
    Copy-Item "$SOEM_ROOT/src/ec_base.c"   -Destination "$buildDir/ec_base.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_main.c"   -Destination "$buildDir/ec_main.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_coe.c"    -Destination "$buildDir/ec_coe.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_foe.c"    -Destination "$buildDir/ec_foe.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_soe.c"    -Destination "$buildDir/ec_soe.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_eoe.c"    -Destination "$buildDir/ec_eoe.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_config.c" -Destination "$buildDir/ec_config.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_dc.c"     -Destination "$buildDir/ec_dc.c" -Force
    Copy-Item "$SOEM_ROOT/src/ec_print.c"  -Destination "$buildDir/ec_print.c" -Force

    # AM243x SOEM OSAL/OSHW glue
    Copy-Item "$ProjectRoot/osal/freertos/osal.c"      -Destination "$buildDir/osal.c" -Force
    Copy-Item "$ProjectRoot/osal/freertos/osal_defs.h" -Destination "$buildDir/osal_defs.h" -Force
    Copy-Item "$ProjectRoot/osal/freertos/osal_defs.h" -Destination "$buildDir/soem/soem/osal_defs.h" -Force
    Copy-Item "$ProjectRoot/oshw/am243x/oshw.c"        -Destination "$buildDir/oshw.c" -Force
    Copy-Item "$ProjectRoot/oshw/am243x/oshw.h"        -Destination "$buildDir/oshw.h" -Force
    Copy-Item "$ProjectRoot/oshw/am243x/nicdrv.c"      -Destination "$buildDir/nicdrv.c" -Force
    Copy-Item "$ProjectRoot/oshw/am243x/nicdrv.h"      -Destination "$buildDir/nicdrv.h" -Force

    # EEA master app
    Copy-Item "$ProjectRoot/app/eea_ecat_main.c" -Destination "$buildDir/eea_ecat_main.c" -Force

    Write-Host "[Build] Running gmake..." -ForegroundColor Yellow
    Push-Location $buildDir
    try {
        & $gmake -j4 `
            INCLUDES_common="-I. -I$CCS_ROOT/tools/compiler/ti-cgt-armllvm_4.0.4.LTS/include/c -I$SDK_PATH/source -I$SDK_PATH/source/networking/enet -I$SDK_PATH/source/networking/enet/core -I$SDK_PATH/source/networking/enet/core/include -I$SDK_PATH/source/networking/enet/soc/k3/am64x_am243x -I$SDK_PATH/source/board/ethphy/enet/rtos_drivers/include -Igenerated" `
            FILES_common="eea_ecat_main.c eea_gateway_bridge.c osal.c oshw.c nicdrv.c ec_base.c ec_main.c ec_coe.c ec_foe.c ec_soe.c ec_eoe.c ec_config.c ec_dc.c ec_print.c main.c ti_drivers_config.c ti_drivers_open_close.c ti_board_config.c ti_board_open_close.c ti_dpl_config.c ti_pinmux_config.c ti_power_clock_config.c" 2>&1 |
            Where-Object { $_ -notmatch "^make\[" } |
            ForEach-Object { Write-Host "  $_" }
        if ($LASTEXITCODE -ne 0) { throw "Build failed (exit $LASTEXITCODE)" }
    } finally {
        Pop-Location
    }
    Write-Host "[Build] Done." -ForegroundColor Green
    Write-Host ""
}

if ($BuildOnly) { Write-Host "BuildOnly mode - done."; exit 0 }

# ─── Locate built image ──────────────────────────────────────────────
$mcelfPath = Get-ChildItem -Path $buildDir -Filter "*.mcelf.hs_fs" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $mcelfPath) {
    throw "No .mcelf.hs_fs image found in $buildDir - build first."
}
Write-Host "[Flash] Using image: $mcelfPath" -ForegroundColor Cyan

# ─── Stage ───────────────────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $flashStageDir | Out-Null
Copy-Item $mcelfPath -Destination "$flashStageDir/" -Force

# ─── Confirm boot mode ───────────────────────────────────────────────
Write-Host ""
Write-Host "ACTION REQUIRED: Board must be in UART boot mode" -ForegroundColor Yellow
Write-Host "  SW4 = 1110 0000  (power-cycle after changing)" -ForegroundColor Yellow
Write-Host "  COM port: $ComPort @ 115200" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press ENTER when board is powered on in UART boot mode..." -ForegroundColor Cyan
Read-Host | Out-Null

# ─── Flash ───────────────────────────────────────────────────────────
Write-Host "[Flash] Writing SBL + app via UART uniflash..." -ForegroundColor Yellow

$imageName = Split-Path -Leaf $mcelfPath
$cfgContent = @"
--flash-writer=$flashWriter
--file=$ospiSbl --operation=flash --flash-offset=0x0
--operation=flash-phy-tuning-data
--file=$flashStageDir/$imageName --operation=flash --flash-offset=0x80000
"@

$cfgPath = "$flashStageDir/eea_gw_flash.cfg"
Set-Content -Path $cfgPath -Value $cfgContent -Encoding ASCII

Push-Location "$SDK_PATH/tools/boot"
& "c:/CoRoot/.venv/Scripts/python.exe" $uartUniflash -p $ComPort --cfg="$cfgPath"
$flashCode = $LASTEXITCODE
Pop-Location

if ($flashCode -ne 0) {
    Write-Host "[Flash] Flash script returned non-zero ($flashCode)." -ForegroundColor Red
    throw "Flash failed"
}

Write-Host ""
Write-Host "[Done] Flash complete." -ForegroundColor Green
Write-Host "  Switch SW4 back to OSPI boot mode: 0100 0100"
Write-Host "  Power-cycle to boot from flash."
