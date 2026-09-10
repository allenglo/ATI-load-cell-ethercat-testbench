# EFlex load-cell test system

Combined handoff repository for the EFlex load-cell test setup. The system includes the AM243x/ATI EtherCAT controller, host-side Python tools and GUI, USB-to-Ethernet/PoE utilities, and the ESP32-S3 OLED/LED/LTC2990 subsystem.

## Repository layout

- `controller/am243x_loadcell/` - AM243x controller project and load-cell firmware.
- `host-tools/` - Python load-cell live GUI plus serial monitor, Ethernet, and PoE diagnostics.
- `firmware/esp32s3/` - ESP32-S3 PlatformIO firmware for OLED, dual LTC2990, accelerometer, APA102 outputs, touch, Wi-Fi/ThingSpeak, and external SPI flash work.
- `docs/` - handoff notes, hardware context, background, and validation records.

## Quick start

### ESP32-S3 firmware

From `firmware/esp32s3/`:

```powershell
python -m platformio run
python -m platformio run --target upload --upload-port COM33
python -m platformio device monitor --port COM33 --baud 115200
```

`COM30` is machine-specific. Use `python -m platformio device list` on another laptop.

### Python host tools

The load-cell GUI entrypoint is `host-tools/launchpad_loadcell_live_gui.py`. Install the dependencies required by that script and start it with:

```powershell
python .\host-tools\launchpad_loadcell_live_gui.py
```

To start directly on the ESP32 temperature serial view, set `LC_GUI_SERIAL_PORT=COM33` and `LC_GUI_SERIAL_TAB=1` first. The port is machine-specific.

The PoE and Ethernet checks are standalone PowerShell utilities in the same folder.

## Important scope note

This repository is a handoff snapshot assembled from the local working projects. Hardware wiring, controller setup, and known limitations are documented in `docs/`. Generated PlatformIO build trees and credentials are intentionally excluded.
