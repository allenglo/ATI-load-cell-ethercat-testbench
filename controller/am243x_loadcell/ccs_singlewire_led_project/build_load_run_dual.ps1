# Build/Load Dual SPI LEDs Project
# Usage: .\build_load_run_dual.ps1 [-BuildOnly] [-LoadOnly] [-RunAfterLoad]

param(
    [switch]$BuildOnly,
    [switch]$LoadOnly,
    [switch]$FlashOnly,
    [switch]$RunAfterLoad,
    [string]$ComPort = "COM9"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$CCS_PATH    = "C:/ti/ccs2050/ccs"
$SDK_PATH    = "C:/ti/mcu_plus_sdk_am243x_12_00_00_26"
$gmake       = "$CCS_PATH/utils/bin/gmake.exe"
$loadti      = "$CCS_PATH/ccs_base/scripting/examples/loadti/loadti.bat"
$ccxml       = (Join-Path (Split-Path $ProjectRoot -Parent) "am2434_xds110_generated.ccxml")
$uartUniflash = "$SDK_PATH/tools/boot/uart_uniflash.py"
$flashWriter  = "$SDK_PATH/tools/boot/sbl_prebuilt/am243x-lp/sbl_uart_uniflash.release.hs_fs.tiimage"
$ospiSbl      = "$SDK_PATH/tools/boot/sbl_prebuilt/am243x-lp/sbl_ospi.release.hs_fs.tiimage"
$probeBootMode = Join-Path (Split-Path $ProjectRoot -Parent) "scripts/probe_boot_mode.ps1"

# Setup environment
& "$ProjectRoot/env_ccs2050.ps1" | Out-Null

$venvScripts = "C:/CoRoot/.venv/Scripts"
if (Test-Path $venvScripts) {
    $env:Path = "$venvScripts;$env:Path"
}

$opensslDir = "C:/Program Files/Git/usr/bin"
if (Test-Path (Join-Path $opensslDir "openssl.exe")) {
    $env:Path = "$opensslDir;$env:Path"
}

Write-Host "SDK_PATH=$SDK_PATH"
Write-Host ""

$buildDir = "$ProjectRoot/am243x-lp/r5fss0-0_nortos/ti-arm-clang"
$outFile = "mcspi_loopback.release.out"
$outPath = "$buildDir/$outFile"
$flashCfgPath = "$buildDir/mcspi_loopback_flash.cfg"
$flashStageDir = "C:/CoRoot/flash_stage_am243x"
$flashAppPath = "$flashStageDir/mcspi_loopback.release.mcelf.hs_fs"

function Get-BootImagePath {
    param([string]$Dir)

    $preferred = Join-Path $Dir "mcspi_loopback.release.mcelf.hs_fs"
    if (Test-Path $preferred) {
        return $preferred
    }

    $fallback = Get-ChildItem -Path $Dir -Filter "*.mcelf.hs_fs" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -ne $fallback) {
        return $fallback.FullName
    }

    return $preferred
}

$mcelfPath = Get-BootImagePath -Dir $buildDir

# === BUILD ===
if (-not $LoadOnly)
{
    Write-Host "=== Building Dual SPI LED Driver ===" -ForegroundColor Cyan
    
    # Copy source files to build directory (avoids path issues)
    Copy-Item "$ProjectRoot/dual_spi_leds.c" -Destination "$buildDir/dual_spi_leds.c" -Force
    Copy-Item "$ProjectRoot/addressable_led.c" -Destination "$buildDir/addressable_led.c" -Force
    Copy-Item "$ProjectRoot/addressable_led.h" -Destination "$buildDir/addressable_led.h" -Force
    
    Push-Location $buildDir
    
    # Build with dual sources (replaces mcspi_loopback.c in FILES_common)
    & $gmake -j4 PROFILE=release `
        OUTNAME=$outFile `
        FILES_common="dual_spi_leds.c addressable_led.c main.c ti_drivers_config.c ti_drivers_open_close.c ti_board_config.c ti_board_open_close.c ti_dpl_config.c ti_pinmux_config.c ti_power_clock_config.c"
    
    $buildCode = $LASTEXITCODE
    Pop-Location
    
    if ($buildCode -ne 0 -and -not (Test-Path $outPath)) {
        Write-Host "Build failed" -ForegroundColor Red
        exit 1
    }

    $mcelfPath = Get-BootImagePath -Dir $buildDir
    if (-not (Test-Path $mcelfPath)) {
        Write-Host "Build did not produce boot image: $mcelfPath" -ForegroundColor Red
        Write-Host "Make sure Python deps are installed in C:/CoRoot/.venv and openssl is on PATH." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Build OK: $outPath" -ForegroundColor Green
    Write-Host "Boot image OK: $mcelfPath" -ForegroundColor Green
    Write-Host ""
}

# === LOAD ===
if (-not $BuildOnly)
{
    if ($FlashOnly)
    {
        Write-Host "=== Flashing OSPI (persistent) ===" -ForegroundColor Cyan

        $mcelfPath = Get-BootImagePath -Dir $buildDir
        if (-not (Test-Path $mcelfPath)) {
            Write-Host "Error: $mcelfPath not found" -ForegroundColor Red
            exit 1
        }

        New-Item -ItemType Directory -Force -Path $flashStageDir | Out-Null
        Copy-Item $mcelfPath -Destination $flashAppPath -Force

        @(
            "--flash-writer=$($flashWriter -replace '\\','/')",
            "--operation=flash-phy-tuning-data",
            "--file=$($ospiSbl -replace '\\','/') --operation=flash --flash-offset=0x0",
            "--file=$($flashAppPath -replace '\\','/') --operation=flash --flash-offset=0x80000"
        ) | Set-Content -Path $flashCfgPath -Encoding ascii

        Write-Host "Using flash COM port: $ComPort" -ForegroundColor Yellow
        Write-Host "Board must be in UART boot mode (1110 0000) before running this step." -ForegroundColor Yellow

        if ($ComPort -ieq 'COM10') {
            Write-Host "Warning: COM10 is usually the application/user UART. Flashing normally uses COM9 (Auxiliary Data Port)." -ForegroundColor Yellow
        }

        if (Test-Path $probeBootMode) {
            Write-Host "Probing boot mode on $ComPort before flash..." -ForegroundColor Cyan
            & $probeBootMode -Ports @($ComPort) -Seconds 3
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Boot mode probe did not report UART boot on $ComPort. Set SW4 to 1110 0000 and power-cycle before flashing." -ForegroundColor Red
                exit 1
            }
        }

        Push-Location "$SDK_PATH/tools/boot"
        & python "$uartUniflash" -p $ComPort --cfg="$flashCfgPath"
        $flashCode = $LASTEXITCODE
        Pop-Location

        if ($flashCode -ne 0) {
            Write-Host "Flash failed" -ForegroundColor Red
            exit 1
        }

        Write-Host "Flash OK. Set boot mode back to OSPI (0100 0100) and power-cycle the board." -ForegroundColor Green
    }
    else
    {
        Write-Host "=== Loading ===" -ForegroundColor Cyan
        
        if (-not (Test-Path $outPath)) {
            Write-Host "Error: $outPath not found" -ForegroundColor Red
            exit 1
        }
        
        if (-not (Test-Path $ccxml)) {
            Write-Host "Error: $ccxml not found" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Loading $outFile..."
        $loadLog = & $loadti -c="$ccxml" -r "$outPath" 2>&1
        $loadLog | ForEach-Object { $_ }

        $loadText = ($loadLog | Out-String)
        $loadHasErrors = ($loadText -match 'SEVERE:') -or
            ($loadText -match 'load failed') -or
            ($loadText -match 'Error code #')

        if ($LASTEXITCODE -ne 0 -or $loadHasErrors) {
            Write-Host "Load failed" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Load OK" -ForegroundColor Green
    }
}

Write-Host "Done." -ForegroundColor Green
