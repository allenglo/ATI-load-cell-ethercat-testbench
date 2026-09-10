# Build validation

Validation date: 2026-09-10

## ESP32-S3

The source project is a PlatformIO Arduino project targeting `esp32-s3-devkitc-1`. Run the build from `firmware/esp32s3`, not from the repository root:

```powershell
Push-Location firmware\esp32s3
python -m platformio run
Pop-Location
```

The current source project was staged without `.pio` so another machine will resolve dependencies from `platformio.ini`.

Latest local result: **SUCCESS**. PlatformIO used Espressif 32 7.0.1 and Arduino framework 3.20017.241212. The resulting firmware used 750,657 bytes of flash (22.5%) and 48,032 bytes of RAM (14.7%). The generated binary remains local because generated binaries are excluded by `.gitignore`.

## Controller and host tools

The AM243x project depends on the local TI Code Composer Studio/toolchain setup. The host tools require the Python packages imported by each script and access to the relevant serial/network adapters. Hardware-dependent validation remains pending on the target bench.
