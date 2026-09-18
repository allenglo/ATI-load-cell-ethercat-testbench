# Build validation

Validation date: 2026-09-18

## ESP32-S3

The source project is a PlatformIO Arduino project targeting `esp32-s3-devkitc-1`. Run the build from `firmware/esp32s3`, not from the repository root:

```powershell
Push-Location firmware\esp32s3
python -m platformio run
Pop-Location
```

The current source project was staged without `.pio` so another machine will resolve dependencies from `platformio.ini`.

Latest local result: **SUCCESS**. PlatformIO used Espressif 32 7.0.1 and Arduino framework 3.20017.241212. The dual-output thermal firmware used 779,545 bytes of flash (23.3%) and 48,056 bytes of RAM (14.7%). The generated binary remains local because generated binaries are excluded by `.gitignore`.

The COM33 bench was tested with the following command sequence:

```text
THERMAL HEAT
THERMAL COOL
THERMAL IDLE
THERMAL AUTO 35.0 0.5 AVG
THERMAL AUTO 10.0 0.5 AVG
THERMAL IDLE
```

Observed results:

- Manual and automatic HEAT reached `heat=1 cool=0`.
- Direction reversal first entered IDLE, waited 500 ms, then COOL reached `heat=0 cool=1`.
- No telemetry line reported both outputs active.
- Both LTC2990 devices remained `GOOD` during the test.
- Final state was `mode=IDLE output=IDLE heat=0 cool=0`.
- The updated GUI was launched on COM33, and its Heat, Cool, Idle, and Auto controls were exercised before returning to IDLE.

After this test, output initialization was moved to the first instructions in `setup()` so both pins are driven LOW as early as possible. That final source rebuild passed. A final reflash could not be completed because the CH343/COM33 USB device was physically absent from Windows at that point; reconnect the bench and rerun the upload command above.

## Controller and host tools

The AM243x project depends on the local TI Code Composer Studio/toolchain setup. The host tools require the Python packages imported by each script and access to the relevant serial/network adapters. The Python GUI passed `py_compile` and was exercised against the COM33 bench.
