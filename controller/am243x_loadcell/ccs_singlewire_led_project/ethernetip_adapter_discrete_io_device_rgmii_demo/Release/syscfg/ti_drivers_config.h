/*
 *  Copyright (C) 2021 Texas Instruments Incorporated
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *    Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 *    Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the
 *    distribution.
 *
 *    Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 *  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 *  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 *  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 *  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 *  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 * Auto generated file
 */

#ifndef TI_DRIVERS_CONFIG_H_
#define TI_DRIVERS_CONFIG_H_

#include <stdint.h>
#include <drivers/hw_include/cslr_soc.h>
#include <drivers/hw_include/hw_types.h>
#include "ti_dpl_config.h"

#ifdef __cplusplus
extern "C" {
#endif


/*
 * Common Functions
 */
void System_init(void);
void System_deinit(void);

/*
 * I2C
 */

/* I2C Instance Macros */
#define CONFIG_I2C0 (0U)

/* I2C Includes */
#include <drivers/i2c.h>
#include <kernel/dpl/ClockP.h>

#define CONFIG_I2C_HLD_NUM_INSTANCES (1U)

/*
 * OSPI
 */
#include <drivers/ospi.h>

/* OSPI Instance Macros */
#define CONFIG_OSPI0 (0U)
#define CONFIG_OSPI_NUM_INSTANCES (1U)
#define CONFIG_OSPI_NUM_DMA_INSTANCES (0U)
/*
 * PRUICSS
 */
#include <drivers/pruicss.h>

/* PRUICSS Instance Macros */
#define CONFIG_PRU_ICSS1 (0U)
#define CONFIG_PRU_ICSS1_CORE_CLK_FREQ_HZ     (200000000U)
#define CONFIG_PRU_ICSS1_CORE_CLK_PERIOD_NSEC (5)
#define CONFIG_PRU_ICSS1_IEP_CLK_FREQ_HZ      (200000000U)
#define CONFIG_PRU_ICSS1_IEP_CLK_PERIOD_NSEC  (5)
#define CONFIG_PRU_ICSS1_UART_CLK_FREQ_HZ      (192000000U)
#define CONFIG_PRU_ICSS1_UART_CLK_PERIOD_NSEC  (5.208333333333333)
#define CONFIG_PRUICSS_NUM_INSTANCES (1U)


/*
 * UART
 */
#include <drivers/uart.h>
/* UART Instance Macros */
#define CONFIG_UART1 (0U)
#define CONFIG_UART_CONSOLE (1U)
#define CONFIG_UART_NUM_INSTANCES (2U)
#define CONFIG_UART_NUM_DMA_INSTANCES (0U)

/* MDIO manual mode specific defines */
#define     MDIO_MANUAL_MODE_LINK_POLLING_ENABLE            0x1
#define     MDIO_MANUAL_MODE_LINK_POLLING_DISABLE           0x0
#define     MDIO_MANUAL_MODE_LINK_POLLING_INTR_ENABLE       0x2
#define     MDIO_MANUAL_MODE_LINK_POLLING_INTR_DISABLE      0x0
#define     MDIO_MANUAL_MODE_PRU_CLK_FREQ_200               0x0
#define     MDIO_MANUAL_MODE_PRU_CLK_FREQ_250               0x4
#define     MDIO_MANUAL_MODE_PRU_CLK_FREQ_333               0x8

#define     MDIO_MANUAL_MODE_FW_CONFIG_VALUE    (MDIO_MANUAL_MODE_LINK_POLLING_ENABLE | MDIO_MANUAL_MODE_LINK_POLLING_INTR_ENABLE | MDIO_MANUAL_MODE_PRU_CLK_FREQ_200)

/*
 * ICSS EMAC
 */
#include <networking/icss_emac/icss_emac.h>

/* ICSS EMAC Instance Macros */
#define CONFIG_ICSS_EMAC0 (0U)
#define CONFIG_ICSS_EMAC_INSTANCES (1U)


#include <drivers/soc.h>
#include <kernel/dpl/CycleCounterP.h>

/*
 * MCU_LBIST
 */
void SDL_lbist_selftest(void);

#ifdef __cplusplus
}
#endif

#endif /* TI_DRIVERS_CONFIG_H_ */
