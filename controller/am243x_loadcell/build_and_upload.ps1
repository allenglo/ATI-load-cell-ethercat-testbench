# AM243x LED Control Project - Build & Upload Script
# PowerShell version for easier management and debugging

param(
    [switch]$BuildOnly = $false,
    [switch]$UploadOnly = $false,
    [switch]$Clean = $false
)

# Configuration
$SDK_PATH = "C:\ti\mcu_plus_sdk_am243x_12_00_00_26"
$CCS_PATH = "C:\ti\ccs2050"
$PROJECT_PATH = "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex"
$CONFIG_FILE = "$PROJECT_PATH\am2434_xds110_generated.ccxml"
$OUTPUT_DIR = "$PROJECT_PATH\build"
$SOURCE_FILE = "$PROJECT_PATH\led_blink_simple.c"

# TI Tool paths
$ARM_COMPILER = "$CCS_PATH\ccs\tools\compiler\ti-cgt-arm_20.2.7.LTS\bin\armcl.exe"
$ARM_LINKER = "$CCS_PATH\ccs\tools\compiler\ti-cgt-arm_20.2.7.LTS\bin\armlnk.exe"
$LOADTI_PATH = "$CCS_PATH\ccs\ccs_base\scripting\examples\loadti\loadti.bat"
$BOOTLOADER = "$SDK_PATH\examples\drivers\boot\sbl_jtag_uniflash\am243x-lp\r5fss0-0_nortos\ti-arm-clang\sbl_jtag_uniflash.release.out"

# Display header
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AM243x LED Control - Build & Upload" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verify prerequisites
Write-Host "[*] Verifying prerequisites..." -ForegroundColor Yellow
$missingTools = @()

if (-not (Test-Path $ARM_COMPILER)) { $missingTools += "ARM Compiler"; Write-Host "  ✗ ARM Compiler not found: $ARM_COMPILER" -ForegroundColor Red }
if (-not (Test-Path $SOURCE_FILE)) { $missingTools += "Source File"; Write-Host "  ✗ Source file not found: $SOURCE_FILE" -ForegroundColor Red }
if (-not (Test-Path $CONFIG_FILE)) { $missingTools += "CCXML Config"; Write-Host "  ✗ CCXML config not found: $CONFIG_FILE" -ForegroundColor Red }
if (-not (Test-Path $BOOTLOADER)) { $missingTools += "Bootloader"; Write-Host "  ✗ Bootloader not found: $BOOTLOADER" -ForegroundColor Red }

if ($missingTools.Count -gt 0) {
    Write-Host "`n✗ Missing tools/files: $($missingTools -join ', ')" -ForegroundColor Red
    Write-Host "Cannot proceed with build." -ForegroundColor Red
    exit 1
} else {
    Write-Host "  ✓ All tools and files found" -ForegroundColor Green
}

# Clean operation
if ($Clean) {
    Write-Host "`n[1/4] Cleaning build artifacts..." -ForegroundColor Yellow
    if (Test-Path $OUTPUT_DIR) {
        Remove-Item $OUTPUT_DIR -Recurse -Force
        Write-Host "  ✓ Build directory cleaned" -ForegroundColor Green
    }
}

# Build only message
if ($UploadOnly) {
    Write-Host "`n[!] Upload-only mode - skipping build phase`n" -ForegroundColor Cyan
    goto Upload
}

# Create output directory
if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null
    Write-Host "  ✓ Created output directory: $OUTPUT_DIR" -ForegroundColor Green
}

# Compilation information
Write-Host "`n[2/4] Build Information:" -ForegroundColor Yellow
Write-Host "  Source:     $SOURCE_FILE" -ForegroundColor Gray
Write-Host "  Output Dir: $OUTPUT_DIR" -ForegroundColor Gray
Write-Host "  Compiler:   $ARM_COMPILER" -ForegroundColor Gray

Write-Host "`n[3/4] Project Build Status:" -ForegroundColor Yellow
Write-Host "  ⓘ Recommended: Import source into CCS and build through IDE" -ForegroundColor Cyan
Write-Host "  ⓘ CCS handles dependencies, linker scripts, and SDK integration" -ForegroundColor Cyan

Write-Host "`n  For command-line build, use:" -ForegroundColor Gray
Write-Host "    & '$ARM_COMPILER' -mv7R5 --abi=eabi -O2 \" -ForegroundColor Gray
Write-Host "      -I'$SDK_PATH\source\kernel\dpl' \" -ForegroundColor Gray
Write-Host "      -I'$SDK_PATH\source\drivers\gpio' \" -ForegroundColor Gray
Write-Host "      -o '$OUTPUT_DIR\led_blink.o' \" -ForegroundColor Gray
Write-Host "      '$SOURCE_FILE'" -ForegroundColor Gray

# Upload section
:Upload

Write-Host "`n[*] Upload Phase:" -ForegroundColor Yellow

if (-not $BuildOnly) {
    Write-Host "`n[4/4] Loading bootloader via JTAG..." -ForegroundColor Yellow
    
    Write-Host "  Command:" -ForegroundColor Gray
    Write-Host "    $LOADTI_PATH -c=`"$CONFIG_FILE`" -cpu=MAIN_Cortex_R5_0_0 -l -r -v `"$BOOTLOADER`"" -ForegroundColor Gray
    Write-Host "`n  Executing..." -ForegroundColor Cyan
    
    & $LOADTI_PATH -c="$CONFIG_FILE" -cpu=MAIN_Cortex_R5_0_0 -l -r -v "$BOOTLOADER"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n  ✓ Bootloader loaded successfully" -ForegroundColor Green
    } else {
        Write-Host "`n  ✗ Bootloader upload failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
}

# Final instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "1. Build the LED Control Application:" -ForegroundColor Yellow
Write-Host "   a) Open CCS and create new project (AM243x LaunchPad)" -ForegroundColor Gray
Write-Host "   b) Add source: led_blink_simple.c" -ForegroundColor Gray
Write-Host "   c) Configure SDK includes and libraries" -ForegroundColor Gray
Write-Host "   d) Build project (Project → Build)" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Load and Execute:" -ForegroundColor Yellow
Write-Host "   a) Open debug configuration" -ForegroundColor Gray
Write-Host "   b) Connect to target (F11)" -ForegroundColor Gray
Write-Host "   c) Run application (F8)" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Verify Execution:" -ForegroundColor Yellow
Write-Host "   a) Watch for console output on UART" -ForegroundColor Gray
Write-Host "   b) Observe LED blink pattern (if external LEDs connected)" -ForegroundColor Gray
Write-Host "   c) Application runs for 60 seconds" -ForegroundColor Gray
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "   - LED_PROJECT_SETUP.md - Complete build guide" -ForegroundColor Gray
Write-Host "   - led_blink_simple.c   - Source code with comments" -ForegroundColor Gray
Write-Host "   - AM243x_LAUNCHPAD_SETUP_MASTER.md - Full board reference" -ForegroundColor Gray

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Build script completed successfully!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
