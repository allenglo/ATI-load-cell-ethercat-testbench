#!/usr/bin/env python3
"""
Automate CCS GUI to build ati_ethercat_master project.
Uses pyautogui to control the CCS window.
"""
import sys
import time
import pyautogui
import pygetwindow as gw
from pathlib import Path

# Enable failsafe: move mouse to corner to abort
pyautogui.FAILSAFE = True

def find_ccs_window():
    """Find and return the CCS window."""
    windows = gw.getWindowsWithTitle('Code Composer Studio')
    if not windows:
        windows = gw.getWindowsWithTitle('CCS')
    if not windows:
        windows = gw.getWindowsWithTitle('Eclipse')
    
    if windows:
        return windows[0]
    return None

def wait_for_window(title_substr, timeout=30):
    """Wait for a window with title containing substring."""
    for _ in range(timeout * 2):
        windows = gw.getWindowsWithTitle(title_substr)
        if windows:
            return windows[0]
        time.sleep(0.5)
    return None

def click_at(x, y, delay=0.3):
    """Click at position with delay."""
    pyautogui.click(x, y)
    time.sleep(delay)

def type_text(text, interval=0.05):
    """Type text character by character."""
    pyautogui.typewrite(text, interval=interval)

def main():
    print("[CCS_AUTO] Starting CCS automation...")
    
    # Find CCS window
    print("[CCS_AUTO] Looking for CCS window...")
    ccs_win = find_ccs_window()
    if not ccs_win:
        print("[CCS_AUTO] ERROR: CCS window not found. Is CCS running?")
        return False
    
    print(f"[CCS_AUTO] Found CCS window: {ccs_win.title}")
    
    # Activate CCS window
    try:
        ccs_win.activate()
        time.sleep(1)
    except Exception as e:
        print(f"[CCS_AUTO] Warning: could not activate window: {e}")
    
    # Click File menu
    print("[CCS_AUTO] Clicking File menu...")
    # Approximate position of File menu (adjust if needed)
    pyautogui.click(100, 50)
    time.sleep(0.5)
    
    # Look for "Open Projects from Filesystem" option
    print("[CCS_AUTO] Waiting for menu to appear...")
    time.sleep(1)
    
    # Type to search for menu item
    pyautogui.typewrite('o', interval=0.1)  # "Open Projects from Filesystem" starts with O
    time.sleep(0.5)
    
    # Press Enter to select
    pyautogui.press('enter')
    time.sleep(1)
    
    # Wait for dialog and fill in path
    print("[CCS_AUTO] Entering project path...")
    project_path = r"C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project\ati_ethercat_master"
    
    # Click in path field and clear it
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    
    # Paste path (using clipboard)
    import subprocess
    # Copy to clipboard
    subprocess.run(['powershell', '-Command', f'"{project_path}" | Set-Clipboard'], check=False)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # Click Open button
    print("[CCS_AUTO] Clicking Open...")
    pyautogui.press('enter')  # or find and click Open button
    time.sleep(3)
    
    # Wait for project to load
    print("[CCS_AUTO] Waiting for project to load...")
    time.sleep(5)
    
    # Right-click on project in explorer to get context menu
    print("[CCS_AUTO] Right-clicking project to build...")
    pyautogui.rightClick(300, 300)
    time.sleep(1)
    
    # Type 'B' for Build or look for Build Project option
    pyautogui.typewrite('b', interval=0.1)
    time.sleep(0.5)
    
    # Press Enter
    pyautogui.press('enter')
    time.sleep(1)
    
    # Wait for build to complete
    print("[CCS_AUTO] Build started. Waiting for completion...")
    max_wait = 120  # 2 minutes
    for i in range(max_wait):
        # Look for "Build Finished" in console or title
        # For now, just wait
        time.sleep(1)
        if (i + 1) % 10 == 0:
            print(f"[CCS_AUTO] Build in progress... ({i+1}s)")
    
    print("[CCS_AUTO] Build should be complete. Checking for output...")
    
    # Check if binary exists
    out_file = Path(r"C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project\ati_ethercat_master\DebugSS0\ati_ethercat_master.out")
    if out_file.exists():
        print(f"[CCS_AUTO] SUCCESS: Binary found at {out_file}")
        return True
    else:
        print(f"[CCS_AUTO] WARNING: Binary not found at {out_file}")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CCS_AUTO] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[CCS_AUTO] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
