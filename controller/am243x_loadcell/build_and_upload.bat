@REM Build and Upload LED Control App to AM243x LaunchPad
@REM This script compiles the LED control application and loads it via JTAG

@echo off
setlocal enabledelayedexpansion

REM Configuration
set SDK_PATH=C:\ti\mcu_plus_sdk_am243x_12_00_00_26
set CCS_PATH=C:\ti\ccs2050
set PROJECT_PATH=C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex
set CONFIG_FILE=%PROJECT_PATH%\am2434_xds110_generated.ccxml
set OUTPUT_DIR=%PROJECT_PATH%\build

REM TI Compiler paths
set ARM_COMPILER=%CCS_PATH%\ccs\tools\compiler\ti-cgt-arm_20.2.7.LTS\bin\armcl.exe
set ARM_ARCH=-mv7R5 --abi=eabi
set INCLUDES=-I%SDK_PATH%\source\kernel\dpl -I%SDK_PATH%\source\drivers\gpio -I%SDK_PATH%\examples\drivers\gpio\gpio_multi_led_blink

REM Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo.
echo ======================================
echo AM243x LED Control - Build & Upload
echo ======================================
echo.
echo Project Path: %PROJECT_PATH%
echo Output Dir:   %OUTPUT_DIR%
echo.

REM Compile the source file
echo [1/3] Compiling LED control code...
echo Command: %ARM_COMPILER% %ARM_ARCH% %INCLUDES% -o "%OUTPUT_DIR%\led_blink.o" "%PROJECT_PATH%\led_blink_simple.c"
echo.

REM Note: This is a simplified placeholder - actual compilation requires proper linker scripts and libraries
echo NOTE: Full compilation requires CCS project configuration or proper linker setup.
echo Please import this source file into a CCS project with AM243x configuration.
echo.

echo [2/3] Creating executable...
echo Skipped - use CCS to build or create proper linker script
echo.

echo [3/3] Uploading to board via JTAG...
cd "%CCS_PATH%\ccs\ccs_base\scripting\examples\loadti"

REM Load the bootloader first (if not already loaded)
echo Loading SBL bootloader...
call loadti.bat ^
  -c="%CONFIG_FILE%" ^
  -cpu=MAIN_Cortex_R5_0_0 ^
  -l -r -v ^
  "%SDK_PATH%\examples\drivers\boot\sbl_jtag_uniflash\am243x-lp\r5fss0-0_nortos\ti-arm-clang\sbl_jtag_uniflash.release.out"

if errorlevel 1 (
    echo.
    echo ERROR: Bootloader upload failed!
    goto error
)

echo.
echo ======================================
echo Build and Upload Instructions
echo ======================================
echo.
echo To complete the LED control build:
echo.
echo 1. Open CCS (CodeComposer Studio)
echo 2. Create a new project:
echo    - Target: AM243x LaunchPad
echo    - CPU: MAIN_Cortex_R5_0_0
echo    - Runtime: No RTOS
echo.
echo 3. Add source file:
echo    - Add "%PROJECT_PATH%\led_blink_simple.c"
echo.
echo 4. Configure project includes:
echo    - %SDK_PATH%\source\kernel\dpl
echo    - %SDK_PATH%\source\drivers\gpio
echo    - %SDK_PATH%\source\drivers\uart
echo.
echo 5. Link against SDK libraries:
echo    - ti.drivers (GPIO, Clock, Debug)
echo    - kernel DPL
echo.
echo 6. Build project (Project -^> Build)
echo.
echo 7. Debug and Run:
echo    - Debug (F11) to connect to target
echo    - Run (F8) to execute
echo.
echo ======================================
echo.

goto end

:error
echo.
echo ERROR: Build/Upload failed
exit /b 1

:end
endlocal
