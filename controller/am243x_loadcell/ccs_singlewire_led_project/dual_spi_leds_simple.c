/*
 * Dual addressable LED demo.
 *
 * Chain 0: SPI0_D0 on board pin 55, 16 LEDs, SPI symbol encoding.
 * Chain 1: J2.15 / GPIO1_13 on board pin 15, 6 LEDs, software-timed single-wire output.
 *
 * Serial debug commands (115200 8N1, send + Enter):
 *   b<0-255>  set brightness  e.g. "b200"
 *   s<1-5000> set step ms     e.g. "s80"
 *   ?         print help + current settings
 */

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/ClockP.h>
#include <kernel/dpl/HwiP.h>
#include <kernel/dpl/SystemP.h>
#include <drivers/mcspi.h>
#include <drivers/gpio.h>
#include <drivers/uart.h>
#include "ti_drivers_config.h"
#include "ti_drivers_open_close.h"
#include "ti_board_open_close.h"
#include "addressable_led.h"

/* Configuration */
#define LED_CHAIN_SPI_COUNT     (16U)
#define LED_CHAIN_GPIO_COUNT    (6U)
#define SPI_CLOCK_HZ            (10000000U)
#define ANIMATION_STEP_US       (40000U)

#define WS_SYM_BITS             (12U)
#define WS_RESET_BYTES          (320U)
#define WS_FRAME_BYTES(n)       ((((n) * 24U * WS_SYM_BITS) + 7U) / 8U + WS_RESET_BYTES)

/* 800 MHz R5F, short/long delays tuned to keep T0H << T1H. */
#define GPIO_T0H_LOOPS          (22U)
#define GPIO_T0L_LOOPS          (82U)
#define GPIO_T1H_LOOPS          (68U)
#define GPIO_T1L_LOOPS          (36U)
#define GPIO_RESET_US           (80U)

/* Global state */
static AddressableLedCtx gSpiChain;
static AddressableLedCtx gGpioChain;
static uint8_t gSpiFrame[WS_FRAME_BYTES(LED_CHAIN_SPI_COUNT)];
static uint8_t gSpiGrb[LED_CHAIN_SPI_COUNT * 3U];
static uint8_t gGpioFrame[WS_FRAME_BYTES(LED_CHAIN_GPIO_COUNT)];
static uint8_t gGpioGrb[LED_CHAIN_GPIO_COUNT * 3U];

/* Debug serial state */
static volatile uint8_t  gBrightness     = 120U;
static volatile uint32_t gStepIntervalUs = ANIMATION_STEP_US;
static char              gCmdBuf[32];
static uint32_t          gCmdLen         = 0U;

static inline void gpio_delay_loops(uint32_t loops)
{
    volatile uint32_t count = loops;

    while (count-- > 0U)
    {
        __asm__ volatile ("nop");
    }
}

static inline void gpio_chain_set_high(void)
{
    GPIO_pinWriteHigh(CONFIG_GPIO_LED_CHAIN2_BASE_ADDR, CONFIG_GPIO_LED_CHAIN2_PIN);
}

static inline void gpio_chain_set_low(void)
{
    GPIO_pinWriteLow(CONFIG_GPIO_LED_CHAIN2_BASE_ADDR, CONFIG_GPIO_LED_CHAIN2_PIN);
}

static inline void gpio_chain_write_bit(uint8_t bit_value)
{
    gpio_chain_set_high();
    if (bit_value != 0U)
    {
        gpio_delay_loops(GPIO_T1H_LOOPS);
        gpio_chain_set_low();
        gpio_delay_loops(GPIO_T1L_LOOPS);
    }
    else
    {
        gpio_delay_loops(GPIO_T0H_LOOPS);
        gpio_chain_set_low();
        gpio_delay_loops(GPIO_T0L_LOOPS);
    }
}

static void gpio_chain_send(const AddressableLedCtx *ctx)
{
    uintptr_t key;
    uint32_t led_index;
    uint32_t color_index;
    uint32_t bit_index;

    key = HwiP_disable();
    for (led_index = 0U; led_index < ctx->led_count; led_index++)
    {
        for (color_index = 0U; color_index < 3U; color_index++)
        {
            uint8_t value = ctx->grb[(led_index * 3U) + color_index];
            for (bit_index = 0U; bit_index < 8U; bit_index++)
            {
                gpio_chain_write_bit((uint8_t)((value >> (7U - bit_index)) & 1U));
            }
        }
    }
    gpio_chain_set_low();
    HwiP_restore(key);
    ClockP_usleep(GPIO_RESET_US);
}

static void animate_spi_chain(uint32_t step)
{
    uint32_t i;
    for (i = 0U; i < LED_CHAIN_SPI_COUNT; i++)
    {
        uint8_t hue = (uint8_t)((step + (i * 256U / LED_CHAIN_SPI_COUNT)) & 0xFFU);
        uint8_t g, r, b;
        addressable_led_hsv_to_grb(hue, 255U, gBrightness, &g, &r, &b);
        addressable_led_set_color(&gSpiChain, i, g, r, b);
    }
}

static void animate_gpio_chain(uint32_t step)
{
    uint32_t i;

    for (i = 0U; i < LED_CHAIN_GPIO_COUNT; i++)
    {
        uint8_t hue = (uint8_t)(((step * 3U) + (i * 256U / LED_CHAIN_GPIO_COUNT)) & 0xFFU);
        uint8_t g, r, b;
        addressable_led_hsv_to_grb(hue, 255U, gBrightness, &g, &r, &b);
        addressable_led_set_color(&gGpioChain, i, g, r, b);
    }
}

/* ---------- Serial debug console ---------- */

static void uart_puts(const char *s)
{
    UART_Transaction t;
    UART_Transaction_init(&t);
    t.buf     = (void *)s;
    t.count   = (uint32_t)strlen(s);
    t.timeout = SystemP_WAIT_FOREVER;
    (void)UART_write(gUartHandle[CONFIG_UART_CONSOLE], &t);
}

static void serial_print_status(void)
{
    char buf[128];
    snprintf(buf, sizeof(buf),
             "\r\n[LED] brightness=%u  step=%ums\r\n",
             (unsigned)gBrightness,
             (unsigned)(gStepIntervalUs / 1000U));
    uart_puts(buf);
}

static void serial_print_help(void)
{
    uart_puts("\r\n--- LED Debug ---\r\n");
    uart_puts("  b<0-255>   brightness  e.g. b200\r\n");
    uart_puts("  s<1-5000>  step ms     e.g. s80\r\n");
    uart_puts("  ?          status + help\r\n");
    serial_print_status();
}

static void process_cmd(void)
{
    gCmdBuf[gCmdLen] = '\0';
    char c0 = gCmdBuf[0];

    if (c0 == '?' || c0 == 'h' || c0 == 'H')
    {
        serial_print_help();
    }
    else if (c0 == 'b' || c0 == 'B')
    {
        unsigned long val = strtoul(gCmdBuf + 1, NULL, 10);
        if (val <= 255U)
        {
            gBrightness = (uint8_t)val;
            serial_print_status();
        }
        else
        {
            uart_puts("[LED] brightness must be 0-255\r\n");
        }
    }
    else if (c0 == 's' || c0 == 'S')
    {
        unsigned long ms = strtoul(gCmdBuf + 1, NULL, 10);
        if (ms >= 1U && ms <= 5000U)
        {
            gStepIntervalUs = (uint32_t)(ms * 1000U);
            serial_print_status();
        }
        else
        {
            uart_puts("[LED] step must be 1-5000 ms\r\n");
        }
    }
    else if (gCmdLen > 0U)
    {
        uart_puts("[LED] unknown cmd — send ? for help\r\n");
    }
}

static void poll_uart(void)
{
    UART_Transaction t;
    char ch;

    while (1)
    {
        UART_Transaction_init(&t);
        t.buf     = &ch;
        t.count   = 1U;
        t.timeout = SystemP_NO_WAIT;
        int32_t ret = UART_read(gUartHandle[CONFIG_UART_CONSOLE], &t);

        if (ret != SystemP_SUCCESS || t.count == 0U)
            break;

        /* echo the character back */
        UART_Transaction et;
        UART_Transaction_init(&et);
        et.buf     = &ch;
        et.count   = 1U;
        et.timeout = SystemP_WAIT_FOREVER;
        (void)UART_write(gUartHandle[CONFIG_UART_CONSOLE], &et);

        if (ch == '\r' || ch == '\n')
        {
            if (gCmdLen > 0U)
            {
                uart_puts("\r\n");
                process_cmd();
                gCmdLen = 0U;
            }
        }
        else if (ch == '\b' || ch == 0x7FU) /* backspace */
        {
            if (gCmdLen > 0U)
                gCmdLen--;
        }
        else if (gCmdLen < (sizeof(gCmdBuf) - 1U))
        {
            gCmdBuf[gCmdLen++] = ch;
        }
    }
}

/* Main entry */
void dual_spi_leds_main(void *args)
{
    uint32_t step = 0U;

    (void)args;

    /* CRITICAL: set bitRate BEFORE Drivers_open() */
    gConfigMcspi0ChCfg[0].bitRate = SPI_CLOCK_HZ;
    gConfigMcspi0ChCfg[0].trMode  = MCSPI_TR_MODE_TX_ONLY;

    Drivers_open();
    Board_driversOpen();

    GPIO_setDirMode(CONFIG_GPIO_LED_CHAIN2_BASE_ADDR,
                    CONFIG_GPIO_LED_CHAIN2_PIN,
                    CONFIG_GPIO_LED_CHAIN2_DIR);
    gpio_chain_set_low();

    if (addressable_led_init_with_storage(&gSpiChain, gMcspiHandle[CONFIG_MCSPI0],
                                          LED_CHAIN_SPI_COUNT, SPI_CLOCK_HZ,
                                          gSpiFrame, sizeof(gSpiFrame), gSpiGrb) != 0)
    {
        DebugP_logError("[DUAL_LED] SPI chain init failed\r\n");
        goto cleanup;
    }
    gSpiChain.txn.channel = gConfigMcspi0ChCfg[0].chNum;

    if (addressable_led_init_with_storage(&gGpioChain, NULL, LED_CHAIN_GPIO_COUNT,
                                          SPI_CLOCK_HZ, gGpioFrame,
                                          sizeof(gGpioFrame), gGpioGrb) != 0)
    {
        DebugP_logError("[DUAL_LED] GPIO chain init failed\r\n");
        addressable_led_deinit(&gSpiChain);
        goto cleanup;
    }

    DebugP_log("\r\n[DUAL_LED] Driver start:\r\n");
    DebugP_log("[DUAL_LED]  SPI0_D0 (pin 55): %u LEDs — rainbow chase\r\n",
               LED_CHAIN_SPI_COUNT);
    DebugP_log("[DUAL_LED]  GPIO1_13 (pin 15): %u LEDs — software single-wire\r\n",
               LED_CHAIN_GPIO_COUNT);
    DebugP_log("[DUAL_LED]  SPI @ %u Hz\r\n", SPI_CLOCK_HZ);
    DebugP_log("[DUAL_LED]  Serial cmds: b<brightness> s<ms> ?\r\n");

    while (1)
    {
        poll_uart();

        animate_spi_chain(step);
        animate_gpio_chain(step);

        if (addressable_led_send(&gSpiChain) != 0)
        {
            DebugP_logError("[DUAL_LED] SPI transfer failed\r\n");
            break;
        }

        gpio_chain_send(&gGpioChain);

        if ((step % 25U) == 0U)
            DebugP_log("[DUAL_LED] step=%u  b=%u  s=%ums\r\n",
                       step, (unsigned)gBrightness,
                       (unsigned)(gStepIntervalUs / 1000U));

        ClockP_usleep(gStepIntervalUs);
        step++;
    }

cleanup:
    addressable_led_deinit(&gSpiChain);
    addressable_led_deinit(&gGpioChain);
    Board_driversClose();
    Drivers_close();
}
