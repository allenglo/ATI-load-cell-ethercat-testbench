# Handoff

## System boundary

The load-cell system is larger than the ESP32-S3 board:

1. The AM243x/ATI EtherCAT controller acquires load-cell data.
2. USB-to-Ethernet and PoE hardware provides the network and power path.
3. Host-side Python tools provide serial monitoring and operator control.
4. The ESP32-S3 provides the OLED, LTC2990 temperature/voltage monitoring, LED outputs, touch input, and related diagnostics.

## First checks on a new laptop

1. Clone the repository and inspect `docs/HARDWARE.md`.
2. Install PlatformIO and build `firmware/esp32s3`.
3. Identify the actual USB serial port; do not assume `COM30`.
4. Run the Ethernet/PoE diagnostic scripts before connecting the load-cell controller.
5. Install the Python GUI dependencies and run the GUI only after confirming the serial device.

## Known limitations

- The Python GUI was recovered as the existing serial-monitor tool; its exact device-specific workflow still needs a live hardware check.
- Confluence URLs were not present in the local source tree, so private links are not fabricated here.
- The ESP32 firmware contains network configuration placeholders and must be reviewed for secrets before deployment.
- The original controller folder contained a large Git-LFS vendor archive under `external/INR_DEV-main`; it is excluded from this handoff because the local LFS objects were unavailable. The active controller sources and tools are included.
- Generated GUI packages, executables, and large serial-log CSV files are excluded; rebuild the GUI locally from `host-tools/serial_monitor_gui.py` or the controller scripts.
- Generated webcam-validation reports and captured images are excluded from Git; the source validation scripts remain available in the controller tree.
- The mirrored external vendor tree is excluded because it contains credentials and third-party artifacts. Retrieve it separately through the approved internal source process when needed.
