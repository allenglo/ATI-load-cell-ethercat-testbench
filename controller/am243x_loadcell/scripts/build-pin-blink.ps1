# build-pin-blink.ps1
# Builds the modified gpio_led_blink (Blink-All-Pins demo) using the SDK makefile.
# Output: gpio_led_blink.release.out in the SDK example build dir.
#
# Usage:
#   .\build-pin-blink.ps1            # default
#   .\build-pin-blink.ps1 -Clean     # clean then build

param(
    [switch]$Clean
)

$ErrorActionPreference = 'Stop'

$buildDir = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26\examples\drivers\gpio\gpio_led_blink\am243x-lp\r5fss0-0_nortos\ti-arm-clang'
$gmake    = 'C:\ti\ccs2050\ccs\utils\bin\gmake.exe'
$sysconfig = 'C:/ti/ccs2050/ccs/utils/sysconfig_1.27.0'
$cgt      = 'C:/ti/ccs2050/ccs/tools/compiler/ti-cgt-armllvm_4.0.4.LTS'
$python   = 'c:/CoRoot/.venv/Scripts/python.exe'
$openssl  = 'C:\Program Files\Git\usr\bin'

$env:PATH = "$openssl;$env:PATH"

Write-Host "[build-pin-blink] Build dir: $buildDir"

Push-Location $buildDir
try {
    if ($Clean) {
        Write-Host "[build-pin-blink] Cleaning..."
        & $gmake clean "CGT_TI_ARM_CLANG_PATH=$cgt" SYSCFG_PATH=$sysconfig PYTHON=$python
        if ($LASTEXITCODE -ne 0) {
            throw "Clean failed with exit code $LASTEXITCODE"
        }
    }

    Write-Host "[build-pin-blink] Building (gpio_led_blink Blink-All-Pins)..."
    & $gmake -j4 "CGT_TI_ARM_CLANG_PATH=$cgt" SYSCFG_PATH=$sysconfig PYTHON=$python
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }

    $out = "$buildDir\gpio_led_blink.release.out"
    if (Test-Path $out) {
        $f = Get-Item $out
        Write-Host "[build-pin-blink] SUCCESS: $out ($([math]::Round($f.Length/1KB)) KB, $($f.LastWriteTime))"
    } else {
        throw "Build completed but .out not found at $out"
    }
}
finally {
    Pop-Location
}
