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
            /* EHRPWM2 pin config */
    /* EHRPWM2_A -> GPMC0_AD8 (U18) */
    {
        PIN_GPMC0_AD8,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },
    /* EHRPWM2 pin config */
    /* EHRPWM2_B -> GPMC0_AD9 (U20) */
    {
        PIN_GPMC0_AD9,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },
            /* EHRPWM1 pin config */
    /* EHRPWM1_A -> GPMC0_AD5 (T20) */
    {
        PIN_GPMC0_AD5,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },
    /* EHRPWM1 pin config */
    /* EHRPWM1_B -> GPMC0_AD6 (T18) */
    {
        PIN_GPMC0_AD6,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },
            /* EHRPWM0 pin config */
    /* EHRPWM0_A -> GPMC0_AD3 (V21) */
    {
        PIN_GPMC0_AD3,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },
    /* EHRPWM0 pin config */
    /* EHRPWM0_B -> GPMC0_AD4 (U21) */
    {
        PIN_GPMC0_AD4,
        ( PIN_MODE(3) | PIN_PULL_DISABLE )
    },

                /* GPIO1_64 -> I2C0_SCL (B16) */
    {
        PIN_I2C0_SCL,
        ( PIN_MODE(7) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
                /* GPIO1_65 -> I2C0_SDA (B15) */
    {
        PIN_I2C0_SDA,
        ( PIN_MODE(7) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
                /* GPIO0_26 -> GPMC0_AD11 (W20) */
    {
        PIN_GPMC0_AD11,
        ( PIN_MODE(7) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
                /* GPIO1_78 -> MMC1_SDWP (C16) */
    {
        PIN_MMC1_SDWP,
        ( PIN_MODE(7) | PIN_PULL_DIRECTION )
    },
                /* GPIO1_77 -> MMC1_SDCD (B17) */
    {
        PIN_MMC1_SDCD,
        ( PIN_MODE(7) | PIN_PULL_DIRECTION )
    },

            /* SPI0 pin config */
    /* SPI0_CLK -> SPI0_CLK (B8) */
    {
        PIN_SPI0_CLK,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* SPI0 pin config */
    /* SPI0_D0 -> SPI0_D0 (A8) */
    {
        PIN_SPI0_D0,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* SPI0 pin config */
    /* SPI0_D1 -> SPI0_D1 (C9) */
    {
        PIN_SPI0_D1,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },

        

            /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPO2 -> PRG0_PRU1_GPO2 (M2) */
    {
        PIN_PRG0_PRU1_GPO2,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPO1 -> PRG0_PRU1_GPO1 (J2) */
    {
        PIN_PRG0_PRU1_GPO1,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPO0 -> PRG0_PRU1_GPO0 (L5) */
    {
        PIN_PRG0_PRU1_GPO0,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPI13 -> PRG0_PRU1_GPO13 (T4) */
    {
        PIN_PRG0_PRU1_GPO13,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPO8 -> PRG0_PRU1_GPO8 (F4) */
    {
        PIN_PRG0_PRU1_GPO8,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPO12 -> PRG0_PRU1_GPO12 (P2) */
    {
        PIN_PRG0_PRU1_GPO12,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPO6 -> PRG0_PRU1_GPO6 (F5) */
    {
        PIN_PRG0_PRU1_GPO6,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU1 pin config */
    /* PRG0_PRU1_GPI11 -> PRG0_PRU1_GPO11 (P1) */
    {
        PIN_PRG0_PRU1_GPO11,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },

            /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI1 -> PRG0_PRU0_GPO1 (J4) */
    {
        PIN_PRG0_PRU0_GPO1,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI11 -> PRG0_PRU0_GPO11 (L1) */
    {
        PIN_PRG0_PRU0_GPO11,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI16 -> PRG0_PRU0_GPO16 (N3) */
    {
        PIN_PRG0_PRU0_GPO16,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI18 -> PRG0_PRU0_GPO18 (K4) */
    {
        PIN_PRG0_PRU0_GPO18,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI3 -> PRG0_PRU0_GPO3 (H1) */
    {
        PIN_PRG0_PRU0_GPO3,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI5 -> PRG0_PRU0_GPO5 (F2) */
    {
        PIN_PRG0_PRU0_GPO5,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI7 -> PRG0_PRU0_GPO7 (E2) */
    {
        PIN_PRG0_PRU0_GPO7,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_PRU0 pin config */
    /* PRG0_PRU0_GPI8 -> PRG0_PRU0_GPO8 (H5) */
    {
        PIN_PRG0_PRU0_GPO8,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },

            /* PRU_ICSSG0_IEP0 pin config */
    /* PRG0_IEP0_EDC_SYNC_OUT0 -> PRG0_PRU0_GPO19 (G2) */
    {
        PIN_PRG0_PRU0_GPO19,
        ( PIN_MODE(2) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG0_IEP0 pin config */
    /* PRG0_IEP0_EDC_SYNC_OUT1 -> PRG0_PRU0_GPO17 (E1) */
    {
        PIN_PRG0_PRU0_GPO17,
        ( PIN_MODE(2) | PIN_PULL_DISABLE )
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


