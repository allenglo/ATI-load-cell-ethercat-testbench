# ESP32-S3 OLED + Dual LTC2990 Monitor

This project uses two I2C buses:
- OLED on dedicated bus pins GPIO8/GPIO9 (as requested)
- Two LTC2990 devices on a separate bus for clean sensor traffic

Display flow:
- Boot screen 1 (fixed timing): I2C scan for OLED bus (8/9)
- Boot screen 2 (fixed timing): I2C scan for sensor bus (17/18)
- Runtime rotating pages:
	- Summary page: temp + VCC for `0x4C` and `0x4F`
	- Detail page for `0x4C`: V1..V4, temp, VCC
	- Detail page for `0x4F`: V1..V4, temp, VCC
	- Accelerometer page: X/Y/Z acceleration values (LIS3DH or MPU6050 auto-detect)

## Pin map

- OLED bus (Wire):
	- SDA: GPIO8
	- SCL: GPIO9
- LTC bus (Wire1):
	- SDA: GPIO17
	- SCL: GPIO18
- APA102 LED ring:
	- DATA: GPIO11
	- CLOCK: GPIO12
- Second APA102 LED array:
	- DATA: GPIO5
	- CLOCK: GPIO6
- LED clock select button:
	- GPIO7 to GND
	- Internal pull-up enabled; button is active low
- Thermal control outputs:
	- HEAT request: GPIO13, active high
	- COOL request: GPIO14, active high
	- Both low: idle

Why 17/18 for LTC bus:
- Good general-purpose GPIOs on ESP32-S3
- Not strapping pins
- Stable for 400kHz I2C in typical dev board setups

## LTC2990 address setup

- Chip A (A1=GND, A0=GND): `0x4C`
- Chip B (A1=VCC, A0=VCC): `0x4F`

## Wiring notes

- OLED:
	- VCC -> 3.3V
	- GND -> GND
	- SDA -> GPIO8
	- SCL -> GPIO9

- LTC2990 pair (both chips on same LTC bus):
	- SDA -> GPIO17
	- SCL -> GPIO18
	- VCC -> 3.3V
	- GND -> GND
	- Address pins:
		- Chip A: A1 -> GND, A0 -> GND
		- Chip B: A1 -> 3.3V, A0 -> 3.3V

- APA102 LED ring and second LED array:
	- Connect DATA and CLOCK to the GPIOs listed above.
	- Connect LED ground and ESP32-S3 ground together.
	- Use a suitable 5V supply for the LEDs; do not power a large array from the ESP32-S3 3.3V pin.
	- Use 3.3V-to-5V logic level shifting for reliable DATA/CLOCK signals when the LEDs are powered at 5V.
	- The second array receives the same 50-pixel animation frame as the existing ring.

- Clock select button:
	- Press the GPIO7 button to cycle through approximately 1 kHz, 5 kHz, 25 kHz, 100 kHz, 250 kHz, and fastest-software-clock modes.
	- The 1 kHz mode is the slowest and most timing-tolerant setting.
	- The selected mode is reported on the serial monitor as `[LED CLOCK]`.
	- Startup defaults to the conservative 25 kHz software-clock mode so LED updates do not starve temperature control. The current `digitalWrite()` implementation does not guarantee a measured 11 MHz clock; a hardware SPI implementation would be required for that specification.

- LED animation and fault indication:
	- Automatic mode continuously moves through layered rainbows, rainbow pulses, counter-rotating rainbow bands, comets, theater chase, sparkles, and additional rainbow motion.
	- If either LTC2990 has invalid or missing data, the normal moving animation continues and a moving red/white warning marker is overlaid on both LED arrays.

## Thermal control

GPIO13 and GPIO14 are active-high logic requests for external power-control hardware. They must not drive a Peltier directly. Firmware initializes both outputs low and enforces a 500 ms all-off interval before changing between heating and cooling.

Use external pull-down resistors on both driver inputs so heating and cooling remain disabled while the ESP32 is reset, unpowered, or still in its boot ROM.

Serial commands at 115200 baud:

```text
THERMAL IDLE
THERMAL HEAT
THERMAL COOL
THERMAL AUTO <target_C> <idle_window_C> <4C|4F|AVG>
```

Accepted ranges are -100 C through 200 C for the target and 0 C through 20 C for the idle window.

Example:

```text
THERMAL AUTO 25.0 0.5 AVG
```

This heats below 24.5 C, idles from 24.5 C through 25.5 C, and cools above 25.5 C. Automatic control falls back to IDLE if the selected sensor data is invalid. Legacy `HEATER ON` and `HEATER OFF` commands remain supported as manual HEAT and IDLE.

The OLED status page shows mode, sensor source, active output, HEAT/COOL bits, current control temperature, target, and idle window.

## Build

```bash
python -m platformio run
```

## Upload

```bash
python -m platformio run --target upload
python -m platformio device monitor -b 115200
```
