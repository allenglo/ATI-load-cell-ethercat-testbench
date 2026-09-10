/*
 *  WS2812 addressable LED driver — MCSPI SPI0_D0, board pin 55 (LP-AM243).
 *
 *  Encoding: each WS2812 data bit → 12 SPI bits @ 10 MHz (100 ns/SPI-bit,
 *  1.2 µs/symbol, matching the 1.25 µs WS2812 bit period):
 *    T1 = 0xFE0  (7 HIGH + 5 LOW → 700 ns / 500 ns)
 *    T0 = 0xF00  (4 HIGH + 8 LOW → 400 ns / 800 ns)
 *  Reset pulse: ≥320 zero-bytes → 256 µs LOW (WS2812 needs >50 µs).
 *
 *  BUG FIX: bitRate and trMode MUST be set in gConfigMcspi0ChCfg before
 *  Drivers_open() — the driver copies them into hardware at open time.
 */

#include <kernel/dpl/DebugP.h>
#include <string.h>
#include <drivers/mcspi.h>
#include <kernel/dpl/ClockP.h>
#include "ti_drivers_config.h"
#include "ti_drivers_open_close.h"
#include "ti_board_open_close.h"

/* ---- config ------------------------------------------------------------ */
#define WS_LED_COUNT        (16U)
#define WS_SPI_HZ           (10000000U)  /* 10 MHz → 100 ns/bit          */
#define WS_SYM_BITS         (12U)        /* SPI bits per WS2812 data bit  */
#define WS_RESET_BYTES      (320U)       /* 256 µs reset (>50 µs needed)  */

/* SPI symbol values (MSB-first in 12-bit field) */
/*
 * WS2812 SPI symbol values (MSB-first, 12-bit, 10 MHz = 100 ns/bit)
 *
 * Root cause of all-white: T0H=400ns was too close to clone threshold.
 * Fix: widen gap between T0H and T1H to 500 ns:
 *   T0: 3 HIGH + 9 LOW = 300 ns / 900 ns  (spec 350±150 / 800±150)
 *   T1: 8 HIGH + 4 LOW = 800 ns / 400 ns  (spec 700±150 / 600±150)
 */
#define WS_ONE              (0xFF0U)     /* 1111 1111 0000  T1H=800ns */
#define WS_ZERO             (0xE00U)     /* 1110 0000 0000  T0H=300ns */

/* frame sizes */
#define WS_PAYLOAD_BITS     (WS_LED_COUNT * 24U * WS_SYM_BITS)
#define WS_PAYLOAD_BYTES    ((WS_PAYLOAD_BITS + 7U) / 8U)
#define WS_FRAME_BYTES      (WS_PAYLOAD_BYTES + WS_RESET_BYTES)

/* animation speed */
#define WS_STEP_US          (40000U)     /* 40 ms per step → ~25 fps      */

/* ---- state ------------------------------------------------------------- */
static uint8_t           gFrame[WS_FRAME_BYTES];
static uint8_t           gGrb[WS_LED_COUNT][3U]; /* [G, R, B] per LED   */
static MCSPI_Transaction gTxn;

/* ---- helpers ----------------------------------------------------------- */

/* Write one bit into the flat SPI bit-stream buffer */
static void ws_set_bit(uint8_t *buf, uint32_t pos, uint8_t val)
{
    uint32_t byte = pos >> 3U;
    uint32_t bit  = 7U - (pos & 7U);
    if (val)
        buf[byte] |=  (uint8_t)(1U << bit);
    else
        buf[byte] &= (uint8_t)~(1U << bit);
}

/* Append a 12-bit SPI symbol to the stream */
static void ws_emit(uint8_t *buf, uint32_t *pos, uint16_t sym)
{
    uint32_t k;
    for (k = 0U; k < WS_SYM_BITS; k++)
    {
        ws_set_bit(buf, *pos, (uint8_t)((sym >> (WS_SYM_BITS - 1U - k)) & 1U));
        (*pos)++;
    }
}

/* Build the full SPI frame from gGrb[] */
static void ws_build_frame(void)
{
    uint32_t led, ch, bit, pos = 0U;
    memset(gFrame, 0, sizeof(gFrame));
    for (led = 0U; led < WS_LED_COUNT; led++)
    {
        for (ch = 0U; ch < 3U; ch++)
        {
            uint8_t v = gGrb[led][ch];
            for (bit = 0U; bit < 8U; bit++)
            {
                uint8_t db = (uint8_t)((v >> (7U - bit)) & 1U);
                ws_emit(gFrame, &pos, db ? WS_ONE : WS_ZERO);
            }
        }
    }
    /* remaining bytes stay 0 → reset pulse */
}

/* Send the frame over SPI */
static int32_t ws_send(void)
{
    int32_t st;
    gTxn.count  = WS_FRAME_BYTES;
    gTxn.txBuf  = (void *)gFrame;
    gTxn.rxBuf  = NULL;
    st = MCSPI_transfer(gMcspiHandle[CONFIG_MCSPI0], &gTxn);
    return ((st == SystemP_SUCCESS) && (gTxn.status == MCSPI_TRANSFER_COMPLETED))
           ? SystemP_SUCCESS : SystemP_FAILURE;
}

/* ---- patterns ---------------------------------------------------------- */

/* Simple HSV hue → GRB, hue 0-255, sat/val 0-255 */
static void hsv_to_grb(uint8_t h, uint8_t s, uint8_t v,
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

/* Rainbow chase: each LED offset by 256/LED_COUNT in hue space */
static void fill_rainbow(uint32_t step)
{
    uint32_t i;
    for (i = 0U; i < WS_LED_COUNT; i++)
    {
        uint8_t hue = (uint8_t)((step + (i * 256U / WS_LED_COUNT)) & 0xFFU);
        hsv_to_grb(hue, 255U, 120U, &gGrb[i][0], &gGrb[i][1], &gGrb[i][2]);
    }
}

/* ---- entry point ------------------------------------------------------- */

void mcspi_loopback_main(void *args)
{
    uint32_t step = 0U;

    /*
     * CRITICAL: set bitRate and trMode BEFORE Drivers_open().
     * The driver copies these into hardware registers at open time.
     * Setting them after open has NO effect (verified in mcspi_v0.c lines 225-228).
     */
    gConfigMcspi0ChCfg[0].bitRate = WS_SPI_HZ;
    gConfigMcspi0ChCfg[0].trMode  = MCSPI_TR_MODE_TX_ONLY;

    Drivers_open();
    Board_driversOpen();

    MCSPI_Transaction_init(&gTxn);
    gTxn.channel   = gConfigMcspi0ChCfg[0].chNum;
    gTxn.dataSize  = 8U;
    gTxn.csDisable = TRUE;

    DebugP_log("\r\n[WS2812] Driver start: %u LEDs on SPI0_D0 (board pin 55)\r\n",
               WS_LED_COUNT);
    DebugP_log("[WS2812] SPI @ %u Hz, 12-bit symbols, rainbow chase\r\n",
               WS_SPI_HZ);

    while (1)
    {
        fill_rainbow(step);
        ws_build_frame();

        if (ws_send() != SystemP_SUCCESS)
        {
            DebugP_logError("[WS2812] SPI transfer failed — halting\r\n");
            break;
        }

        if ((step % 25U) == 0U)
            DebugP_log("[WS2812] step=%u\r\n", step);

        ClockP_usleep(WS_STEP_US);
        step++;
    }

    Board_driversClose();
    Drivers_close();
}
