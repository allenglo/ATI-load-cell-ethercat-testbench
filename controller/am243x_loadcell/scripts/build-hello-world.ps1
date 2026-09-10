param(
    [string]$SdkPath = $env:MCU_PLUS_SDK_AM243X_PATH,
    [string]$Board = 'am243x-lp'
)

if (-not $SdkPath) {
    $SdkPath = 'C:\ti\mcu_plus_sdk_am243x_12_00_00_26'
}

if (-not (Test-Path $SdkPath)) {
    Write-Error "SDK path not found: $SdkPath"
    exit 1
}

$gmake = Get-Command gmake -ErrorAction SilentlyContinue
if (-not $gmake) {
    Write-Error 'gmake is not on PATH yet. Install the TI toolchain and reopen the shell.'
    exit 1
}

$exampleDir = Join-Path $SdkPath "examples\hello_world\$Board\r5fss0-0_freertos\ti-arm-clang"
if (-not (Test-Path $exampleDir)) {
    Write-Error "Example path not found: $exampleDir"
    exit 1
}

Push-Location $SdkPath
try {
    & $gmake.Source -s -C $exampleDir
} finally {
    Pop-Location
}

Write-Host ''
Write-Host 'If the build succeeded, check the example directory for the generated hello_world output and mcelf image.' -ForegroundColor Cyan