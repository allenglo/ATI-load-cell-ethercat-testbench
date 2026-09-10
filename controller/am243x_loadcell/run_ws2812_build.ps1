$ErrorActionPreference = "Stop"

$Sdk = "C:/ti/mcu_plus_sdk_am243x_12_00_00_26"
$Example = "$Sdk/examples/drivers/mcspi/mcspi_loopback/am243x-lp/r5fss0-0_nortos/ti-arm-clang"
$Gmake = "C:/ti/ccs2050/ccs/utils/bin/gmake.exe"
$CcsPath = "C:/ti/ccs2050/ccs"
$Python = "C:/CoRoot/.venv/Scripts/python.exe"
$Ccxml = "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/am2434_xds110_generated.ccxml"
$Out = "$Example/mcspi_loopback.release.out"
$MaxLoadAttempts = 4

$syscfgCandidates = @(
	Get-ChildItem -Path "C:/ti" -Directory -Filter "sysconfig_*" -ErrorAction SilentlyContinue
	Get-ChildItem -Path "C:/ti/ccs2050/ccs/utils" -Directory -Filter "sysconfig_*" -ErrorAction SilentlyContinue
)

$SyscfgDir = $syscfgCandidates |
	Sort-Object FullName -Descending |
	Select-Object -First 1

if (-not $SyscfgDir) {
	throw "No SysConfig install found under C:/ti (expected folder like sysconfig_1.xx.x)"
}

Set-Location $Example
& $Gmake -s all PYTHON=$Python CCS_PATH=$CcsPath SYSCFG_PATH=$($SyscfgDir.FullName)
if ($LASTEXITCODE -ne 0) {
	throw "Build failed"
}

Set-Location "C:/ti/ccs2050/ccs/ccs_base/scripting/examples/loadti"

function Invoke-LoadTi {
	param(
		[string]$CcxmlPath,
		[string]$OutPath
	)

	$loadOutput = & .\loadti.bat "-c=$CcxmlPath" "-cpu=MAIN_Cortex_R5_0_0" "-l" "-r" "-v" "$OutPath" 2>&1
	$loadOutput | ForEach-Object { Write-Host $_ }

	$failedByText = $false
	foreach ($line in $loadOutput) {
		if ($line -match "Error code #4011" -or
			$line -match "Load failed" -or
			$line -match "Trouble Writing Memory Block" -or
			$line -match "Verification failed") {
			$failedByText = $true
			break
		}
	}

	if ($LASTEXITCODE -ne 0 -or $failedByText) {
		return $false
	}

	return $true
}

$loaded = $false
for ($attempt = 1; $attempt -le $MaxLoadAttempts; $attempt++) {
	Write-Host "[loadti] Attempt $attempt of $MaxLoadAttempts"
	$loaded = Invoke-LoadTi -CcxmlPath $Ccxml -OutPath $Out

	if ($loaded) {
		break
	}

	if ($attempt -lt $MaxLoadAttempts) {
		Write-Warning "[loadti] Attempt $attempt failed. Retrying..."
	}
}

if (-not $loaded) {
	throw "Target load failed after $MaxLoadAttempts attempts"
}
