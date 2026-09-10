#!/usr/bin/env python3
"""
CCS GUI Automation - Build ati_ethercat_master
Uses pyautogui for mouse/keyboard control of CCS window.
"""
import sys
import time
import pyautogui
import pygetwindow as gw
from pathlib import Path

# Failsafe: move mouse to top-left corner to abort
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5  # Pause between actions

def log(msg):
    print(f"[CCS_GUI] {msg}")
    sys.stdout.flush()

def find_window(keywords):
    """Find window by keywords."""
    for keyword in keywords:
        windows = gw.getWindowsWithTitle(keyword)
        if windows:
            return windows[0]
    return None

def activate_and_focus(window, timeout=5):
    """Activate window and wait for focus."""
    try:
        window.activate()
        time.sleep(0.5)
        # Move mouse to center to ensure focus
        pyautogui.moveTo(window.left + window.width // 2, window.top + window.height // 2)
        time.sleep(0.5)
        return True
    except Exception as e:
        log(f"Warning: Could not activate window: {e}")
        return False

def wait_for_text_in_window(text, timeout=10):
    """Wait for text to appear in window (polling-based)."""
    # This is approximate - we can't read window contents directly with pyautogui
    # So we'll just wait and assume it appears
    log(f"Waiting for element containing '{text}'... ({timeout}s timeout)")
    time.sleep(timeout)

def type_path(path_str):
    """Type a file path carefully."""
    # Clear field first
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    
    # Type path character by character
    for char in path_str:
        if char == '\\':
            pyautogui.typewrite('/', interval=0.02)
        else:
            pyautogui.typewrite(char, interval=0.02)
    time.sleep(0.3)

def main():
    log("Starting CCS GUI Automation")
    
    # Find CCS window
    log("Looking for CCS window...")
    ccs_win = find_window(['Code Composer Studio', 'Eclipse', 'CCS'])
    
    if not ccs_win:
        log("ERROR: CCS window not found. Trying to launch CCS...")
        import subprocess
        ccs_exe = r"C:\ti\ccs2050\ccs\eclipse\ccs.exe"
        try:
            subprocess.Popen([ccs_exe])
            log("CCS launched, waiting 10 seconds for startup...")
            time.sleep(10)
            ccs_win = find_window(['Code Composer Studio', 'Eclipse', 'CCS'])
        except Exception as e:
            log(f"ERROR: Could not launch CCS: {e}")
            return False
    
    if not ccs_win:
        log("ERROR: Could not find or launch CCS window")
        return False
    
    log(f"Found CCS window: {ccs_win.title}")
    log(f"  Position: ({ccs_win.left}, {ccs_win.top})")
    log(f"  Size: {ccs_win.width}x{ccs_win.height}")
    
    # Activate window
    if not activate_and_focus(ccs_win):
        log("WARNING: Could not focus window, continuing anyway")
    
    time.sleep(1)
    
    # Step 1: Click File menu
    log("Step 1: Opening File menu")
    # File menu is typically at top-left
    file_menu_x = ccs_win.left + 50
    file_menu_y = ccs_win.top + 30
    pyautogui.click(file_menu_x, file_menu_y)
    time.sleep(0.8)
    
    # Step 2: Press 'O' to select "Open Projects from Filesystem"
    log("Step 2: Selecting 'Open Projects'")
    pyautogui.typewrite('o', interval=0.1)
    time.sleep(0.5)
    
    # Press Enter or click
    pyautogui.press('enter')
    time.sleep(1.5)
    
    # Step 3: Wait for dialog and enter project path
    log("Step 3: Entering project path in dialog")
    project_path = r"C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project\ati_ethercat_master"
    
    # Look for path field and click it
    time.sleep(1)
    
    # Try Ctrl+L to focus path bar
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)
    
    # Type path
    type_path(project_path)
    time.sleep(0.5)
    
    log(f"Typed path: {project_path}")
    
    # Step 4: Click Open or press Enter
    log("Step 4: Clicking Open button")
    pyautogui.press('enter')
    time.sleep(2)
    
    # Step 5: Wait for project to load in workspace
    log("Step 5: Waiting for project to load...")
    time.sleep(5)
    
    # Step 6: Right-click on project in Project Explorer to build
    log("Step 6: Right-clicking project to build")
    
    # Project explorer is typically on left side
    proj_explorer_x = ccs_win.left + 150
    proj_explorer_y = ccs_win.top + 200
    
    pyautogui.rightClick(proj_explorer_x, proj_explorer_y)
    time.sleep(1)
    
    # Step 7: Select "Build Project"
    log("Step 7: Selecting 'Build Project'")
    pyautogui.typewrite('b', interval=0.1)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(1)
    
    # Step 8: Wait for build to complete
    log("Step 8: Build started, waiting for completion (up to 3 minutes)...")
    build_timeout = 180
    for i in range(build_timeout):
        time.sleep(1)
        if (i + 1) % 30 == 0:
            log(f"  Build in progress... {i+1}s elapsed")
    
    log("Build wait time elapsed, checking for output binary...")
    
    # Step 9: Check if binary was created
    out_file = Path(project_path) / 'DebugSS0' / 'ati_ethercat_master.out'
    if out_file.exists():
        size = out_file.stat().st_size
        log(f"SUCCESS: Binary created: {out_file}")
        log(f"  File size: {size} bytes")
        return True
    else:
        log(f"FAILED: Binary not found at {out_file}")
        # Check if DebugSS0 directory exists
        debug_dir = Path(project_path) / 'DebugSS0'
        if debug_dir.exists():
            log(f"  DebugSS0 directory exists, contents:")
            for item in debug_dir.iterdir():
                log(f"    - {item.name}")
        else:
            log(f"  DebugSS0 directory does not exist")
        return False

if __name__ == '__main__':
    try:
        log("=== CCS GUI Automation Started ===")
        success = main()
        log("=== CCS GUI Automation Finished ===")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("Interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        log(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
