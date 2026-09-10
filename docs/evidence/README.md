# Local GUI evidence

The load-cell screenshot in this folder was captured on 2026-09-10 after starting the actual live application:

```powershell
Push-Location controller\am243x_loadcell\scripts
python .\launchpad_loadcell_live_gui.py
Pop-Location
```

The GUI launched and remained responsive. The screenshot shows the connected USB-to-Ethernet adapter, decoded load-cell force/torque samples, and the live graph panels. The separate `serial_monitor_gui_local.png` image is retained as evidence for the generic serial monitor tool.

The file `esp32_com30_serial_monitor_gui.png` shows the combined GUI auto-connected to the ESP32-S3 on `COM30` at 115200 baud. The ESP32 is streaming diagnostics. At capture time both LTC2990 devices reported `MISS`, so the next hardware check is the LTC bus wiring and addresses (`0x4C` and `0x4F` on GPIO17/GPIO18). The LED output was tested separately with `RING WHITE` followed by `RING AUTO`; the firmware acknowledged both commands and was left in automatic animation mode.

The complete temperature-probe bench is on `COM33`, not `COM30`. It reports both LTC2990 devices as `GOOD` at addresses `0x4C` and `0x4F`, with approximately 23-24 C internal temperatures and an MPU6050 detected. The PlatformIO and GUI examples use COM33 for this bench.
