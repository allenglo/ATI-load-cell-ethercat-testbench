#!powershell
# Build and flash UART echo test for AM243x LaunchPad

$SDK_PATH = "C:/ti/mcu_plus_sdk_am243x_12_00_00_26"
$CCS_PATH = "C:/ti/ccs2050/ccs"
$SYSCFG_PATH = "$CCS_PATH/utils/sysconfig_1.27.0"
$PROJECT_DIR = $PSScriptRoot
$BUILD_DIR = "$PROJECT_DIR/am243x-lp/r5fss0-0_nortos/ti-arm-clang"

Write-Host "=== Building UART Echo Test ===" -ForegroundColor Cyan
Write-Host "Project: $PROJECT_DIR"
Write-Host "Build dir: $BUILD_DIR"

# Change to build directory
Push-Location $BUILD_DIR

# Clean old build
if (Test-Path "obj") { Remove-Item -Recurse -Force "obj" }
if (Test-Path "*.out") { Remove-Item -Force "*.out" }

# Run gmake
Write-Host "Running gmake..." -ForegroundColor Yellow
$env:SDK_PATH = $SDK_PATH
$env:TOOLS_PATH = "C:/ti"
gmake -f makefile all

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "✓ Build OK" -ForegroundColor Green

# Copy boot image
$bootImg = Get-Item "*.mcelf.hs_fs" -ErrorAction SilentlyContinue
if ($bootImg) {
    $stageDir = "$PROJECT_DIR/../../../flash_stage_test"
    New-Item -ItemType Directory -Force -Path $stageDir | Out-Null
    Copy-Item $bootImg.FullName "$stageDir/uart_echo.release.mcelf.hs_fs" -Force
    Write-Host "✓ Boot image: $($bootImg.Name)" -ForegroundColor Green
}

Pop-Location
Write-Host "Done!" -ForegroundColor Green
