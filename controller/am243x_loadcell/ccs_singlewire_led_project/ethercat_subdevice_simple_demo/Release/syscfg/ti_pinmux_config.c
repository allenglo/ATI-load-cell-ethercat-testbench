/*
 *  Copyright (C) 2021-2024 Texas Instruments Incorporated
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
            /* I2C0 pin config */
    /* I2C0_SCL -> I2C0_SCL (B16) */
    {
        PIN_I2C0_SCL,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* I2C0 pin config */
    /* I2C0_SDA -> I2C0_SDA (B15) */
    {
        PIN_I2C0_SDA,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },

            /* OSPI0 pin config */
    /* OSPI0_CLK -> OSPI0_CLK (P20) */
    {
        PIN_OSPI0_CLK,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* OSPI0 pin config */
    /* OSPI0_CSn0 -> OSPI0_CSn0 (L20) */
    {
        PIN_OSPI0_CSN0,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* OSPI0 pin config */
    /* OSPI0_D0 -> OSPI0_D0 (L19) */
    {
        PIN_OSPI0_D0,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* OSPI0 pin config */
    /* OSPI0_D1 -> OSPI0_D1 (N20) */
    {
        PIN_OSPI0_D1,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* OSPI0 pin config */
    /* OSPI0_D2 -> OSPI0_D2 (L21) */
    {
        PIN_OSPI0_D2,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* OSPI0 pin config */
    /* OSPI0_D3 -> OSPI0_D3 (N19) */
    {
        PIN_OSPI0_D3,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },

                /* GPIO0_22 -> GPMC0_AD7 (U19) */
    {
        PIN_GPMC0_AD7,
        ( PIN_MODE(7) | PIN_PULL_DISABLE )
    },
                /* GPIO1_55 -> UART0_RTSn (A9) */
    {
        PIN_UART0_RTSN,
        ( PIN_MODE(7) | PIN_PULL_DISABLE )
    },
                /* GPIO0_28 -> GPMC0_AD13 (Y19) */
    {
        PIN_GPMC0_AD13,
        ( PIN_MODE(7) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
                /* GPIO0_20 -> PRG1_PRU1_GPO18 (Y15) */
    {
        PIN_PRG1_PRU1_GPO18,
        ( PIN_MODE(7) | PIN_PULL_DISABLE )
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

            /* SPI0_CS1 pin config */
    /* SPI0_CS1 -> SPI0_CS1 (B7) */
    {
        PIN_SPI0_CS1,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },


            /* USART0 pin config */
    /* UART0_RXD -> UART0_RXD (B10) */
    {
        PIN_UART0_RXD,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* USART0 pin config */
    /* UART0_TXD -> UART0_TXD (B11) */
    {
        PIN_UART0_TXD,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },

            /* PRU_ICSSG1_MDIO0 pin config */
    /* PRG1_MDIO0_MDC -> PRG1_MDIO0_MDC (W1) */
    {
        PIN_PRG1_MDIO0_MDC,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MDIO0 pin config */
    /* PRG1_MDIO0_MDIO -> PRG1_MDIO0_MDIO (V2) */
    {
        PIN_PRG1_MDIO0_MDIO,
        ( PIN_MODE(0) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDC_LATCH_IN0 -> PRG1_PRU0_GPO18 (Y4) */
    {
        PIN_PRG1_PRU0_GPO18,
        ( PIN_MODE(2) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDC_LATCH_IN1 -> PRG1_PRU0_GPO7 (V13) */
    {
        PIN_PRG1_PRU0_GPO7,
        ( PIN_MODE(2) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDC_SYNC_OUT0 -> PRG1_PRU0_GPO19 (U3) */
    {
        PIN_PRG1_PRU0_GPO19,
        ( PIN_MODE(2) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDC_SYNC_OUT1 -> PRG1_PRU0_GPO17 (T2) */
    {
        PIN_PRG1_PRU0_GPO17,
        ( PIN_MODE(2) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDIO_DATA_IN_OUT28 -> PRG1_PRU0_GPO9 (W16) */
    {
        PIN_PRG1_PRU0_GPO9,
        ( PIN_MODE(6) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDIO_DATA_IN_OUT29 -> PRG1_PRU0_GPO10 (W13) */
    {
        PIN_PRG1_PRU0_GPO10,
        ( PIN_MODE(6) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDIO_DATA_IN_OUT30 -> PRG1_PRU1_GPO9 (Y16) */
    {
        PIN_PRG1_PRU1_GPO9,
        ( PIN_MODE(6) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_IEP0 pin config */
    /* PRG1_IEP0_EDIO_DATA_IN_OUT31 -> PRG1_PRU1_GPO10 (U13) */
    {
        PIN_PRG1_PRU1_GPO10,
        ( PIN_MODE(6) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_RXD0 -> PRG1_PRU0_GPO0 (V4) */
    {
        PIN_PRG1_PRU0_GPO0,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_RXD1 -> PRG1_PRU0_GPO1 (W5) */
    {
        PIN_PRG1_PRU0_GPO1,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_RXD2 -> PRG1_PRU0_GPO2 (AA4) */
    {
        PIN_PRG1_PRU0_GPO2,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_RXD3 -> PRG1_PRU0_GPO3 (Y5) */
    {
        PIN_PRG1_PRU0_GPO3,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_RXDV -> PRG1_PRU0_GPO4 (AA5) */
    {
        PIN_PRG1_PRU0_GPO4,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_RXER -> PRG1_PRU0_GPO5 (U14) */
    {
        PIN_PRG1_PRU0_GPO5,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_RXLINK -> PRG1_PRU0_GPO8 (Y13) */
    {
        PIN_PRG1_PRU0_GPO8,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_TXD0 -> PRG1_PRU0_GPO11 (V5) */
    {
        PIN_PRG1_PRU0_GPO11,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_TXD1 -> PRG1_PRU0_GPO12 (W2) */
    {
        PIN_PRG1_PRU0_GPO12,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_TXD2 -> PRG1_PRU0_GPO13 (V6) */
    {
        PIN_PRG1_PRU0_GPO13,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_TXD3 -> PRG1_PRU0_GPO14 (AA7) */
    {
        PIN_PRG1_PRU0_GPO14,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII0_TXEN -> PRG1_PRU0_GPO15 (Y7) */
    {
        PIN_PRG1_PRU0_GPO15,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_RXD0 -> PRG1_PRU1_GPO0 (AA10) */
    {
        PIN_PRG1_PRU1_GPO0,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_RXD1 -> PRG1_PRU1_GPO1 (Y10) */
    {
        PIN_PRG1_PRU1_GPO1,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_RXD2 -> PRG1_PRU1_GPO2 (Y11) */
    {
        PIN_PRG1_PRU1_GPO2,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_RXD3 -> PRG1_PRU1_GPO3 (V12) */
    {
        PIN_PRG1_PRU1_GPO3,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_RXDV -> PRG1_PRU1_GPO4 (Y12) */
    {
        PIN_PRG1_PRU1_GPO4,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_RXER -> PRG1_PRU1_GPO5 (AA11) */
    {
        PIN_PRG1_PRU1_GPO5,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_RXLINK -> PRG1_PRU1_GPO8 (W11) */
    {
        PIN_PRG1_PRU1_GPO8,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_TXD0 -> PRG1_PRU1_GPO11 (Y6) */
    {
        PIN_PRG1_PRU1_GPO11,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_TXD1 -> PRG1_PRU1_GPO12 (AA8) */
    {
        PIN_PRG1_PRU1_GPO12,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_TXD2 -> PRG1_PRU1_GPO13 (Y9) */
    {
        PIN_PRG1_PRU1_GPO13,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_TXD3 -> PRG1_PRU1_GPO14 (W9) */
    {
        PIN_PRG1_PRU1_GPO14,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII1_TXEN -> PRG1_PRU1_GPO15 (V9) */
    {
        PIN_PRG1_PRU1_GPO15,
        ( PIN_MODE(0) | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII_MR0_CLK -> PRG1_PRU0_GPO6 (Y2) */
    {
        PIN_PRG1_PRU0_GPO6,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII_MR1_CLK -> PRG1_PRU1_GPO6 (V10) */
    {
        PIN_PRG1_PRU1_GPO6,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII_MT0_CLK -> PRG1_PRU0_GPO16 (W6) */
    {
        PIN_PRG1_PRU0_GPO16,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
    },
    /* PRU_ICSSG1_MII_G_RT pin config */
    /* PR1_MII_MT1_CLK -> PRG1_PRU1_GPO16 (Y8) */
    {
        PIN_PRG1_PRU1_GPO16,
        ( PIN_MODE(1) | PIN_INPUT_ENABLE | PIN_PULL_DISABLE )
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


