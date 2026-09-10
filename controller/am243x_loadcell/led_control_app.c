/*
 * AM243x LaunchPad LED Control Application
 * Drives 3 LEDs on GPIO pins: GPIO1_0, GPIO1_2, GPIO1_35
 * 
 * LED Patterns:
 * - LED1 (GPIO1_0):  Blink 500ms on/off
 * - LED2 (GPIO1_2):  Blink 1s on/off (half speed)
 * - LED3 (GPIO1_35): Blink 1.5s on/off (slowest)
 */

#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/ClockP.h>
#include <drivers/gpio.h>
#include "ti_drivers_config.h"
#include "ti_drivers_open_close.h"
#include "ti_board_open_close.h"

/* GPIO Configuration */
#define LED1_PIN    0   /* GPIO1_0 on J4, pin 33 */
#define LED2_PIN    2   /* GPIO1_2 on J4, pin 31 */
#define LED3_PIN    35  /* GPIO1_35 on J4, pin 79 */

#define LED_GPIO_BASE_ADDR   (0x42110000U)  /* GPIO1 base address */

/* LED state tracking */
typedef struct {
    uint32_t pin;
    uint32_t delayMs;
    uint32_t state;
    char *name;
} LED_Config;

LED_Config leds[3] = {
    { LED1_PIN,  500, 0, "LED1 (GPIO1_0)" },
    { LED2_PIN, 1000, 0, "LED2 (GPIO1_2)" },
    { LED3_PIN, 1500, 0, "LED3 (GPIO1_35)" },
};

#define NUM_LEDS 3

/* Function prototypes */
void gpio_init_led(uint32_t pin);
void gpio_set_led(uint32_t pin, uint32_t state);
void led_control_main(void *args);

/*
 * Initialize GPIO pin as output for LED
 */
void gpio_init_led(uint32_t pin)
{
    GPIO_Config gpioCfg;
    GPIO_PinConfig pinCfg;

    /* Configure GPIO pin as output */
    pinCfg.pin = pin;
    pinCfg.pinDirection = GPIO_DIR_OUTPUT;
    pinCfg.pinOutputBuffer = GPIO_OUTBUF_NORMAL;
    
    GPIO_init();
    GPIO_configure(LED_GPIO_BASE_ADDR, &pinCfg);
    
    DebugP_log("Initialized LED on GPIO1_%u\r\n", pin);
}

/*
 * Set GPIO pin state (1=ON, 0=OFF)
 */
void gpio_set_led(uint32_t pin, uint32_t state)
{
    if (state) {
        GPIO_setOutputHigh(LED_GPIO_BASE_ADDR, pin);
    } else {
        GPIO_setOutputLow(LED_GPIO_BASE_ADDR, pin);
    }
}

/*
 * Main LED control application
 * Blinks all 3 LEDs with different rates for 60 seconds
 */
void led_control_main(void *args)
{
    int32_t i;
    uint32_t runTime = 60; /* Run for 60 seconds */
    uint32_t loopTime = 100; /* Check every 100ms */
    uint32_t elapsedTime = 0;

    /* Initialize drivers */
    Drivers_open();
    Board_driversOpen();

    DebugP_log("\r\n");
    DebugP_log("==============================================\r\n");
    DebugP_log("AM243x LaunchPad LED Control Application\r\n");
    DebugP_log("==============================================\r\n");
    DebugP_log("Blinking 3 LEDs with different rates:\r\n");
    DebugP_log("  - LED1: 500ms blink rate (fastest)\r\n");
    DebugP_log("  - LED2: 1000ms blink rate\r\n");
    DebugP_log("  - LED3: 1500ms blink rate (slowest)\r\n");
    DebugP_log("Duration: %u seconds\r\n", runTime);
    DebugP_log("==============================================\r\n\r\n");

    /* Initialize LED GPIO pins */
    for (i = 0; i < NUM_LEDS; i++) {
        gpio_init_led(leds[i].pin);
    }

    /* LED blink loop */
    while (elapsedTime < (runTime * 1000)) {
        
        for (i = 0; i < NUM_LEDS; i++) {
            /* Check if it's time to toggle this LED */
            if (((elapsedTime / leds[i].delayMs) % 2) == 0) {
                leds[i].state = 1;  /* ON */
            } else {
                leds[i].state = 0;  /* OFF */
            }
            
            gpio_set_led(leds[i].pin, leds[i].state);
        }

        /* Print status every 5 seconds */
        if ((elapsedTime % 5000) == 0 && elapsedTime > 0) {
            DebugP_log("[%3us] LED1:%s  LED2:%s  LED3:%s\r\n",
                (elapsedTime / 1000),
                (leds[0].state ? "ON " : "OFF"),
                (leds[1].state ? "ON " : "OFF"),
                (leds[2].state ? "ON " : "OFF"));
        }

        /* Wait 100ms before next check */
        ClockP_sleep(loopTime / 1000.0);
        elapsedTime += loopTime;
    }

    /* Turn off all LEDs */
    for (i = 0; i < NUM_LEDS; i++) {
        gpio_set_led(leds[i].pin, 0);
    }

    DebugP_log("\r\n");
    DebugP_log("==============================================\r\n");
    DebugP_log("LED Control Test Completed Successfully!\r\n");
    DebugP_log("All LEDs turned OFF.\r\n");
    DebugP_log("==============================================\r\n");

    Board_driversClose();
    Drivers_close();
}
