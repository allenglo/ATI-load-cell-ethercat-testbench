# flash_and_test.ps1
# Complete script to flash SBL NULL (one-time init) and then load examples via JTAG
# Run after setting physical boot mode switches as described below.
#
# ============================================================
# PHYSICAL BOARD STEPS (do these manually):
#
# STEP 1 - Flash SBL NULL (one-time, needed once):
#   a) Power OFF the board
#   b) Set SW4 = 1110 0000  (UART BOOT MODE)
#   c) Power ON the board
#   d) Run section: flash-sbl-null  (see below)
#   e) Power OFF the board
#   f) Set SW4 = 0100 0100  (OSPI BOOT MODE)
#   g) Power ON the board
#   h) From now on, use CCS JTAG to load examples (no switch change needed)
#
# STEP 2 - Load example via CCS JTAG (after SBL NULL is flashed):
#   - Open CCS -> Target Configuration -> am243x_lp_xds110.ccxml -> Launch
#   - Connect to MAIN_Cortex_R5_0_0
#   - Reset CPU
#   - Load Program -> browse to the .out file
#   - Resume
# ============================================================

param(
    [ValidateSet('flash-sbl-null', 'flash-led-blink', 'flash-hello-world', 'build-adc', 'help')]
    [string]$Action = 'help',
    [string]$Port = 'COM9'
)

$sdk     = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26'
$py      = 'c:\CoRoot\.venv\Scripts\python.exe'
$boot    = "$sdk\tools\boot"
$openssl = 'C:\Program Files\Git\usr\bin'
$gmake   = 'C:\ti\ccs2050\ccs\utils\bin\gmake.exe'

$env:PATH = "$openssl;$env:PATH"

function Sign-Image($mcelf, $signed) {
    $script = "$sdk\tools\boot\signing\appimage_x509_cert_gen.py"
    $key    = "$sdk\tools\boot\signing\rom_degenerateKey.pem"
    & $py $script --bin $mcelf --key $key --output $signed --swrv 1 --loadaddr 0x70000000 --sign_key_id 0 --imageType APPIMAGE
    if ($LASTEXITCODE -ne 0) { throw "Signing failed for $mcelf" }
}

switch ($Action) {
    'flash-sbl-null' {
        Write-Host "`n[ACTION] Flashing SBL NULL to OSPI flash via UART on $Port"
        Write-Host "  Board must be in UART BOOT MODE (SW4 = 1110 0000)"
        Push-Location $boot
        & $py uart_uniflash.py -p $Port --cfg="sbl_prebuilt/am243x-lp/default_sbl_null.cfg"
        Pop-Location
    }

    'flash-led-blink' {
        Write-Host "`n[ACTION] Flashing gpio_led_blink to OSPI flash via UART on $Port"
        Write-Host "  Board must be in UART BOOT MODE (SW4 = 1110 0000)"
        $cfg = 'C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\demo\gpio_led_blink_uart_ospi.cfg'
        Push-Location $boot
        & $py uart_uniflash.py -p $Port --cfg="$cfg"
        Pop-Location
    }

    'flash-hello-world' {
        Write-Host "`n[ACTION] Flashing hello_world to OSPI flash via UART on $Port"
        Write-Host "  Board must be in UART BOOT MODE (SW4 = 1110 0000)"
        $dir = "$sdk\examples\hello_world\am243x-lp\r5fss0-0_freertos\ti-arm-clang"
        # Build if needed
        if (-not (Test-Path "$dir\hello_world.release.mcelf.hs_fs")) {
            Write-Host "  Building hello_world first..."
            & $gmake -s -C "$sdk\examples\hello_world\am243x-lp\r5fss0-0_freertos\ti-arm-clang" `
                CCS_PATH=C:/ti/ccs2050/ccs TOOLS_PATH=C:/ti `
                SYSCFG_PATH=C:/ti/ccs2050/ccs/utils/sysconfig_1.27.0 `
                PYTHON=c:/CoRoot/.venv/Scripts/python.exe
            if (-not (Test-Path "$dir\hello_world.release.mcelf")) {
                throw "Build failed, no mcelf output"
            }
            Sign-Image "$dir\hello_world.release.mcelf" "$dir\hello_world.release.mcelf.hs_fs"
        }
        # Flash
        $cfgContent = @"
--flash-writer=sbl_prebuilt/am243x-lp/sbl_uart_uniflash.release.hs_fs.tiimage
--file=$dir\hello_world.release.mcelf.hs_fs --operation=flash --flash-offset=0x80000
"@
        $tmpCfg = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.cfg'
        $cfgContent | Set-Content $tmpCfg
        Push-Location $boot
        & $py uart_uniflash.py -p $Port --cfg="$tmpCfg"
        Pop-Location
        Remove-Item $tmpCfg -Force
    }

    'build-adc' {
        Write-Host "`n[ACTION] Building adc_singleshot example"
        $adcDir = "$sdk\examples\drivers\adc\adc_singleshot\am243x-lp\r5fss0-0_freertos\ti-arm-clang"
        & $gmake -s -C $adcDir `
            CCS_PATH=C:/ti/ccs2050/ccs TOOLS_PATH=C:/ti `
            SYSCFG_PATH=C:/ti/ccs2050/ccs/utils/sysconfig_1.27.0 `
            PYTHON=c:/CoRoot/.venv/Scripts/python.exe
        if ($LASTEXITCODE -eq 0 -and (Test-Path "$adcDir\adc_singleshot.release.mcelf")) {
            Write-Host "  Build succeeded. Signing..."
            Sign-Image "$adcDir\adc_singleshot.release.mcelf" "$adcDir\adc_singleshot.release.mcelf.hs_fs"
            Write-Host "  Signed output: $adcDir\adc_singleshot.release.mcelf.hs_fs"
        } else {
            Write-Host "  Build failed or mcelf missing."
        }
    }

    default {
        Write-Host @"
Usage: .\flash_and_test.ps1 -Action <action> [-Port COM9]

Actions:
  flash-sbl-null    One-time flash of SBL NULL bootloader (must be done once before CCS JTAG loading)
                    Board must be in UART BOOT MODE (SW4 = 1110 0000)

  flash-led-blink   Flash gpio_led_blink to OSPI flash
                    Board must be in UART BOOT MODE (SW4 = 1110 0000)

  flash-hello-world Flash hello_world to OSPI flash
                    Board must be in UART BOOT MODE (SW4 = 1110 0000)

  build-adc         Build the adc_singleshot example (no flash needed yet)

Boot mode switch settings (SW4, LP-AM243x):
  UART boot:  SW4 = 1110 0000   (for flashing)
  OSPI boot:  SW4 = 0100 0100   (for running flashed apps)
  DEV  boot:  SW4 = 1111 0000   (for CCS scripting path)

CCS JTAG load (recommended for development):
  1. Flash SBL NULL once (uart boot → flash → ospi boot)
  2. Set OSPI boot mode, power on
  3. Open CCS → Target Configurations → am243x_lp_xds110.ccxml → Launch
  4. Connect MAIN_Cortex_R5_0_0 → Reset → Load Program (.out file) → Resume
  5. Watch output on UART terminal (COM9, 115200 baud)

Built .out files ready to load:
  hello_world:    $sdk\examples\hello_world\am243x-lp\r5fss0-0_freertos\ti-arm-clang\hello_world.release.out
  gpio_led_blink: $sdk\examples\drivers\gpio\gpio_led_blink\am243x-lp\r5fss0-0_nortos\ti-arm-clang\gpio_led_blink.release.out
"@
    }
}
