#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Safe flash procedure with boot mode switching
.DESCRIPTION
    Handles switching boot modes, waiting for user confirmation, and reflashing
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LaunchPad Safe Flash Procedure"
Write-Host "========================================"
Write-Host ""

Write-Host "STEP 1: Switch Boot Mode to UART" -ForegroundColor Yellow
Write-Host "================================="
Write-Host ""
Write-Host "Current: 0100 0100 (OSPI - boots from flash)"
Write-Host "Needed:  1110 0000 (UART - waits for flash script)"
Write-Host ""
Write-Host "ACTION: Set SW4 to: 1110 0000" -ForegroundColor Red
Write-Host "        (top row: 1-1-1-0, bottom row: 0-0-0-0)"
Write-Host ""
Write-Host "Press ENTER when done..."
Read-Host | Out-Null

Write-Host ""
Write-Host "STEP 2: Power Cycle Board" -ForegroundColor Yellow
Write-Host "========================="
Write-Host ""
Write-Host "ACTION: Power OFF the board (unplug PoE or power)"
Write-Host "        Wait 5 seconds..."
Start-Sleep -Seconds 2
Write-Host "        Power ON the board"
Write-Host ""
Write-Host "Press ENTER when powered back on..."
Read-Host | Out-Null

Write-Host ""
Write-Host "STEP 3: Verify UART Boot Mode (should see repeating 'C')" -ForegroundColor Yellow
Write-Host "========================================================"
$port = New-Object System.IO.Ports.SerialPort COM10,115200,None,8,one
$port.ReadTimeout = 1000
try {
    $port.Open()
    Write-Host "Checking for boot mode indicators..."
    Start-Sleep -Milliseconds 500
    $data = $port.ReadExisting()
    if($data -like "*C*" -or $data -like "*c*") {
        Write-Host "✓ Good! Seeing 'C' characters (UART boot ready)" -ForegroundColor Green
    } else {
        Write-Host "⚠ Not seeing boot indicators. Data received: $([char[]]$data | ForEach-Object {[int]$_})" -ForegroundColor Yellow
    }
} catch { Write-Host "ERROR reading COM10: $_" } finally { if($port.IsOpen) { $port.Close() } }

Write-Host ""
Write-Host "STEP 4: Run Flash Script" -ForegroundColor Yellow
Write-Host "======================="
Write-Host ""
Write-Host "Ready to flash. Running: build_load_run_dual.ps1 -FlashOnly"
Write-Host ""
Write-Host "Press ENTER to proceed with flashing..."
Read-Host | Out-Null

Set-Location "C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project"
.\build_load_run_dual.ps1 -FlashOnly -ComPort COM10

Write-Host ""
Write-Host "STEP 5: Switch Back to OSPI Boot Mode" -ForegroundColor Yellow
Write-Host "======================================"
Write-Host ""
Write-Host "ACTION: Set SW4 to: 0100 0100" -ForegroundColor Red
Write-Host "        (top row: 0-1-0-0, bottom row: 0-1-0-0)"
Write-Host ""
Write-Host "Press ENTER when done..."
Read-Host | Out-Null

Write-Host ""
Write-Host "STEP 6: Power Cycle and Verify App" -ForegroundColor Yellow
Write-Host "=================================="
Write-Host ""
Write-Host "ACTION: Power OFF the board"
Write-Host "        Wait 5 seconds..."
Start-Sleep -Seconds 2
Write-Host "        Power ON the board"
Write-Host ""
Write-Host "Press ENTER..."
Read-Host | Out-Null

Write-Host ""
Write-Host "Checking for app startup messages..." -ForegroundColor Cyan
$port = New-Object System.IO.Ports.SerialPort COM10,115200,None,8,one
$port.ReadTimeout = 1000
try {
    $port.Open()
    Start-Sleep -Milliseconds 1000
    $output = $port.ReadExisting()
    Write-Host "UART Output:" -ForegroundColor Green
    Write-Host $output
    if($output -like "*Dual*" -or $output -like "*LED*" -or $output -like "*?*") {
        Write-Host ""
        Write-Host "✓ APP IS RUNNING!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠ App may not have started. Check bootloader output above." -ForegroundColor Yellow
    }
} catch { Write-Host "ERROR: $_" } finally { if($port.IsOpen) { $port.Close() } }

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Flash Complete!"
Write-Host "========================================"
