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
 * EPWM
 */
#include <drivers/epwm.h>
#include <drivers/soc.h>

/* EPWM Instance Macros */
#define EPWM0_BASE_ADDR (CSL_EPWM2_EPWM_BASE)
#define EPWM0_FCLK (250000000)
#define EPWM0_INTR (112)
#define EPWM0_TRIP_INTR (113)
#define EPWM0_INTR_IS_PULSE (TRUE)
#define EPWM1_BASE_ADDR (CSL_EPWM1_EPWM_BASE)
#define EPWM1_FCLK (250000000)
#define EPWM1_INTR (110)
#define EPWM1_TRIP_INTR (111)
#define EPWM1_INTR_IS_PULSE (TRUE)
#define EPWM2_BASE_ADDR (CSL_EPWM0_EPWM_BASE)
#define EPWM2_FCLK (250000000)
#define EPWM2_INTR (108)
#define EPWM2_TRIP_INTR (109)
#define EPWM2_INTR_IS_PULSE (TRUE)
#define CONFIG_EPWM_NUM_INSTANCES (3U)

/*
 * GPIO
 */
#include <drivers/gpio.h>
#include <kernel/dpl/AddrTranslateP.h>

/* GPIO PIN Macros */
#define MTR_1_PWM_EN_BASE_ADDR (CSL_GPIO1_BASE)
#define MTR_1_PWM_EN_PIN (64)
#define MTR_1_PWM_EN_DIR (GPIO_DIRECTION_OUTPUT)
#define MTR_1_PWM_EN_TRIG_TYPE (GPIO_TRIG_TYPE_NONE)
#define MTR_2_PWM_EN_BASE_ADDR (CSL_GPIO1_BASE)
#define MTR_2_PWM_EN_PIN (65)
#define MTR_2_PWM_EN_DIR (GPIO_DIRECTION_OUTPUT)
#define MTR_2_PWM_EN_TRIG_TYPE (GPIO_TRIG_TYPE_NONE)
#define BP_MUX_SEL_BASE_ADDR (CSL_GPIO0_BASE)
#define BP_MUX_SEL_PIN (26)
#define BP_MUX_SEL_DIR (GPIO_DIRECTION_OUTPUT)
#define BP_MUX_SEL_TRIG_TYPE (GPIO_TRIG_TYPE_NONE)
#define ENC1_EN_BASE_ADDR (CSL_GPIO1_BASE)
#define ENC1_EN_PIN (78)
#define ENC1_EN_DIR (GPIO_DIRECTION_OUTPUT)
#define ENC1_EN_TRIG_TYPE (GPIO_TRIG_TYPE_NONE)
#define ENC2_EN_BASE_ADDR (CSL_GPIO1_BASE)
#define ENC2_EN_PIN (77)
#define ENC2_EN_DIR (GPIO_DIRECTION_OUTPUT)
#define ENC2_EN_TRIG_TYPE (GPIO_TRIG_TYPE_NONE)
#define CONFIG_GPIO_NUM_INSTANCES (5U)

/*
 * IPC Notify
 */
#include <drivers/ipc_notify.h>


/*
 * MCSPI
 */
#include <drivers/mcspi.h>

/* MCSPI Instance Macros */
#define CONFIG_MCSPI0 (0U)
#define CONFIG_MCSPI_NUM_INSTANCES (1U)
#define CONFIG_MCSPI_NUM_DMA_INSTANCES (0U)

/*
 * UDMA
 */
#include <drivers/udma.h>

/* UDMA Instance Macros */
#define CONFIG_UDMA0 (0U)
#define CONFIG_UDMA_NUM_INSTANCES (1U)

/* UDMA Driver Objects */
extern Udma_DrvObject   gUdmaDrvObj[CONFIG_UDMA_NUM_INSTANCES];

/* UDMA functions as specified in SYSCONFIG */
/* For instance CONFIG_UDMA0 */
extern uint64_t Udma_defaultVirtToPhyFxn(const void *virtAddr, uint32_t chNum, void *appData);
extern void *Udma_defaultPhyToVirtFxn(uint64_t phyAddr, uint32_t chNum, void *appData);

/*
 * PRUICSS
 */
#include <drivers/pruicss.h>

/* PRUICSS Instance Macros */
#define CONFIG_PRU_ICSS0 (0U)
#define CONFIG_PRU_ICSS0_CORE_CLK_FREQ_HZ     (300000000U)
#define CONFIG_PRU_ICSS0_CORE_CLK_PERIOD_NSEC (3.3333333333333335)
#define CONFIG_PRU_ICSS0_IEP_CLK_FREQ_HZ      (300000000U)
#define CONFIG_PRU_ICSS0_IEP_CLK_PERIOD_NSEC  (3.3333333333333335)
#define CONFIG_PRUICSS_NUM_INSTANCES (1U)

/*
 * EnDat
 */

/* EnDat Instance Macros */
#define CONFIG_ENDAT_NUM_INSTANCES               1


#define CONFIG_ENDAT0                  0
#define CONFIG_ENDAT0_CHANNEL0         1
#define CONFIG_ENDAT0_CHANNEL1         0
#define CONFIG_ENDAT0_CHANNEL2         1
#define CONFIG_ENDAT0_load_share_mode  1
#define  CONFIG_ENDAT0_MODE             2
#define CONFIG_ENDAT0_BOOSTER_PACK     1
#define  PRU_ICSSGx_PRU_SLICE            1




/*
 * PRU_IPC
 */
#include <pru_io/driver/pru_ipc.h>
#include <pru_io/driver/icss_intc_defines.h>

/* PRU_IPC Instance Macros */
#define CONFIG_PRU_IPC_NUM_INSTANCES    1
#define CONFIG_PRU_IPC0                 0
#define CONFIG_PRU_IPC0_BLOCKSIZE       32
#define CONFIG_PRU_IPC0_BUFFERS         1

/*
 *  ICSS_INTC
 */
#include <pru_io/driver/icss_intc_defines.h>
extern PRUICSS_IntcInitData icss0_intc_initdata;


#include <drivers/soc.h>
#include <kernel/dpl/CycleCounterP.h>


#ifdef __cplusplus
}
#endif

#endif /* TI_DRIVERS_CONFIG_H_ */
