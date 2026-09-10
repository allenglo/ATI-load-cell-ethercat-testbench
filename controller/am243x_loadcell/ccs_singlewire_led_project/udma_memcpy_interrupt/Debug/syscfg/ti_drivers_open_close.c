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

#include "ti_drivers_open_close.h"
#include <kernel/dpl/DebugP.h>

void Drivers_open(void)
{
    Drivers_udmaOpen();
    Drivers_uartOpen();
}

void Drivers_close(void)
{
    Drivers_udmaClose();
    Drivers_uartClose();
}

/*
 * UDMA
 */
/*
 * UDMA BCDMA_0 Blockcopy Parameters
 */
/* UDMA BCDMA_0 Blockcopy Channel Objects */
static Udma_ChObject gConfigUdma0BlkCopyChObj[CONFIG_UDMA0_NUM_BLKCOPY_CH];
/* UDMA CONFIG_UDMA0 Blockcopy Channel Handle */
Udma_ChHandle gConfigUdma0BlkCopyChHandle[CONFIG_UDMA0_NUM_BLKCOPY_CH];

/* UDMA BCDMA_0 Blockcopy Channel Ring Mem Size */
#define UDMA_CONFIG_UDMA0_BLK_COPY_CH_0_RING_MEM_SIZE     (((1U * 8U) + UDMA_CACHELINE_ALIGNMENT) & ~(UDMA_CACHELINE_ALIGNMENT - 1U))

/* UDMA BCDMA_0 Blockcopy Channel Ring Mem */
static uint8_t gConfigUdma0BlkCopyCh0RingMem[UDMA_CONFIG_UDMA0_BLK_COPY_CH_0_RING_MEM_SIZE] __attribute__((aligned(UDMA_CACHELINE_ALIGNMENT)));

/* UDMA BCDMA_0 Blockcopy Channel Ring Memory Pointers - for all channels */
static uint8_t *gConfigUdma0BlkCopyChRingMem[CONFIG_UDMA0_NUM_BLKCOPY_CH] = {
    &gConfigUdma0BlkCopyCh0RingMem[0U],
};
/* UDMA BCDMA_0 Blockcopy Channel Ring Elem Count */
static uint32_t gConfigUdma0BlkCopyChRingElemCnt[CONFIG_UDMA0_NUM_BLKCOPY_CH] = {
    1U,
};
/* UDMA BCDMA_0 Blockcopy Channel Ring Memory Size */
static uint32_t gConfigUdma0BlkCopyChRingMemSize[CONFIG_UDMA0_NUM_BLKCOPY_CH] = {
    UDMA_CONFIG_UDMA0_BLK_COPY_CH_0_RING_MEM_SIZE,
};
/* UDMA BCDMA_0 Blockcopy Channel Event Object */
static Udma_EventObject gConfigUdma0BlkCopyCqEventObj[CONFIG_UDMA0_NUM_BLKCOPY_CH];

/* UDMA BCDMA_0 Blockcopy Channel Event Callback */
static Udma_EventCallback gConfigUdma0BlkCopyCqEventCb[CONFIG_UDMA0_NUM_BLKCOPY_CH] = {
    &App_udmaEventCb,
};
/* UDMA CONFIG_UDMA0 Blockcopy Event Handle */
Udma_EventHandle gConfigUdma0BlkCopyCqEventHandle[CONFIG_UDMA0_NUM_BLKCOPY_CH];

static void Drivers_udmaConfigUdma0BlkCopyOpen(void)
{
    int32_t             retVal = UDMA_SOK;
    uint32_t            chType, chCnt;
    Udma_ChHandle       chHandle;
    Udma_ChPrms         chPrms;
    Udma_ChTxPrms       txPrms;
    Udma_ChRxPrms       rxPrms;
    Udma_DrvHandle      drvHandle = &gUdmaDrvObj[CONFIG_UDMA0];
    Udma_EventPrms      cqEventPrms;
    Udma_EventHandle    cqEventHandle;

    for(chCnt = 0U; chCnt < CONFIG_UDMA0_NUM_BLKCOPY_CH; chCnt++)
    {
        chHandle = &gConfigUdma0BlkCopyChObj[chCnt];
        gConfigUdma0BlkCopyChHandle[chCnt] = chHandle;

        /* Init channel parameters */
        chType = UDMA_CH_TYPE_TR_BLK_COPY;
        UdmaChPrms_init(&chPrms, chType);
        chPrms.fqRingPrms.ringMem       = gConfigUdma0BlkCopyChRingMem[chCnt];
        chPrms.fqRingPrms.ringMemSize   = gConfigUdma0BlkCopyChRingMemSize[chCnt];
        chPrms.fqRingPrms.elemCnt       = gConfigUdma0BlkCopyChRingElemCnt[chCnt];

        /* Open channel for block copy */
        retVal = Udma_chOpen(drvHandle, chHandle, chType, &chPrms);
        DebugP_assert(UDMA_SOK == retVal);

        /* Config TX channel */
        UdmaChTxPrms_init(&txPrms, chType);
        retVal = Udma_chConfigTx(chHandle, &txPrms);
        DebugP_assert(UDMA_SOK == retVal);

        /* Config RX channel - which is implicitly paired to TX channel in
         * block copy mode */
        UdmaChRxPrms_init(&rxPrms, chType);
        retVal = Udma_chConfigRx(chHandle, &rxPrms);
        DebugP_assert(UDMA_SOK == retVal);

        /* Register completion event */
        if(NULL != gConfigUdma0BlkCopyCqEventCb[chCnt])
        {
            cqEventHandle = &gConfigUdma0BlkCopyCqEventObj[chCnt];
            gConfigUdma0BlkCopyCqEventHandle[chCnt] = cqEventHandle;
            UdmaEventPrms_init(&cqEventPrms);
            cqEventPrms.eventType         = UDMA_EVENT_TYPE_DMA_COMPLETION;
            cqEventPrms.eventMode         = UDMA_EVENT_MODE_SHARED;
            cqEventPrms.chHandle          = chHandle;
            cqEventPrms.controllerEventHandle = Udma_eventGetGlobalHandle(drvHandle);
            cqEventPrms.eventCb           = gConfigUdma0BlkCopyCqEventCb[chCnt];
            retVal = Udma_eventRegister(drvHandle, cqEventHandle, &cqEventPrms);
            DebugP_assert(UDMA_SOK == retVal);
        }
    }

    return;
}

static void Drivers_udmaConfigUdma0BlkCopyClose(void)
{
    int32_t         retVal, tempRetVal;
    uint32_t        chCnt;
    Udma_ChHandle   chHandle;
    uint64_t        pDesc;

    for(chCnt = 0U; chCnt < CONFIG_UDMA0_NUM_BLKCOPY_CH; chCnt++)
    {
        chHandle = &gConfigUdma0BlkCopyChObj[chCnt];

        /* Flush any pending request from the free queue */
        while(1)
        {
            tempRetVal = Udma_ringFlushRaw(
                             Udma_chGetFqRingHandle(chHandle), &pDesc);
            if(UDMA_ETIMEOUT == tempRetVal)
            {
                break;
            }
        }

        /* Unregister completion event */
        if(NULL != gConfigUdma0BlkCopyCqEventHandle[chCnt])
        {
            retVal = Udma_eventUnRegister(gConfigUdma0BlkCopyCqEventHandle[chCnt]);
            DebugP_assert(UDMA_SOK == retVal);
            gConfigUdma0BlkCopyCqEventHandle[chCnt] = NULL;
        }

        /* Close channel */
        retVal = Udma_chClose(chHandle);
        DebugP_assert(UDMA_SOK == retVal);
    }

    return;
}

void Drivers_udmaOpen(void)
{
    Drivers_udmaConfigUdma0BlkCopyOpen();
}

void Drivers_udmaClose(void)
{
    Drivers_udmaConfigUdma0BlkCopyClose();
}


/*
 * UART
 */

/* UART Driver handles */
UART_Handle gUartHandle[CONFIG_UART_NUM_INSTANCES];

#include <drivers/uart/v0/lld/dma/uart_dma.h>
#include <kernel/dpl/ClockP.h>

UART_DmaChConfig gUartDmaChConfig[CONFIG_UART_NUM_INSTANCES] =
{
                NULL,
};

/* UART Driver Parameters */
UART_Params gUartParams[CONFIG_UART_NUM_INSTANCES] =
{
        {
            .baudRate           = 115200,
            .dataLength         = UART_LEN_8,
            .stopBits           = UART_STOPBITS_1,
            .parityType         = UART_PARITY_NONE,
            .readMode           = UART_TRANSFER_MODE_BLOCKING,
            .readReturnMode     = UART_READ_RETURN_MODE_FULL,
            .writeMode          = UART_TRANSFER_MODE_BLOCKING,
            .readCallbackFxn    = NULL,
            .writeCallbackFxn   = NULL,
            .hwFlowControl      = FALSE,
            .hwFlowControlThr   = UART_RXTRIGLVL_16,
            .transferMode       = UART_CONFIG_MODE_INTERRUPT,
            .skipIntrReg         = FALSE,
            .uartDmaIndex = -1,
            .intrNum            = 210U,
            .intrPriority       = 4U,
            .operMode           = UART_OPER_MODE_16X,
            .rxTrigLvl          = UART_RXTRIGLVL_8,
            .txTrigLvl          = UART_TXTRIGLVL_32,
            .rxEvtNum           = 0U,
            .txEvtNum           = 0U,
        },
};

void Drivers_uartOpen(void)
{
    uint32_t instCnt;
    int32_t  status = SystemP_SUCCESS;

    for(instCnt = 0U; instCnt < CONFIG_UART_NUM_INSTANCES; instCnt++)
    {
        gUartHandle[instCnt] = NULL;   /* Init to NULL so that we can exit gracefully */
    }

    /* Open all instances */
    for(instCnt = 0U; instCnt < CONFIG_UART_NUM_INSTANCES; instCnt++)
    {
        gUartHandle[instCnt] = UART_open(instCnt, &gUartParams[instCnt]);
        if(NULL == gUartHandle[instCnt])
        {
            DebugP_logError("UART open failed for instance %d !!!\r\n", instCnt);
            status = SystemP_FAILURE;
            break;
        }
    }

    if(SystemP_FAILURE == status)
    {
        Drivers_uartClose();   /* Exit gracefully */
    }

    return;
}

void Drivers_uartClose(void)
{
    uint32_t instCnt;

    /* Close all instances that are open */
    for(instCnt = 0U; instCnt < CONFIG_UART_NUM_INSTANCES; instCnt++)
    {
        if(gUartHandle[instCnt] != NULL)
        {
            UART_close(gUartHandle[instCnt]);
            gUartHandle[instCnt] = NULL;
        }
    }

    return;
}

