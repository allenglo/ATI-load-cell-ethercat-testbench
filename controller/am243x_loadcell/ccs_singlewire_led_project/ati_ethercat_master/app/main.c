#include <stdlib.h>
#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/SystemP.h>
#include "ti_drivers_config.h"
#include "ti_board_config.h"
#include "ti_drivers_open_close.h"
#include "ti_board_open_close.h"
#include "FreeRTOS.h"
#include "task.h"
#include <string.h>

#define MAIN_TASK_PRI  (2)
#define MAIN_TASK_SIZE (16384U/sizeof(configSTACK_DEPTH_TYPE))

#define TRACE_MAIN(fmt, ...) DebugP_log("[MAIN][TRACE] %s:%d " fmt "\r\n", __FUNCTION__, __LINE__, ##__VA_ARGS__)
#define ERROR_MAIN(fmt, ...) DebugP_log("[MAIN][ERROR] %s:%d " fmt "\r\n", __FUNCTION__, __LINE__, ##__VA_ARGS__)

static StackType_t  gMainTaskStack[MAIN_TASK_SIZE] __attribute__((aligned(32)));
static StaticTask_t gMainTaskObj;
static TaskHandle_t gMainTask;

void ati_ecat_master_task(void *args);

static void raw_uart_probe(const char *msg)
{
    UART_Transaction trans;

    if ((msg == NULL) || (gUartHandle[CONFIG_UART0] == NULL))
    {
        return;
    }

    UART_Transaction_init(&trans);
    trans.buf = (void *)msg;
    trans.count = strlen(msg);
    if (trans.count > 0U)
    {
        (void)UART_write(gUartHandle[CONFIG_UART0], &trans);
        UART_flushTxFifo(gUartHandle[CONFIG_UART0]);
    }
}

static void freertos_main(void *args)
{
    int32_t status;

    TRACE_MAIN("freertos_main enter args=%p", args);

    TRACE_MAIN("Drivers_open() begin");
    Drivers_open();
    TRACE_MAIN("Drivers_open() done");
    raw_uart_probe("[UART][RAW] after Drivers_open\r\n");

    TRACE_MAIN("Board_driversOpen() begin");
    status = Board_driversOpen();
    TRACE_MAIN("Board_driversOpen() status=%d", status);
    raw_uart_probe("[UART][RAW] after Board_driversOpen\r\n");
    if (status != SystemP_SUCCESS)
    {
        ERROR_MAIN("Board_driversOpen failed status=%d", status);
        raw_uart_probe("[UART][RAW][ERROR] Board_driversOpen failed\r\n");
    }
    DebugP_assert(status == SystemP_SUCCESS);

    DebugP_log("[ECAT] main start\r\n");
    TRACE_MAIN("ati_ecat_master_task() begin");
    ati_ecat_master_task(NULL);
    TRACE_MAIN("ati_ecat_master_task() returned");

    TRACE_MAIN("Board_driversClose() begin");
    Board_driversClose();
    TRACE_MAIN("Board_driversClose() done");

    TRACE_MAIN("Drivers_close() begin");
    Drivers_close();
    TRACE_MAIN("Drivers_close() done");

    TRACE_MAIN("vTaskDelete(NULL)");
    vTaskDelete(NULL);
}

int main(void)
{
    System_init();
    TRACE_MAIN("System_init() done");

    TRACE_MAIN("Board_init() begin");
    Board_init();
    TRACE_MAIN("Board_init() done");

    TRACE_MAIN("xTaskCreateStatic(freertos_main) begin");
    gMainTask = xTaskCreateStatic(freertos_main, "freertos_main",
                                  MAIN_TASK_SIZE, NULL, MAIN_TASK_PRI,
                                  gMainTaskStack, &gMainTaskObj);
    TRACE_MAIN("xTaskCreateStatic result=%p", gMainTask);
    if (gMainTask == NULL)
    {
        ERROR_MAIN("xTaskCreateStatic failed");
    }
    configASSERT(gMainTask != NULL);

    TRACE_MAIN("vTaskStartScheduler() begin");
    vTaskStartScheduler();

    ERROR_MAIN("vTaskStartScheduler() returned unexpectedly");
    DebugP_assertNoLog(0);
    return 0;
}
