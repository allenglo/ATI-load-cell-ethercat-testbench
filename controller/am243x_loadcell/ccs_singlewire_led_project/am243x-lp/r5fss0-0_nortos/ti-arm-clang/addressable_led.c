/*
 * Addressable LED Driver Implementation
 */

#include "addressable_led.h"
#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/SystemP.h>
#include <string.h>
#include <stdlib.h>

/* ---- SPI Symbol Encoding (10 MHz, 100 ns/bit, 1.2 µs/symbol) ----------- */

#define WS_SYM_BITS             (12U)
#define WS_ONE                  (0xFF0U)     /* T1H = 800 ns, T1L = 400 ns */
#define WS_ZERO                 (0xE00U)     /* T0H = 300 ns, T0L = 900 ns */
#define WS_RESET_BYTES          (320U)       /* ~256 µs reset pulse */

/* ---- Helper: Write bit to flat buffer ----------------------------------- */

static void ws_set_bit(uint8_t *buf, uint32_t pos, uint8_t val)
{
    uint32_t byte_idx = pos >> 3U;
    uint32_t bit_idx  = 7U - (pos & 7U);
    if (val)
        buf[byte_idx] |=  (uint8_t)(1U << bit_idx);
    else
        buf[byte_idx] &= (uint8_t)~(1U << bit_idx);
}

/* ---- Helper: Emit 12-bit SPI symbol ------------------------------------ */

static void ws_emit(uint8_t *buf, uint32_t *pos, uint16_t sym)
{
    uint32_t k;
    for (k = 0U; k < WS_SYM_BITS; k++)
    {
        ws_set_bit(buf, *pos, (uint8_t)((sym >> (WS_SYM_BITS - 1U - k)) & 1U));
        (*pos)++;
    }
}

/* ---- Initialization ------------------------------------------------------ */

static uint32_t addressable_led_calc_frame_bytes(uint32_t led_count)
{
    uint32_t payload_bits;
    uint32_t payload_bytes;

    payload_bits  = led_count * 24U * WS_SYM_BITS;
    payload_bytes = (payload_bits + 7U) / 8U;

    return payload_bytes + WS_RESET_BYTES;
}

int32_t addressable_led_init_with_storage(AddressableLedCtx *ctx,
                                          MCSPI_Handle mcspi_handle,
                                          uint32_t led_count,
                                          uint32_t spi_hz,
                                          uint8_t *frame_storage,
                                          uint32_t frame_bytes,
                                          uint8_t *grb_storage)
{
    uint32_t required_frame_bytes;

    if (!ctx || !frame_storage || !grb_storage || led_count == 0U)
        return -1;

    required_frame_bytes = addressable_led_calc_frame_bytes(led_count);
    if (frame_bytes < required_frame_bytes)
        return -1;

    ctx->mcspi_handle = mcspi_handle;
    ctx->led_count    = led_count;
    ctx->spi_hz       = spi_hz;
    ctx->frame        = frame_storage;
    ctx->frame_bytes  = required_frame_bytes;
    ctx->grb          = grb_storage;
    ctx->owns_storage = 0U;

    MCSPI_Transaction_init(&ctx->txn);
    ctx->txn.channel   = 0U;
    ctx->txn.dataSize  = 8U;
    ctx->txn.csDisable = TRUE;

    memset(ctx->grb, 0, led_count * 3U);
    memset(ctx->frame, 0, ctx->frame_bytes);

    return 0;
}

int32_t addressable_led_init(AddressableLedCtx *ctx, MCSPI_Handle mcspi_handle,
                             uint32_t led_count, uint32_t spi_hz)
{
    uint32_t frame_bytes;
    uint8_t *frame_storage;
    uint8_t *grb_storage;

    if (!ctx || led_count == 0U)
        return -1;

    frame_bytes = addressable_led_calc_frame_bytes(led_count);
    frame_storage = (uint8_t *)malloc(frame_bytes);
    grb_storage   = (uint8_t *)malloc(led_count * 3U);

    if (!frame_storage || !grb_storage)
    {
        free(frame_storage);
        free(grb_storage);
        return -1;
    }

    if (addressable_led_init_with_storage(ctx, mcspi_handle, led_count, spi_hz,
                                          frame_storage, frame_bytes, grb_storage) != 0)
    {
        free(frame_storage);
        free(grb_storage);
        return -1;
    }

    ctx->owns_storage = 1U;

    return 0;
}

void addressable_led_deinit(AddressableLedCtx *ctx)
{
    if (!ctx)
        return;
    if (ctx->owns_storage && ctx->grb)
        free(ctx->grb);
    if (ctx->owns_storage && ctx->frame)
        free(ctx->frame);
    ctx->grb   = NULL;
    ctx->frame = NULL;
    ctx->owns_storage = 0U;
}

/* ---- Color Control ------------------------------------------------------- */

void addressable_led_set_color(AddressableLedCtx *ctx, uint32_t idx,
                               uint8_t g, uint8_t r, uint8_t b)
{
    if (!ctx || !ctx->grb || idx >= ctx->led_count)
        return;
    ctx->grb[idx * 3U + 0U] = g;
    ctx->grb[idx * 3U + 1U] = r;
    ctx->grb[idx * 3U + 2U] = b;
}

void addressable_led_fill(AddressableLedCtx *ctx, uint8_t g, uint8_t r, uint8_t b)
{
    uint32_t i;
    if (!ctx)
        return;
    for (i = 0U; i < ctx->led_count; i++)
        addressable_led_set_color(ctx, i, g, r, b);
}

/* ---- HSV Helper ---------------------------------------------------------- */

void addressable_led_hsv_to_grb(uint8_t h, uint8_t s, uint8_t v,
                                uint8_t *g, uint8_t *r, uint8_t *b)
{
    uint8_t region, rem, p, q, t;
    if (s == 0U) { *r = *g = *b = v; return; }
    region = (uint8_t)(h / 43U);
    rem    = (uint8_t)((h - (region * 43U)) * 6U);
    p = (uint8_t)((v * (255U - s)) >> 8U);
    q = (uint8_t)((v * (255U - ((s * rem) >> 8U))) >> 8U);
    t = (uint8_t)((v * (255U - ((s * (255U - rem)) >> 8U))) >> 8U);
    switch (region)
    {
        case 0:  *r = v; *g = t; *b = p; break;
        case 1:  *r = q; *g = v; *b = p; break;
        case 2:  *r = p; *g = v; *b = t; break;
        case 3:  *r = p; *g = q; *b = v; break;
        case 4:  *r = t; *g = p; *b = v; break;
        default: *r = v; *g = p; *b = q; break;
    }
}

/* ---- Frame Building & Transmission -------------------------------------- */

int32_t addressable_led_send(AddressableLedCtx *ctx)
{
    uint32_t led, ch, bit, pos = 0U;
    int32_t st;

    if (!ctx || !ctx->frame || !ctx->grb || !ctx->mcspi_handle)
        return -1;

    /* Build frame: convert GRB to SPI bit-stream */
    memset(ctx->frame, 0, ctx->frame_bytes);

    for (led = 0U; led < ctx->led_count; led++)
    {
        for (ch = 0U; ch < 3U; ch++)
        {
            uint8_t v = ctx->grb[led * 3U + ch];
            for (bit = 0U; bit < 8U; bit++)
            {
                uint8_t db = (uint8_t)((v >> (7U - bit)) & 1U);
                ws_emit(ctx->frame, &pos, db ? WS_ONE : WS_ZERO);
            }
        }
    }
    /* Remaining bytes stay 0 → reset pulse */

    /* Transmit */
    ctx->txn.count = ctx->frame_bytes;
    ctx->txn.txBuf = (void *)ctx->frame;
    ctx->txn.rxBuf = NULL;

    st = MCSPI_transfer(ctx->mcspi_handle, &ctx->txn);

    return ((st == SystemP_SUCCESS) && (ctx->txn.status == MCSPI_TRANSFER_COMPLETED))
           ? 0 : -1;
}
