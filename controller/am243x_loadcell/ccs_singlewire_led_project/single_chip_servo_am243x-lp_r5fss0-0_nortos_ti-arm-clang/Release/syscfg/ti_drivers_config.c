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
#include <drivers/sciclient.h>

/*
 * GPIO
 */

/* ----------- GPIO Direction, Trigger, Interrupt initialization ----------- */

void GPIO_init()
{
    uint32_t    baseAddr;

    /* Instance 0 */
    /* Get address after translation translate */
    baseAddr = (uint32_t) AddrTranslateP_getLocalAddr(MTR_1_PWM_EN_BASE_ADDR);
    GPIO_pinWriteLow(baseAddr, MTR_1_PWM_EN_PIN);

    GPIO_setDirMode(baseAddr, MTR_1_PWM_EN_PIN, MTR_1_PWM_EN_DIR);
    /* Instance 1 */
    /* Get address after translation translate */
    baseAddr = (uint32_t) AddrTranslateP_getLocalAddr(MTR_2_PWM_EN_BASE_ADDR);
    GPIO_pinWriteLow(baseAddr, MTR_2_PWM_EN_PIN);

    GPIO_setDirMode(baseAddr, MTR_2_PWM_EN_PIN, MTR_2_PWM_EN_DIR);
    /* Instance 2 */
    /* Get address after translation translate */
    baseAddr = (uint32_t) AddrTranslateP_getLocalAddr(BP_MUX_SEL_BASE_ADDR);
    GPIO_pinWriteLow(baseAddr, BP_MUX_SEL_PIN);

    GPIO_setDirMode(baseAddr, BP_MUX_SEL_PIN, BP_MUX_SEL_DIR);
    /* Instance 3 */
    /* Get address after translation translate */
    baseAddr = (uint32_t) AddrTranslateP_getLocalAddr(ENC1_EN_BASE_ADDR);
    GPIO_pinWriteLow(baseAddr, ENC1_EN_PIN);

    GPIO_setDirMode(baseAddr, ENC1_EN_PIN, ENC1_EN_DIR);
    /* Instance 4 */
    /* Get address after translation translate */
    baseAddr = (uint32_t) AddrTranslateP_getLocalAddr(ENC2_EN_BASE_ADDR);
    GPIO_pinWriteLow(baseAddr, ENC2_EN_PIN);

    GPIO_setDirMode(baseAddr, ENC2_EN_PIN, ENC2_EN_DIR);
}


/* ----------- GPIO Interrupt de-initialization ----------- */
void GPIO_deinit()
{

}

/*
 * IPC Notify
 */
#include <drivers/ipc_notify.h>
#include <drivers/ipc_notify/v0/ipc_notify_v0.h>


/* This function is called within IpcNotify_init, this function returns core specific IPC config */
void IpcNotify_getConfig(IpcNotify_InterruptConfig **interruptConfig, uint32_t *interruptConfigNum)
{
    /* extern globals that are specific to this core */
    extern IpcNotify_InterruptConfig gIpcNotifyInterruptConfig_r5fss0_0[];
    extern uint32_t gIpcNotifyInterruptConfigNum_r5fss0_0;

    *interruptConfig = &gIpcNotifyInterruptConfig_r5fss0_0[0];
    *interruptConfigNum = gIpcNotifyInterruptConfigNum_r5fss0_0;
}


/*
 * MCSPI
 */

#include "ti_drivers_open_close.h"

uint32_t gMcspiNumCh[1] =
{
    CONFIG_MCSPI0_NUM_CH,
};

/* MCSPI atrributes */
static MCSPI_Attrs gMcspiAttrs[CONFIG_MCSPI_NUM_INSTANCES] =
{
    {
        .baseAddr           = CSL_MCSPI0_CFG_BASE,
        .inputClkFreq       = 50000000U,
        .intrNum            = 204,
        .operMode           = MCSPI_OPER_MODE_POLLED,
        .intrPriority       = 4U,
        .chMode             = MCSPI_CH_MODE_SINGLE,
        .pinMode            = MCSPI_PINMODE_3PIN,
        .initDelay          = MCSPI_INITDLY_0,
        .multiWordAccess    = FALSE,

    },
};
/* MCSPI objects - initialized by the driver */
static MCSPI_Object gMcspiObjects[CONFIG_MCSPI_NUM_INSTANCES];
/* MCSPI driver configuration */
MCSPI_Config gMcspiConfig[CONFIG_MCSPI_NUM_INSTANCES] =
{
    {
        &gMcspiAttrs[CONFIG_MCSPI0],
        &gMcspiObjects[CONFIG_MCSPI0],
    },
};

uint32_t gMcspiConfigNum = CONFIG_MCSPI_NUM_INSTANCES;

#include <drivers/mcspi/v0/lld/dma/mcspi_dma.h>
MCSPI_DmaConfig gMcspiDmaConfig =
{
    .fxns        = NULL,
    .mcspiDmaArgs = (void *)NULL,
};

MCSPI_DmaHandle gMcspiDmaHandle[0] =
{
};


uint32_t gMcspiDmaConfigNum = CONFIG_MCSPI_NUM_DMA_INSTANCES;

/*
 * UDMA
 */
/* UDMA driver instance object */
Udma_DrvObject          gUdmaDrvObj[CONFIG_UDMA_NUM_INSTANCES];
/* UDMA driver instance init params */
static Udma_InitPrms    gUdmaInitPrms[CONFIG_UDMA_NUM_INSTANCES] =
{
    {
        .instId             = UDMA_INST_ID_PKTDMA_0,
        .skipGlobalEventReg = FALSE,
        .virtToPhyFxn       = Udma_defaultVirtToPhyFxn,
        .phyToVirtFxn       = Udma_defaultPhyToVirtFxn,
    },
};

/*
 * PRUICSS
 */
/* PRUICSS HW attributes - provided by the driver */
extern PRUICSS_HwAttrs gPruIcssHwAttrs_ICSSG0;

/* PRUICSS objects - initialized by the driver */
static PRUICSS_Object gPruIcssObjects[CONFIG_PRUICSS_NUM_INSTANCES];
/* PRUICSS driver configuration */
PRUICSS_Config gPruIcssConfig[CONFIG_PRUICSS_NUM_INSTANCES] =
{
    {
        .object = &gPruIcssObjects[CONFIG_PRU_ICSS0],
        .hwAttrs = &gPruIcssHwAttrs_ICSSG0
    },
};

uint32_t gPruIcssConfigNum = CONFIG_PRUICSS_NUM_INSTANCES;

/*
 * PRU_IPC
 */
/* Shared Memory Buffers */
#define PRU_IPC_1_BUF_MEM_SIZE (128)
uint32_t gPruIpc1BufMem1[PRU_IPC_1_BUF_MEM_SIZE] __attribute__((aligned(4), section(".bss.pru_ipc_1buf_mem1")));
/* Shared Memory Array of Buffers */
uint32_t PruIpc_bufferAddrs1[1] = {
            (uint32_t) gPruIpc1BufMem1,
};

/*
    // Sample Reference code for Linker:
    // Transfer this code to Linker file as required.

SECTIONS
{
    // Buffer memory used by PRU_IPC
    .bss.pru_ipc_1buf_mem1 (NOLOAD): {} > PRU_IPC_BUF_MEM
}

MEMORY
{
    // shared memory segments
    // - make sure there is an MPU entry which maps below regions as non-cache
    // shared memory that is used between ICCS and this core. MARK as cache+sharable
    // make sure the LENGTH fits in the specified memory
    // ORIGIN is the start address of the memory you want to use as shared memory. 0x78000040 = TCM
    PRU_IPC_BUF_MEM         : ORIGIN = 0x78000040, LENGTH = 0x200
}

*/

/* PRU_IPC objects - initialized by the driver */
static PRU_IPC_Object gPruIpcObjects[CONFIG_PRU_IPC_NUM_INSTANCES];
/* PRU_IPC Attrs - initialized by sysconfig */
static PRU_IPC_Attrs  gPruIpcAttrs[CONFIG_PRU_IPC_NUM_INSTANCES] =
{
    {
        .dataSize      = 4,
        .blockSize     = 32,
        .noOfBlocks    = 4,
        .noOfBuffers   = 1,
        .bufferAddrs   = PruIpc_bufferAddrs1,
        .config        = (Config_Mem_Struct *)(CSL_PRU_ICSSG0_DRAM0_SLV_RAM_BASE + 0),
        .pruEvtoutNum  = ICSS_INTC_HOST_INTR_2 - ICSS_INTC_HOST_INTR_2,
        .sysEventNum   = ICSS_INTC_EVENT_16,
        .r5fIntrNum    = 120 + ICSS_INTC_HOST_INTR_2 - ICSS_INTC_HOST_INTR_2,
        .blockSizeBytes = 128,
        .enableRxInt   = 1,
        .enableTxInt   = 0,
    },
};

/* PruIpc driver configuration */
PRU_IPC_Config gPruIpcConfig[CONFIG_PRU_IPC_NUM_INSTANCES] =
{
    {
        .attrs  = &gPruIpcAttrs[0],
        .object = &gPruIpcObjects[0],
    },
};

uint32_t gPruIpcConfigNum = CONFIG_PRU_IPC_NUM_INSTANCES;

/*
 *  ICSSG0_INTC
 */
PRUICSS_IntcInitData icss0_intc_initdata =
{
    {
        ICSS_INTC_EVENT_16,
        0xFF
    },
    {
        {
            ICSS_INTC_EVENT_16,
            ICSS_INTC_CHANNEL_2,
            SYS_EVT_POLARITY_HIGH,
            SYS_EVT_TYPE_PULSE,
        },
        {0xFF, 0xFF, 0xFF, 0xFF}
    },
    {
        {
            ICSS_INTC_CHANNEL_2,
            ICSS_INTC_HOST_INTR_2
        },
        {0xFF, 0xFF}
    },
    (
        ICSS_INTC_HOST_INTR_2_HOSTEN_MASK
    )
};


void Pinmux_init(void);
void PowerClock_init(void);
void PowerClock_deinit(void);

/*
 * Common Functions
 */
void System_init(void)
{
    /* DPL init sets up address transalation unit, on some CPUs this is needed
     * to access SCICLIENT services, hence this needs to happen first
     */
    Dpl_init();
    /* We should do sciclient init before we enable power and clock to the peripherals */
    /* SCICLIENT init */
    {
        int32_t retVal = SystemP_SUCCESS;

        retVal = Sciclient_init(CSL_CORE_ID_R5FSS0_0);
        DebugP_assertNoLog(SystemP_SUCCESS == retVal);
    }

    
    /* initialize PMU */
    CycleCounterP_init(SOC_getSelfCpuClk());


    PowerClock_init();
    /* Now we can do pinmux */
    Pinmux_init();
    /* finally we initialize all peripheral drivers */
    /* EPWM */
    {
        /* Enable time base clock for the selected ePWM */
       SOC_setEpwmTbClk(2, TRUE);
       SOC_setEpwmTbClk(1, TRUE);
       SOC_setEpwmTbClk(0, TRUE);
    }
    GPIO_init();
    /* IPC Notify */
    {
        IpcNotify_Params notifyParams;
        int32_t status;

        /* initialize parameters to default */
        IpcNotify_Params_init(&notifyParams);

        /* specify the priority of IPC Notify interrupt */
        notifyParams.intrPriority = 15U;

        /* specify the core on which this API is called */
        notifyParams.selfCoreId = CSL_CORE_ID_R5FSS0_0;

        /* list the cores that will do IPC Notify with this core
        * Make sure to NOT list 'self' core in the list below
        */
        notifyParams.numCores = 3;
        notifyParams.coreIdList[0] = CSL_CORE_ID_R5FSS0_1;
        notifyParams.coreIdList[1] = CSL_CORE_ID_R5FSS1_0;
        notifyParams.coreIdList[2] = CSL_CORE_ID_M4FSS0_0;

        notifyParams.isMailboxIpcEnabled = 0;

        notifyParams.isCrcEnabled = 0;

        /* initialize the IPC Notify module */
        status = IpcNotify_init(&notifyParams);
        DebugP_assert(status==SystemP_SUCCESS);

    }

    MCSPI_init();
    /* UDMA */
    {
        uint32_t        instId;
        int32_t         retVal = UDMA_SOK;

        for(instId = 0U; instId < CONFIG_UDMA_NUM_INSTANCES; instId++)
        {
            retVal += Udma_init(&gUdmaDrvObj[instId], &gUdmaInitPrms[instId]);
            DebugP_assert(UDMA_SOK == retVal);
        }
    }
    PRUICSS_init();

}

void System_deinit(void)
{
    /* EPWM */
    {
        /* Disable time base clock for the selected ePWM */
      SOC_setEpwmTbClk(2, FALSE);			 
	
      SOC_setEpwmTbClk(1, FALSE);			 
	
      SOC_setEpwmTbClk(0, FALSE);			 
	
    }
    GPIO_deinit();
    IpcNotify_deInit();

    MCSPI_deinit();
    /* UDMA */
    {
        uint32_t        instId;
        int32_t         retVal = UDMA_SOK;

        for(instId = 0U; instId < CONFIG_UDMA_NUM_INSTANCES; instId++)
        {
            retVal += Udma_deinit(&gUdmaDrvObj[instId]);
            DebugP_assert(UDMA_SOK == retVal);
        }
    }
    PRUICSS_deinit();
    PowerClock_deinit();
    /* SCICLIENT deinit */
    {
        int32_t         retVal = SystemP_SUCCESS;

        retVal = Sciclient_deinit();
        DebugP_assertNoLog(SystemP_SUCCESS == retVal);
    }
    Dpl_deinit();
}
