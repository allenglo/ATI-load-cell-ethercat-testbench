#!/bin/bash
# Direct build for dual SPI LEDs project
# Invokes gmake with correct source files

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_DIR/am243x-lp/r5fss0-0_nortos/ti-arm-clang"

export MCU_PLUS_SDK_PATH="${MCU_PLUS_SDK_PATH:-/c/ti/mcu_plus_sdk_am243x_12_00_00_26}"

cd "$BUILD_DIR"

# Build with dual SPI sources
make -j4 PROFILE=release \
    OUTNAME=dual_spi_leds.release.out \
    FILES_common="$PROJECT_DIR/dual_spi_leds.c $PROJECT_DIR/addressable_led.c main.c ti_drivers_config.c ti_drivers_open_close.c ti_board_config.c ti_board_open_close.c ti_dpl_config.c ti_pinmux_config.c ti_power_clock_config.c" \
    INCLUDES_common="-I${CG_TOOL_ROOT}/include/c -I${MCU_PLUS_SDK_PATH}/source -Igenerated -I$PROJECT_DIR"

echo "Build complete: am243x-lp/r5fss0-0_nortos/ti-arm-clang/dual_spi_leds.release.out"
