/*
 * Addressable LED Driver — SPI-based (WS2812, 645-587, etc.)
 *
 * Generic module supporting multiple SPI instances driving single-wire
 * addressable LED chains via SPI symbol encoding at 10 MHz.
 *
 * Protocol: GRB color space, 24-bit per LED, SPI symbol encoding.
 */

#ifndef ADDRESSABLE_LED_H
#define ADDRESSABLE_LED_H

#include <stdint.h>
#include <drivers/mcspi.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---- Context & Configuration -------------------------------------------- */

typedef struct {
    MCSPI_Handle     mcspi_handle;
    uint32_t         led_count;
    uint32_t         spi_hz;         /* typically 10 MHz */
    uint8_t         *frame;          /* SPI bit-stream buffer (heap or static) */
    uint32_t         frame_bytes;    /* total frame size including reset */
    uint8_t         *grb;            /* GRB color array: [led_count][3] */
    MCSPI_Transaction txn;           /* reusable transaction */
    uint8_t          owns_storage;   /* 1 if allocated by module */
} AddressableLedCtx;

/* ---- Initialization ------------------------------------------------------ */

/**
 * Initialize addressable LED context.
 *
 * @param ctx           Caller-allocated context
 * @param mcspi_handle  Open MCSPI driver handle
 * @param led_count     Number of LEDs
 * @param spi_hz        SPI clock (e.g., 10000000 for 10 MHz)
 * @return              0 on success, -1 on allocation failure
 */
int32_t addressable_led_init(AddressableLedCtx *ctx, MCSPI_Handle mcspi_handle,
                             uint32_t led_count, uint32_t spi_hz);

/**
 * Initialize with caller-provided storage.
 *
 * @param frame_storage  Buffer used for encoded frame bytes
 * @param frame_bytes    Size of frame_storage in bytes
 * @param grb_storage    Buffer used for [led_count][3] GRB data
 */
int32_t addressable_led_init_with_storage(AddressableLedCtx *ctx,
                                          MCSPI_Handle mcspi_handle,
                                          uint32_t led_count,
                                          uint32_t spi_hz,
                                          uint8_t *frame_storage,
                                          uint32_t frame_bytes,
                                          uint8_t *grb_storage);

/**
 * Deinitialize & free resources.
 */
void addressable_led_deinit(AddressableLedCtx *ctx);

/* ---- Color Control ------------------------------------------------------- */

/**
 * Set GRB color for a single LED.
 *
 * @param ctx    Context
 * @param idx    LED index (0 to led_count-1)
 * @param g      Green (0-255)
 * @param r      Red (0-255)
 * @param b      Blue (0-255)
 */
void addressable_led_set_color(AddressableLedCtx *ctx, uint32_t idx,
                               uint8_t g, uint8_t r, uint8_t b);

/**
 * Fill all LEDs with same GRB color.
 */
void addressable_led_fill(AddressableLedCtx *ctx, uint8_t g, uint8_t r, uint8_t b);

/* ---- HSV Helper ---------------------------------------------------------- */

/**
 * Convert HSV (0-255 range) to GRB.
 *
 * @param h      Hue (0-255)
 * @param s      Saturation (0-255)
 * @param v      Value/brightness (0-255)
 * @param g, r, b  Pointers to store GRB output
 */
void addressable_led_hsv_to_grb(uint8_t h, uint8_t s, uint8_t v,
                                uint8_t *g, uint8_t *r, uint8_t *b);

/* ---- Transmission ------------------------------------------------------- */

/**
 * Build SPI frame from current GRB colors and transmit.
 *
 * @param ctx    Context
 * @return       0 on success, -1 on transfer failure
 */
int32_t addressable_led_send(AddressableLedCtx *ctx);

#ifdef __cplusplus
}
#endif

#endif /* ADDRESSABLE_LED_H */
