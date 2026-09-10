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
	- Startup defaults to the fastest software-clock mode. The current `digitalWrite()` implementation does not guarantee a measured 11 MHz clock; a hardware SPI implementation would be required for that specification.

- LED animation and fault indication:
	- Automatic mode continuously moves through layered rainbows, rainbow pulses, counter-rotating rainbow bands, comets, theater chase, sparkles, and additional rainbow motion.
	- If either LTC2990 has invalid or missing data, the normal moving animation continues and a moving red/white warning marker is overlaid on both LED arrays.

## Build

```bash
python -m platformio run
```

## Upload

```bash
python -m platformio run --target upload
python -m platformio device monitor -b 115200
```
