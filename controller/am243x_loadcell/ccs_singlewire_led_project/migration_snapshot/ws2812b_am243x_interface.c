#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/ClockP.h>
#include <drivers/mcspi.h>
#include <stdarg.h>
#include <stdio.h>
#include "ti_drivers_config.h"
#include "driver_ws2812b_interface.h"

static MCSPI_Transaction gWsSpiTxn;

uint8_t ws2812b_interface_spi_10mhz_init(void)
{
    Drivers_open();
    Board_driversOpen();

    gConfigMcspi0ChCfg[0].bitRate = 10000000U;
    gConfigMcspi0ChCfg[0].trMode = MCSPI_TR_MODE_TX_ONLY;

    MCSPI_Transaction_init(&gWsSpiTxn);
    gWsSpiTxn.channel = gConfigMcspi0ChCfg[0].chNum;
    gWsSpiTxn.dataSize = 8U;
    gWsSpiTxn.csDisable = TRUE;
    gWsSpiTxn.rxBuf = NULL;
    gWsSpiTxn.args = NULL;

    return 0;
}

uint8_t ws2812b_interface_spi_deinit(void)
{
    Board_driversClose();
    Drivers_close();
    return 0;
}

uint8_t ws2812b_interface_spi_write_cmd(uint8_t *buf, uint16_t len)
{
    int32_t status;

    gWsSpiTxn.count = len;
    gWsSpiTxn.txBuf = (void *)buf;

    status = MCSPI_transfer(gMcspiHandle[CONFIG_MCSPI0], &gWsSpiTxn);
    if ((status != SystemP_SUCCESS) || (gWsSpiTxn.status != MCSPI_TRANSFER_COMPLETED))
    {
        return 1;
    }
    return 0;
}

void ws2812b_interface_delay_ms(uint32_t ms)
{
    ClockP_usleep(ms * 1000U);
}

void ws2812b_interface_debug_print(const char *const fmt, ...)
{
    char buf[256];
    va_list args;
    va_start(args, fmt);
    (void)vsnprintf(buf, sizeof(buf), fmt, args);
    va_end(args);
    DebugP_log("%s", buf);
}
