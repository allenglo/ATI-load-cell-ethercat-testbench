# Dual SPI Addressable LED Driver for AM243x LaunchPad

## Overview

Modular, reusable SPI addressable LED driver supporting simultaneous operation on multiple SPI buses.

**Current Configuration:**
- **Chain 0**: SPI0_D0 (board pin 55) → 16x WS2812 LEDs (rainbow chase animation)
- **Chain 1**: SPI3_D0 (board pin 15) → 6x 645-587 LEDs (static cyan)
- **SPI Clock**: 10 MHz (100 ns/bit, 1.2 µs symbol period)
- **Update Rate**: 40 ms per frame (25 fps)

## Architecture

### Module Structure

```
┌─ addressable_led.h/c (CORE)
│  ├─ AddressableLedCtx: Encapsulates one LED chain
│  ├─ addressable_led_init(): Allocate & setup
│  ├─ addressable_led_send(): Build frame + transmit
│  ├─ addressable_led_set_color(): Set individual LED (GRB)
│  ├─ addressable_led_fill(): Set all LEDs
│  └─ addressable_led_hsv_to_grb(): Color space conversion
│
└─ dual_spi_leds.c (APP)
   ├─ Instantiate two AddressableLedCtx (SPI0, SPI3)
   ├─ Configure both SPI peripherals @ 10 MHz
   ├─ Main loop: update colors, send both chains
   └─ Animate with HSV rainbow on chain 0, static on chain 1
```

### Key Design Decisions

1. **Generic Module**: `addressable_led.h/c` knows nothing about specific SPI instances
   - Can be reused for any count of chains/pins
   - Protocol-agnostic (only implements WS2812-compatible symbols currently)

2. **Simultaneous Drive**: Both SPI0 and SPI3 update at same 40 ms interval
   - Each transfer ~300 µs per chain (negligible vs 40 ms frame time)
   - True parallel hardware operation (no crosstalk)

3. **GRB Color Space**: 
   - WS2812 uses Green-Red-Blue byte order
   - HSV-to-GRB helper for smooth rainbow animations

4. **SPI Configuration Critical**: bitRate and trMode MUST be set BEFORE `Drivers_open()`
   - Driver copies config to hardware at open time only
   - Default 50 MHz will cause protocol violations

## Files

| File | Purpose |
|------|---------|
| `addressable_led.h` | Module API (public interface) |
| `addressable_led.c` | Implementation (bit-stream encode, SPI transfer) |
| `dual_spi_leds.c` | Application (two LED chains, animation) |
| `example.syscfg` | Board config (SPI0, SPI3, UART) |
| `build_load_run_dual.ps1` | PowerShell build/load automation |
| `build_dual.sh` | Bash build wrapper (alternative) |

## Building & Running

### Prerequisites
- CCS 2050 with ti-arm-clang compiler
- MCU+ SDK AM243x v12.00.00.26
- gmake, Python 3.x

### Build Only
```powershell
.\build_load_run_dual.ps1 -BuildOnly
```

Output: `am243x-lp\r5fss0-0_nortos\ti-arm-clang\dual_spi_leds.release.out`

### Build & Load
```powershell
.\build_load_run_dual.ps1
```

### Load Only (binary already built)
```powershell
.\build_load_run_dual.ps1 -LoadOnly
```

## Usage Example: Adding a Third Chain

To add a third SPI LED chain:

1. **Update syscfg** (`example.syscfg`):
   ```javascript
   const mcspi3 = mcspi.addInstance();
   mcspi3.$name = "CONFIG_MCSPI2";
   mcspi3.SPI.$assign = "SPI2";
   mcspi3.SPI.D0.$assign = "SPI2_D0";
   // ... bitRate, CS config
   ```

2. **Update main** (`dual_spi_leds.c`):
   ```c
   AddressableLedCtx gLedChain2;  // New context
   
   addressable_led_init(&gLedChain2, gMcspiHandle[CONFIG_MCSPI2], 8U, SPI_CLOCK_HZ);
   // ... in main loop:
   addressable_led_send(&gLedChain2);
   ```

3. Rebuild and test.

## Protocol Details

### WS2812 SPI Encoding (10 MHz)

Each WS2812 data bit → 12 SPI bits:

| Data Bit | SPI Symbol | T_HIGH | T_LOW | Binary |
|----------|-----------|--------|-------|--------|
| **1** | 0xFF0 | 800 ns | 400 ns | 1111111100 |
| **0** | 0xE00 | 300 ns | 900 ns | 1110000000 |

**Frame Structure**:
- 24 bits per LED (GRB)
- 288 SPI bits per LED (24 × 12)
- 288 bytes per 16 LEDs + 320 reset bytes = 608 bytes total frame

**Reset Pulse**: 
- ≥320 bytes of zeros = 256 µs LOW (WS2812 needs >50 µs)

### 645-587 LEDs

Assumed to use same protocol as WS2812. If timing differs, update `WS_ONE` and `WS_ZERO` constants in `addressable_led.c`.

## Troubleshooting

### LEDs all white / not responding
- Verify SPI clock is 10 MHz (check UART output: `"SPI @ 10000000 Hz"`)
- Confirm pins 55 (SPI0_D0) and 15 (SPI3_D0) are connected
- Check 3.3V supply to LED chains

### JTAG load fails
- Power-cycle board (unplug USB, wait 2s, replug)
- Verify `am2434_xds110_generated.ccxml` exists in project root

### Build fails with undefined symbols
- Ensure syscfg was run (should auto-generate `ti_drivers_config.c`)
- Verify MCU_PLUS_SDK_PATH environment variable is set correctly

## Performance Notes

- **Frame transmission time**: ~600 µs per 16-LED chain (negligible)
- **Update interval**: 40 ms per animation step (can reduce for faster animation)
- **CPU overhead**: ~1% (SPI DMA handles transfer, main loop just polls status)

## Future Extensions

1. **PWM dimming**: Add global brightness control
2. **Different LED types**: Add SK6812 / APA102 / NeoPixel variants (different symbols/protocols)
3. **Interrupt-driven updates**: Replace polling with MCSPI transfer complete interrupt
4. **Patterns library**: Pre-canned animations (pulse, strobe, gradient, etc.)
5. **UART command interface**: Dynamic color/animation control from PC
