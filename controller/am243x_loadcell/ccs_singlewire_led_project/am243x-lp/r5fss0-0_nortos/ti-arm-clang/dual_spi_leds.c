/*
 * Dual Addressable LED Demo: SPI + GPIO bit-bang
 *
 * Drives two independent LED chains:
 *   - SPI0_D0 (board pin 55):  16x WS2812 LEDs (rainbow chase) via MCSPI
 *   - GPIO pin (pin 15):        6x 645-587 LEDs (static cyan) via bit-bang
 *
 * SPI: 10 MHz, TX_ONLY, no chip select.
 * GPIO: 3.3V logic, timing via software delays.
 * Both update at 40 ms intervals (25 fps).
 *
 * NOTE: GPIO bit-banging is slower (~2-3 ms per transfer) than SPI,
 * but sufficient for a small 6-LED chain and avoids SPI port conflicts.
 */

#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/ClockP.h>
#include <kernel/dpl/AddrTranslateP.h>
#include <drivers/mcspi.h>
#include "ti_drivers_config.h"
#include <drivers/gpio.h>
#include "ti_drivers_open_close.h"
#include "ti_board_open_close.h"
#include "addressable_led.h"

/* ---- Configuration ------------------------------------------------------- */

#define LED_CHAIN_SPI_COUNT    (16U)
#define LED_CHAIN_GPIO_COUNT   (6U)
#define SPI_CLOCK_HZ           (10000000U)
#define ANIMATION_STEP_US      (40000U)

/* GPIO bit-bang timing (approximate, in CPU cycles at 800 MHz) */
#define T_HIGH_NS              (350U)      /* ~350 ns for bit=1 high time */
#define T_LOW_NS               (800U)      /* ~800 ns for bit=0 low time  */
#define T_RESET_US             (60U)       /* >50 µs reset pulse          */

/* ---- Global Contexts ----------------------------------------------------- */

static AddressableLedCtx gLedChain_SPI;   /* SPI0 → pin 55 */
static AddressableLedCtx gLedChain_GPIO;  /* GPIO → pin 15 */
static uint32_t          gLedChain2BaseAddr;
static uint32_t          gLedChain2Pin;

/* ---- GPIO Bit-Bang Helpers ----------------------------------------------- */

/* Rough delay (assumes 800 MHz core, ~1 cycle = 1.25 ns) */
static void delay_ns(uint32_t ns)
{
    uint32_t loops = (ns * 800U) / 1000U;  /* Very rough approximation */
    while (loops--);
}

/* Transmit one bit on GPIO (blocking, ~1.25 µs per bit) */
static void gpio_write_bit(uint32_t baseAddr, uint32_t pin, uint32_t bit)
{
    if (bit)
    {
        /* T1: HIGH for 350 ns, LOW for 800 ns */
        GPIO_pinWriteHigh(baseAddr, pin);
        delay_ns(T_HIGH_NS);
        GPIO_pinWriteLow(baseAddr, pin);
        delay_ns(T_LOW_NS);
    }
    else
    {
        /* T0: HIGH for ~100 ns, LOW for ~1100 ns */
        GPIO_pinWriteHigh(baseAddr, pin);
        delay_ns(100U);
        GPIO_pinWriteLow(baseAddr, pin);
        delay_ns(T_LOW_NS + 300U);
    }
}

/* Transmit full frame (304 bytes = 2432 bits ≈ 3 ms) */
static int32_t gpio_send_frame(uint32_t baseAddr, uint32_t pin, uint8_t *frame, uint32_t frame_bytes)
{
    uint32_t byte_idx, bit_idx;

    GPIO_pinWriteLow(baseAddr, pin);  /* Ensure LOW before start */
    ClockP_usleep(10U);              /* Wait for any residual charge */

    for (byte_idx = 0U; byte_idx < frame_bytes; byte_idx++)
    {
        uint8_t b = frame[byte_idx];
        for (bit_idx = 0U; bit_idx < 8U; bit_idx++)
        {
            uint8_t bit = (b >> (7U - bit_idx)) & 1U;
            gpio_write_bit(baseAddr, pin, bit);
        }
    }

    GPIO_pinWriteLow(baseAddr, pin);       /* Ensure LOW */
    ClockP_usleep(T_RESET_US);            /* Reset pulse */

    return 0;
}

/* ---- Animation Helpers --------------------------------------------------- */

/* Rainbow chase for SPI chain */
static void animate_rainbow(uint32_t step)
{
    uint32_t i;
    for (i = 0U; i < LED_CHAIN_SPI_COUNT; i++)
    {
        uint8_t hue = (uint8_t)((step + (i * 256U / LED_CHAIN_SPI_COUNT)) & 0xFFU);
        uint8_t g, r, b;
        addressable_led_hsv_to_grb(hue, 255U, 120U, &g, &r, &b);
        addressable_led_set_color(&gLedChain_SPI, i, g, r, b);
    }
}

/* Static cyan for GPIO chain */
static void set_cyan(void)
{
    addressable_led_fill(&gLedChain_GPIO, 255U, 0U, 255U);  /* G=255, R=0, B=255 */
}

/* ---- Entry Point --------------------------------------------------------- */

void dual_spi_leds_main(void *args)
{
    uint32_t step = 0U;

    /*
     * CRITICAL: Set bitRate and trMode BEFORE Drivers_open().
     * The MCSPI driver copies these to hardware at open time only.
     */
    gConfigMcspi0ChCfg[0].bitRate = SPI_CLOCK_HZ;
    gConfigMcspi0ChCfg[0].trMode  = MCSPI_TR_MODE_TX_ONLY;

    Drivers_open();
    Board_driversOpen();

    gLedChain2BaseAddr = (uint32_t)AddrTranslateP_getLocalAddr(CONFIG_GPIO_LED_CHAIN2_BASE_ADDR);
    gLedChain2Pin = CONFIG_GPIO_LED_CHAIN2_PIN;

    /* Initialize SPI chain */
    if (addressable_led_init(&gLedChain_SPI, gMcspiHandle[CONFIG_MCSPI0],
                             LED_CHAIN_SPI_COUNT, SPI_CLOCK_HZ) != 0)
    {
        DebugP_logError("[DUAL_LED] Failed to init SPI chain\r\n");
        goto cleanup;
    }

    /* Initialize GPIO chain (dummy MCSPI handle, we'll use GPIO directly) */
    if (addressable_led_init(&gLedChain_GPIO, NULL,
                             LED_CHAIN_GPIO_COUNT, SPI_CLOCK_HZ) != 0)
    {
        DebugP_logError("[DUAL_LED] Failed to init GPIO chain\r\n");
        addressable_led_deinit(&gLedChain_SPI);
        goto cleanup;
    }

    DebugP_log("\r\n[DUAL_LED] Driver start:\r\n");
    DebugP_log("[DUAL_LED]  Chain 0: %u LEDs on SPI0_D0 (pin 55) — SPI @ %u Hz\r\n",
               LED_CHAIN_SPI_COUNT, SPI_CLOCK_HZ);
    DebugP_log("[DUAL_LED]  Chain 1: %u LEDs on GPIO (pin 15) — bit-bang\r\n",
               LED_CHAIN_GPIO_COUNT);

    set_cyan();  /* Initialize GPIO chain to cyan */

    while (1)
    {
        /* Update colors */
        animate_rainbow(step);
        /* GPIO chain stays cyan (no update needed) */

        /* Transmit SPI chain */
        if (addressable_led_send(&gLedChain_SPI) != 0)
        {
            DebugP_logError("[DUAL_LED] SPI transfer failed\r\n");
            break;
        }

        /* Transmit GPIO chain (blocking, ~3 ms) */
        if (gpio_send_frame(gLedChain2BaseAddr, gLedChain2Pin, gLedChain_GPIO.frame,
                           gLedChain_GPIO.frame_bytes) != 0)
        {
            DebugP_logError("[DUAL_LED] GPIO transfer failed\r\n");
            break;
        }

        if ((step % 25U) == 0U)
            DebugP_log("[DUAL_LED] step=%u\r\n", step);

        ClockP_usleep(ANIMATION_STEP_US);
        step++;
    }

cleanup:
    addressable_led_deinit(&gLedChain_SPI);
    addressable_led_deinit(&gLedChain_GPIO);
    Board_driversClose();
    Drivers_close();
}
