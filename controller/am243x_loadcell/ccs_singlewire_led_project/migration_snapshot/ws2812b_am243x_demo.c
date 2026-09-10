#include <stdint.h>
#include <kernel/dpl/ClockP.h>
#include <kernel/dpl/DebugP.h>

#include "driver_ws2812b_basic.h"

#define APP_WS_LED_COUNT        (16U)
#define APP_WS_TEMP_BUF_BYTES   (APP_WS_LED_COUNT * 48U)

static uint32_t gRgb[APP_WS_LED_COUNT];
static uint8_t gTemp[APP_WS_TEMP_BUF_BYTES];

static inline uint32_t rgb_pack(uint8_t r, uint8_t g, uint8_t b)
{
    return (((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b);
}

void ws2812b_am243x_demo_main(void *args)
{
    uint32_t i;
    uint32_t step;

    if (ws2812b_basic_init() != 0)
    {
        DebugP_logError("ws2812b init failed\r\n");
        return;
    }

    for (step = 0U; step < 64U; step++)
    {
        for (i = 0U; i < APP_WS_LED_COUNT; i++)
        {
            gRgb[i] = 0U;
        }

        gRgb[(step + 0U) % APP_WS_LED_COUNT] = rgb_pack(0x30U, 0x00U, 0x00U);
        gRgb[(step + 5U) % APP_WS_LED_COUNT] = rgb_pack(0x00U, 0x30U, 0x00U);
        gRgb[(step + 10U) % APP_WS_LED_COUNT] = rgb_pack(0x00U, 0x00U, 0x30U);

        if (ws2812b_basic_write(gRgb, APP_WS_LED_COUNT, gTemp, sizeof(gTemp)) != 0)
        {
            DebugP_logError("ws2812b write failed at step %u\r\n", step);
            break;
        }

        ClockP_usleep(120000U);
    }

    for (i = 0U; i < APP_WS_LED_COUNT; i++)
    {
        gRgb[i] = 0U;
    }
    (void)ws2812b_basic_write(gRgb, APP_WS_LED_COUNT, gTemp, sizeof(gTemp));
    (void)ws2812b_basic_deinit();

    DebugP_log("ws2812b demo done\r\n");
}
