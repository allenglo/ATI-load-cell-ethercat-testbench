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
#define EPWM3_OUTA_BASE_ADDR (CSL_EPWM5_EPWM_BASE)
#define EPWM3_OUTA_FCLK (250000000)
#define EPWM3_OUTA_INTR (118)
#define EPWM3_OUTA_TRIP_INTR (139)
#define EPWM3_OUTA_INTR_IS_PULSE (TRUE)
#define EPWM4_BASE_ADDR (CSL_EPWM7_EPWM_BASE)
#define EPWM4_FCLK (250000000)
#define EPWM4_INTR (148)
#define EPWM4_TRIP_INTR (149)
#define EPWM4_INTR_IS_PULSE (TRUE)
#define EPWM5_BASE_ADDR (CSL_EPWM8_EPWM_BASE)
#define EPWM5_FCLK (250000000)
#define EPWM5_INTR (150)
#define EPWM5_TRIP_INTR (178)
#define EPWM5_INTR_IS_PULSE (TRUE)
#define EPWM3_OUTB_BASE_ADDR (CSL_EPWM3_EPWM_BASE)
#define EPWM3_OUTB_FCLK (250000000)
#define EPWM3_OUTB_INTR (114)
#define EPWM3_OUTB_TRIP_INTR (115)
#define EPWM3_OUTB_INTR_IS_PULSE (TRUE)
#define CONFIG_EPWM_NUM_INSTANCES (4U)

/*
 * IPC Notify
 */
#include <drivers/ipc_notify.h>



#include <drivers/soc.h>
#include <kernel/dpl/CycleCounterP.h>


#ifdef __cplusplus
}
#endif

#endif /* TI_DRIVERS_CONFIG_H_ */
