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
#include "ti_drivers_config.h"
#include <drivers/pinmux.h>

static Pinmux_PerCfg_t gPinMuxMainDomainCfg[] = {
            /* EHRPWM5 pin config */
    /* EHRPWM5_A -> GPMC0_BE1n (P21) */
    {
        PIN_GPMC0_BE1N,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },
            /* EHRPWM7 pin config */
    /* EHRPWM7_A -> PRG0_PRU1_GPO18 (D1) */
    {
        PIN_PRG0_PRU1_GPO18,
        ( PIN_MODE(6) | PIN_PULL_DISABLE )
    },
    /* EHRPWM7 pin config */
    /* EHRPWM7_B -> PRG0_PRU1_GPO19 (F3) */
    {
        PIN_PRG0_PRU1_GPO19,
        ( PIN_MODE(6) | PIN_PULL_DISABLE )
    },
            /* EHRPWM8 pin config */
    /* EHRPWM8_A -> GPMC0_AD7 (U19) */
    {
        PIN_GPMC0_AD7,
        ( PIN_MODE(4) | PIN_PULL_DISABLE )
    },
    /* EHRPWM8 pin config */
    /* EHRPWM8_B -> GPMC0_AD10 (V20) */
    {
        PIN_GPMC0_AD10,
        ( PIN_MODE(4) | PIN_PULL_DISABLE )
    },
            /* EHRPWM3 pin config */
    /* EHRPWM3_B -> GPMC0_AD14 (Y18) */
    {
        PIN_GPMC0_AD14,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },

    {PINMUX_END, PINMUX_END}
};

static Pinmux_PerCfg_t gPinMuxMcuDomainCfg[] = {
                                
    {PINMUX_END, PINMUX_END}
};

/*
 * Pinmux
 */


void Pinmux_init(void)
{
    Pinmux_config(gPinMuxMainDomainCfg, PINMUX_DOMAIN_ID_MAIN);

    
    Pinmux_config(gPinMuxMcuDomainCfg, PINMUX_DOMAIN_ID_MCU);
}


