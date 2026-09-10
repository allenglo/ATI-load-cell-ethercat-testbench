#!/usr/bin/env python3
"""
Build ati_ethercat_master using TI SDK gmake system.
Sets up environment and invokes build without GUI.
"""
import subprocess
import os
import sys
from pathlib import Path
import json

def run_cmd(cmd, cwd=None, env=None):
    """Run command and return (success, stdout, stderr)."""
    print(f"[BUILD] Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            env=env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("[BUILD] ati_ethercat_master Build Script")
    
    # Paths
    project_root = Path(r"C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project\ati_ethercat_master")
    sdk_root = Path(r"C:\ti\mcu_plus_sdk_am243x_12_00_00_26")
    ccs_root = Path(r"C:\ti\ccs2050\ccs")
    
    # Check paths exist
    if not project_root.exists():
        print(f"[BUILD] ERROR: Project not found: {project_root}")
        return False
    
    if not sdk_root.exists():
        print(f"[BUILD] ERROR: SDK not found: {sdk_root}")
        return False
    
    print(f"[BUILD] Project: {project_root}")
    print(f"[BUILD] SDK: {sdk_root}")
    
    # Setup environment
    build_env = os.environ.copy()
    build_env['MCU_PLUS_SDK_PATH'] = str(sdk_root)
    build_env['CCS_INSTALL_DIR'] = str(ccs_root)
    build_env['CCS_IDE_MODE'] = '1'
    build_env['CG_TOOL_ROOT'] = str(ccs_root / 'ccs_base' / 'ti-cgt-armllvm_4.0.4.LTS')
    
    # Try to find gmake
    gmake_candidates = [
        str(ccs_root / 'utils' / 'bin' / 'gmake.exe'),
        str(ccs_root / 'ccs_base' / 'common' / 'bin' / 'gmake.exe'),
        'gmake.exe',
        'gmake',
    ]
    
    gmake_exe = None
    for candidate in gmake_candidates:
        if os.path.exists(candidate) or subprocess.run(f'where {candidate}', 
                                                       shell=True, 
                                                       capture_output=True).returncode == 0:
            gmake_exe = candidate
            break
    
    if not gmake_exe:
        print("[BUILD] ERROR: gmake not found")
        return False
    
    print(f"[BUILD] Using gmake: {gmake_exe}")
    
    # Build DebugSS0 configuration
    config = 'DebugSS0'
    print(f"[BUILD] Building configuration: {config}")
    
    build_cmd = f'{gmake_exe} -C "{project_root}" all PROFILE={config}'
    
    success, stdout, stderr = run_cmd(build_cmd, env=build_env)
    
    print("[BUILD] --- BUILD OUTPUT ---")
    if stdout:
        print(stdout[-2000:] if len(stdout) > 2000 else stdout)  # Last 2000 chars
    if stderr:
        print("[BUILD] STDERR:", stderr[-1000:] if len(stderr) > 1000 else stderr)
    
    # Check if binary exists
    out_file = project_root / config / 'ati_ethercat_master.out'
    if out_file.exists():
        print(f"[BUILD] SUCCESS: Binary created: {out_file}")
        print(f"[BUILD] Size: {out_file.stat().st_size} bytes")
        return True
    else:
        print(f"[BUILD] FAILED: Binary not found at {out_file}")
        print(f"[BUILD] Build returned: {success}")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[BUILD] EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
