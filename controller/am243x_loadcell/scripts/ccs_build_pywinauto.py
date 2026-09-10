#!/usr/bin/env python3
"""
CCS Build Automation using pywinauto.
Controls CCS IDE to build ati_ethercat_master project.
"""
import sys
import time
from pathlib import Path
from pywinauto.application import Application
from pywinauto import keyboard

def log(msg):
    print(f"[PYWINAUTO] {msg}")
    sys.stdout.flush()

def main():
    log("Starting CCS Build Automation with pywinauto")
    
    # Connect to CCS window (should already be running)
    log("Connecting to Code Composer Studio...")
    try:
        app = Application(backend='uia').connect(title_re='.*Code Composer Studio.*')
        log("Connected to CCS")
    except Exception as e:
        log(f"ERROR: Could not connect to CCS: {e}")
        log("Make sure CCS is already running")
        return False
    
    ccs_win = app.window(title_re='.*Code Composer Studio.*')
    log(f"CCS window found: {ccs_win.window_text()}")
    
    # Step 1: Open File menu
    log("Step 1: Opening File menu...")
    time.sleep(0.5)
    keyboard.send_keys('%f')  # Alt+F for File
    time.sleep(1)
    
    # Step 2: Select "Open Projects from Filesystem"
    log("Step 2: Typing 'o' for Open Projects...")
    keyboard.send_keys('o')
    time.sleep(0.5)
    
    # Press Enter to activate
    keyboard.send_keys('{ENTER}')
    time.sleep(2)
    
    # Step 3: Dialog should appear, enter path
    log("Step 3: Entering project path...")
    project_path = r"C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project\ati_ethercat_master"
    
    # Wait for dialog and clear any existing text
    time.sleep(1)
    keyboard.send_keys('^a')  # Ctrl+A to select all
    time.sleep(0.2)
    
    # Type the path using clipboard (more reliable than typewrite)
    import subprocess
    subprocess.run(['powershell', '-Command', f'"{project_path}" | Set-Clipboard'], check=False)
    time.sleep(0.3)
    keyboard.send_keys('^v')  # Ctrl+V to paste
    time.sleep(0.5)
    
    log(f"Entered path: {project_path}")
    
    # Step 4: Click Open button (usually at bottom right of dialog)
    log("Step 4: Pressing Enter to open...")
    keyboard.send_keys('{ENTER}')
    time.sleep(3)
    
    # Step 5: Wait for project to load
    log("Step 5: Waiting for project to load...")
    time.sleep(5)
    
    # Step 6: Right-click in project explorer area
    log("Step 6: Finding project in explorer and right-clicking...")
    time.sleep(1)
    keyboard.send_keys('+{F10}')  # Shift+F10 for right-click context menu
    time.sleep(1)
    
    # Step 7: Select Build Project
    log("Step 7: Selecting 'Build Project'...")
    keyboard.send_keys('b')  # B for Build Project
    time.sleep(0.5)
    keyboard.send_keys('{ENTER}')
    time.sleep(2)
    
    # Step 8: Wait for build to complete (max 3 minutes)
    log("Step 8: Build started, waiting for completion (up to 3 minutes)...")
    build_timeout = 180
    for i in range(build_timeout):
        time.sleep(1)
        if (i + 1) % 30 == 0:
            log(f"  Build in progress... {i+1}s elapsed")
    
    log("Build wait complete, checking for output binary...")
    
    # Step 9: Check if binary exists
    out_file = Path(project_path) / 'DebugSS0' / 'ati_ethercat_master.out'
    if out_file.exists():
        size = out_file.stat().st_size
        log(f"SUCCESS: Binary created!")
        log(f"  Path: {out_file}")
        log(f"  Size: {size} bytes")
        return True
    else:
        log(f"FAILED: Binary not found at {out_file}")
        debug_dir = Path(project_path) / 'DebugSS0'
        if debug_dir.exists():
            log(f"  DebugSS0 exists, contents:")
            for item in debug_dir.iterdir():
                log(f"    - {item.name}")
        else:
            log(f"  DebugSS0 directory not found")
        return False

if __name__ == '__main__':
    try:
        log("=== pywinauto CCS Automation Started ===")
        success = main()
        log("=== pywinauto CCS Automation Finished ===")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
