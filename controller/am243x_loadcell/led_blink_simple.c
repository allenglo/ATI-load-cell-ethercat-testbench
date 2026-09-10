/*
 * AM243x LaunchPad LED Control - Simplified Version
 * Controls 3 LEDs on GPIO1_0, GPIO1_2, GPIO1_35
 */

#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/ClockP.h>
#include <drivers/gpio.h>

/* GPIO pin definitions for LEDs */
#define LED1_BASE       (CSL_GPIO1_U_BASE)
#define LED1_PIN        (0U)

#define LED2_BASE       (CSL_GPIO1_U_BASE)
#define LED2_PIN        (2U)

#define LED3_BASE       (CSL_GPIO1_U_BASE)
#define LED3_PIN        (35U)

/* LED pattern timing (milliseconds) */
#define LED1_BLINK_MS   (500U)
#define LED2_BLINK_MS   (1000U)
#define LED3_BLINK_MS   (1500U)

#define RUN_TIME_SEC    (60U)

/* GPIO register access macros */
#define GPIO_OUT_DATA_REG_OFFSET    (0x100U)
#define GPIO_OUT_EN_REG_OFFSET      (0x104U)
#define GPIO_OUT_DATA(base)         ((base) + GPIO_OUT_DATA_REG_OFFSET)
#define GPIO_OUT_EN(base)           ((base) + GPIO_OUT_EN_REG_OFFSET)

#define GPIO_SET_OUTPUT(base, pin)  do { \
    uint32_t reg = HW_RD_REG32(GPIO_OUT_EN(base)); \
    reg |= (1U << (pin)); \
    HW_WR_REG32(GPIO_OUT_EN(base), reg); \
} while(0)

#define GPIO_SET_HIGH(base, pin)    do { \
    uint32_t reg = HW_RD_REG32(GPIO_OUT_DATA(base)); \
    reg |= (1U << (pin)); \
    HW_WR_REG32(GPIO_OUT_DATA(base), reg); \
} while(0)

#define GPIO_SET_LOW(base, pin)     do { \
    uint32_t reg = HW_RD_REG32(GPIO_OUT_DATA(base)); \
    reg &= ~(1U << (pin)); \
    HW_WR_REG32(GPIO_OUT_DATA(base), reg); \
} while(0)

void main(void)
{
    uint32_t elapsedMs = 0;
    uint32_t runTimeMs = RUN_TIME_SEC * 1000U;
    uint32_t stepMs = 100U;
    uint32_t led1State, led2State, led3State;

    DebugP_log("\r\n");
    DebugP_log("========================================\r\n");
    DebugP_log("AM243x LED Control Application\r\n");
    DebugP_log("========================================\r\n");
    DebugP_log("GPIO Pins:\r\n");
    DebugP_log("  LED1 -> GPIO1_0  (500ms blink)\r\n");
    DebugP_log("  LED2 -> GPIO1_2  (1000ms blink)\r\n");
    DebugP_log("  LED3 -> GPIO1_35 (1500ms blink)\r\n");
    DebugP_log("Runtime: %u seconds\r\n", RUN_TIME_SEC);
    DebugP_log("========================================\r\n\r\n");

    /* Configure GPIO pins as outputs */
    GPIO_SET_OUTPUT(LED1_BASE, LED1_PIN);
    GPIO_SET_OUTPUT(LED2_BASE, LED2_PIN);
    GPIO_SET_OUTPUT(LED3_BASE, LED3_PIN);
    
    DebugP_log("GPIO pins configured as outputs.\r\n");
    DebugP_log("Starting LED blink test...\r\n\r\n");

    /* Main blink loop */
    while (elapsedMs < runTimeMs) {
        
        /* Calculate LED states based on elapsed time */
        led1State = ((elapsedMs / LED1_BLINK_MS) % 2);
        led2State = ((elapsedMs / LED2_BLINK_MS) % 2);
        led3State = ((elapsedMs / LED3_BLINK_MS) % 2);

        /* Set GPIO outputs */
        if (led1State) {
            GPIO_SET_HIGH(LED1_BASE, LED1_PIN);
        } else {
            GPIO_SET_LOW(LED1_BASE, LED1_PIN);
        }

        if (led2State) {
            GPIO_SET_HIGH(LED2_BASE, LED2_PIN);
        } else {
            GPIO_SET_LOW(LED2_BASE, LED2_PIN);
        }

        if (led3State) {
            GPIO_SET_HIGH(LED3_BASE, LED3_PIN);
        } else {
            GPIO_SET_LOW(LED3_BASE, LED3_PIN);
        }

        /* Print status every 5 seconds */
        if ((elapsedMs % 5000U) == 0U && elapsedMs > 0U) {
            DebugP_log("[%2us] LED1:%s  LED2:%s  LED3:%s\r\n",
                (elapsedMs / 1000U),
                (led1State ? "ON " : "OFF"),
                (led2State ? "ON " : "OFF"),
                (led3State ? "ON " : "OFF"));
        }

        /* Small delay */
        ClockP_usleep(stepMs * 1000U);
        elapsedMs += stepMs;
    }

    /* Turn off all LEDs */
    GPIO_SET_LOW(LED1_BASE, LED1_PIN);
    GPIO_SET_LOW(LED2_BASE, LED2_PIN);
    GPIO_SET_LOW(LED3_BASE, LED3_PIN);

    DebugP_log("\r\n");
    DebugP_log("========================================\r\n");
    DebugP_log("LED Test Complete - All LEDs OFF\r\n");
    DebugP_log("========================================\r\n");

    return;
}
