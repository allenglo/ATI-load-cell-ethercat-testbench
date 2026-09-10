/*
 * SOEM nicdrv implementation for AM243x CPSW
 *
 * Maps SOEM raw EtherCAT frame I/O to TI EnetDma Tx/Rx using the same
 * API as the enet_l2_cpsw example (EnetDma_submitTxPktQ /
 * EnetDma_retrieveRxPktQ).
 *
 * Architecture:
 *   - Single DMA Tx channel (ENET_DMA_TX_CH0)
 *   - Single DMA Rx flow   (ENET_DMA_RX_CH0)
 *   - No redundancy (one MAC port)
 *   - EtherCAT EtherType = 0x88A4
 *   - SOEM buffer index stored in bytes [4:5] of source MAC (standard trick)
 */

#include "nicdrv.h"
#include "oshw.h"
#include "osal.h"

/* TI SDK headers */
#include <networking/enet/core/include/enet.h>
#include <networking/enet/core/include/core/enet_dma.h>
#include <networking/enet/core/utils/include/enet_apputils.h>
#include <networking/enet/core/utils/include/enet_appmemutils.h>
#include <networking/enet/core/utils/include/enet_appmemutils_cfg.h>
#include <networking/enet/core/src/dma/udma/enet_udma_memcfg.h>
#include <ti_enet_config.h>
#include <ti_enet_open_close.h>

#include <kernel/dpl/ClockP.h>
#include <kernel/dpl/SemaphoreP.h>
#include <kernel/dpl/DebugP.h>
#include <string.h>

static uint32_t g_txCount = 0U;
static uint32_t g_rxCount = 0U;
static uint32_t g_rxTimeoutCount = 0U;
static bool g_driverInited = false;

/* -----------------------------------------------------------------------
 * Constants
 * ----------------------------------------------------------------------- */
#define ECAT_ETHERTYPE          (0x88A4U)
#define ECAT_HDR_LEN            (14U)       /* dst(6) + src(6) + type(2) */
#define ECAT_MAX_FRAME          (1518U)

/* Primary source MAC – SOEM standard, not the real NIC MAC */
static const uint8_t g_srcMac[6] = {0x01,0x01,0x05,0x01,0x00,0x00};
/* Broadcast destination for EtherCAT */
static const uint8_t g_dstMac[6] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};

const uint16 priMAC[3] = {0x0101, 0x0101, 0x0101};
const uint16 secMAC[3] = {0x0404, 0x0404, 0x0404};

void ec_setupheader(void *p)
{
    uint8_t *bp = (uint8_t *)p;
    memcpy(bp, g_dstMac, 6);
    memcpy(bp + 6, g_srcMac, 6);
    bp[12] = 0x88;
    bp[13] = 0xA4;
}

/* -----------------------------------------------------------------------
 * Module-level state
 * ----------------------------------------------------------------------- */
typedef struct
{
    EnetDma_TxChHandle  hTxCh;
    EnetDma_RxChHandle  hRxCh;
    uint32_t            txChNum;
    uint32_t            rxFlowIdx;
    uint32_t            rxStartFlowIdx;
    uint8_t             macAddr[6];
    SemaphoreP_Object   rxSem;          /* posted by ISR */
    Enet_Handle         hEnet;
    uint32_t            coreKey;
    EnetDma_PktQ        txFreePktInfoQ;
} Am243xEnetCtx;

static Am243xEnetCtx g_enetCtx;
static bool          g_enetReady = false;

static void ecx_init_tx_free_q(void)
{
    EnetDma_Pkt *pPktInfo;
    uint32_t i;
    uint32_t scatterSegments[] = {ENET_MEM_LARGE_POOL_PKT_SIZE};

    EnetQueue_initQ(&g_enetCtx.txFreePktInfoQ);
    for (i = 0U; i < ENET_SYSCFG_TOTAL_NUM_TX_PKT; i++)
    {
        pPktInfo = EnetMem_allocEthPkt(&g_enetCtx,
                                       ENETDMA_CACHELINE_ALIGNMENT,
                                       ENET_ARRAYSIZE(scatterSegments),
                                       scatterSegments);
        EnetAppUtils_assert(pPktInfo != NULL);
        ENET_UTILS_SET_PKT_APP_STATE(&pPktInfo->pktState, ENET_PKTSTATE_APP_WITH_FREEQ);
        EnetQueue_enq(&g_enetCtx.txFreePktInfoQ, &pPktInfo->node);
    }
}

static void ecx_init_rx_ready_q(EnetDma_RxChHandle hRxCh)
{
    EnetDma_PktQ rxReadyQ;
    EnetDma_PktQ rxFreeQ;
    EnetDma_Pkt *pPktInfo;
    uint32_t i;
    int32_t status;
    uint32_t scatterSegments[] = {
        ENET_MEM_LARGE_POOL_PKT_SIZE / 4,
        ENET_MEM_LARGE_POOL_PKT_SIZE / 4,
        ENET_MEM_LARGE_POOL_PKT_SIZE / 4,
        ENET_MEM_LARGE_POOL_PKT_SIZE / 4,
    };

    EnetQueue_initQ(&rxFreeQ);
    for (i = 0U; i < ENET_SYSCFG_TOTAL_NUM_RX_PKT; i++)
    {
        pPktInfo = EnetMem_allocEthPkt(&g_enetCtx,
                                       ENETDMA_CACHELINE_ALIGNMENT,
                                       ENET_ARRAYSIZE(scatterSegments),
                                       scatterSegments);
        EnetAppUtils_assert(pPktInfo != NULL);
        ENET_UTILS_SET_PKT_APP_STATE(&pPktInfo->pktState, ENET_PKTSTATE_APP_WITH_FREEQ);
        EnetQueue_enq(&rxFreeQ, &pPktInfo->node);
    }

    EnetQueue_initQ(&rxReadyQ);
    status = EnetDma_retrieveRxPktQ(hRxCh, &rxReadyQ);
    EnetAppUtils_assert(status == ENET_SOK);
    EnetAppUtils_assert(EnetQueue_getQCount(&rxReadyQ) == 0U);

    EnetAppUtils_validatePacketState(&rxFreeQ,
                                     ENET_PKTSTATE_APP_WITH_FREEQ,
                                     ENET_PKTSTATE_APP_WITH_DRIVER);
    EnetDma_submitRxPktQ(hRxCh, &rxFreeQ);
}

/* -----------------------------------------------------------------------
 * Rx ISR callback – just posts the semaphore
 * ----------------------------------------------------------------------- */
static void ecx_rx_isr(void *arg)
{
    (void)arg;
    SemaphoreP_post(&g_enetCtx.rxSem);
}

/* -----------------------------------------------------------------------
 * Open / close
 * ----------------------------------------------------------------------- */
int ecx_setupnic(ecx_portt *port, const char *ifname, int secondary)
{
    int32_t status;
    EnetApp_HandleInfo      handleInfo;
    EnetPer_AttachCoreOutArgs attachOut;
    EnetApp_GetDmaHandleInArgs txIn, rxIn;
    EnetApp_GetTxDmaHandleOutArgs txOut;
    EnetApp_GetRxDmaHandleOutArgs rxOut;

    (void)ifname;
    (void)secondary;

    memset(&g_enetCtx, 0, sizeof(g_enetCtx));

    /* Initialise CPSW driver (syscfg-generated) */
    if (!g_driverInited)
    {
        EnetApp_driverInit();
        g_driverInited = true;
    }

    /*
     * Enable CPSW peripheral clocks via TISCI before opening.
     * The L2-CPSW example always calls EnetAppUtils_enableClocks before
     * EnetApp_driverOpen; without this the PKTDMA channel open fails because
     * the CPSW CPPI / RGMII clocks are not set at the required frequencies.
     */
    EnetAppUtils_enableClocks(ENET_CPSW_3G, 0U);

    status = EnetApp_driverOpen(ENET_CPSW_3G, 0U);
    if (status != ENET_SOK) { return 0; }

    EnetApp_acquireHandleInfo(ENET_CPSW_3G, 0U, &handleInfo);
    g_enetCtx.hEnet = handleInfo.hEnet;

    EnetApp_coreAttach(ENET_CPSW_3G, 0U, EnetSoc_getCoreId(), &attachOut);
    g_enetCtx.coreKey = attachOut.coreKey;

    /* Tx channel */
    txIn.cbArg    = NULL;
    txIn.notifyCb = NULL;
    EnetApp_getTxDmaHandle(ENET_DMA_TX_CH0, &txIn, &txOut);
    g_enetCtx.hTxCh   = txOut.hTxCh;
    g_enetCtx.txChNum = txOut.txChNum;
    if (!g_enetCtx.hTxCh) { return 0; }

    /* Pre-populate Tx free queue */
    ecx_init_tx_free_q();

    /* Rx flow */
    SemaphoreP_constructBinary(&g_enetCtx.rxSem, 0U);
    rxIn.notifyCb = ecx_rx_isr;
    rxIn.cbArg    = NULL;
    EnetApp_getRxDmaHandle(ENET_DMA_RX_CH0, &rxIn, &rxOut);
    g_enetCtx.hRxCh          = rxOut.hRxCh;
    g_enetCtx.rxFlowIdx       = rxOut.rxFlowIdx;
    g_enetCtx.rxStartFlowIdx  = rxOut.rxFlowStartIdx;
    EnetUtils_copyMacAddr(g_enetCtx.macAddr,
                          rxOut.macAddr[rxOut.numValidMacAddress - 1]);
    if (!g_enetCtx.hRxCh) { return 0; }

    ecx_init_rx_ready_q(g_enetCtx.hRxCh);

    /* Initialise SOEM port struct */
    memset(port->rxbufstat, EC_BUF_EMPTY, sizeof(port->rxbufstat));
    port->stack.sock          = NULL;   /* unused – we use EnetDma directly */
    port->stack.txbuf         = &(port->txbuf);
    port->stack.txbuflength   = &(port->txbuflength);
    port->stack.rxbuf         = &(port->rxbuf);
    port->stack.rxbufstat     = &(port->rxbufstat);
    port->stack.rxsa          = &(port->rxsa);

    g_enetReady = true;
    return 1;
}

int ecx_closenic(ecx_portt *port)
{
    (void)port;
    if (!g_enetReady)
    {
        return 1;
    }

    /* Close Rx/Tx DMA – basic teardown */
    EnetDma_PktQ fq, cq;
    EnetQueue_initQ(&fq);
    EnetQueue_initQ(&cq);
    EnetApp_closeRxDma(ENET_DMA_RX_CH0, g_enetCtx.hEnet,
                       g_enetCtx.coreKey, EnetSoc_getCoreId(), &fq, &cq);
    EnetAppUtils_freePktInfoQ(&fq);
    EnetAppUtils_freePktInfoQ(&cq);

    EnetQueue_initQ(&fq);
    EnetQueue_initQ(&cq);
    EnetApp_closeTxDma(ENET_DMA_TX_CH0, g_enetCtx.hEnet,
                       g_enetCtx.coreKey, EnetSoc_getCoreId(), &fq, &cq);
    EnetAppUtils_freePktInfoQ(&fq);
    EnetAppUtils_freePktInfoQ(&cq);

    EnetAppUtils_freePktInfoQ(&g_enetCtx.txFreePktInfoQ);

    /* Detach/release/driver deinit to avoid stale CPSW/UDMA state */
    EnetApp_coreDetach(ENET_CPSW_3G, 0U, EnetSoc_getCoreId(), g_enetCtx.coreKey);
    EnetApp_releaseHandleInfo(ENET_CPSW_3G, 0U);
    if (g_driverInited)
    {
        EnetApp_driverDeInit();
        g_driverInited = false;
    }

    SemaphoreP_destruct(&g_enetCtx.rxSem);
    memset(&g_enetCtx, 0, sizeof(g_enetCtx));
    g_enetReady = false;
    return 1;
}

/* -----------------------------------------------------------------------
 * Transmit
 * Copies the SOEM tx buffer (already fully built by ec_setupdatagram) into
 * a free DMA packet and submits it.
 * ----------------------------------------------------------------------- */
int ecx_outframe(ecx_portt *port, uint8 idx, int stacknumber)
{
    EnetDma_PktQ    txQ;
    EnetDma_Pkt    *pkt;
    uint8_t        *buf;
    uint16_t        len;

    (void)stacknumber;

    /* Retrieve any completed Tx descriptors back to free pool */
    {
        EnetDma_PktQ freeQ;
        EnetQueue_initQ(&freeQ);
        EnetDma_retrieveTxPktQ(g_enetCtx.hTxCh, &freeQ);
        EnetDma_Pkt *fp = (EnetDma_Pkt *)EnetQueue_deq(&freeQ);
        while (fp)
        {
            ENET_UTILS_SET_PKT_APP_STATE(&fp->pktState, ENET_PKTSTATE_APP_WITH_FREEQ);
            EnetQueue_enq(&g_enetCtx.txFreePktInfoQ, &fp->node);
            fp = (EnetDma_Pkt *)EnetQueue_deq(&freeQ);
        }
    }

    pkt = (EnetDma_Pkt *)EnetQueue_deq(&g_enetCtx.txFreePktInfoQ);
    if (!pkt) { return -1; }

    buf = (uint8_t *)pkt->sgList.list[0].bufPtr;
    len = (uint16_t)port->txbuflength[idx];

    /* Copy pre-built SOEM frame (already has EtherCAT header + datagrams) */
    memcpy(buf, &(port->txbuf[idx][0]), len);

    /* Overwrite Ethernet src MAC bytes [4:5] with SOEM buffer index so
     * ecx_inframe() can match the response to this slot */
    buf[10] = (uint8_t)(idx >> 8);
    buf[11] = (uint8_t)(idx & 0xFF);

    pkt->sgList.list[0].segmentFilledLen = len;
    pkt->sgList.numScatterSegments       = 1U;
    ENET_UTILS_SET_PKT_APP_STATE(&pkt->pktState, ENET_PKTSTATE_APP_WITH_DRIVER);

    EnetQueue_initQ(&txQ);
    EnetQueue_enq(&txQ, &pkt->node);
    EnetDma_submitTxPktQ(g_enetCtx.hTxCh, &txQ);

    port->rxbufstat[idx] = EC_BUF_TX;
    g_txCount++;
    if (g_txCount <= 5U)
    {
        DebugP_log("[NIC] TX idx=%d len=%d count=%u\r\n", (int)idx, (int)len, g_txCount);
    }
    return len;
}

int ecx_outframe_red(ecx_portt *port, uint8 idx)
{
    return ecx_outframe(port, idx, 0);
}

/* -----------------------------------------------------------------------
 * Receive
 * Drains the CPSW Rx queue and copies matching frames into SOEM rx buffers.
 * ----------------------------------------------------------------------- */
int ecx_inframe(ecx_portt *port, int stacknumber, int timeout)
{
    EnetDma_PktQ  rxReadyQ;
    EnetDma_PktQ  rxFreeQ;
    EnetDma_Pkt  *pkt;
    uint8_t      *buf;
    uint16_t      etherType;
    int           idx;
    int           found = -1;
    ec_timet      deadline;

    (void)stacknumber;

    {
        ec_timet tdelta = osal_usec_to_timet((uint64_t)timeout);
        ec_timet tnow;
        osal_get_monotonic_time(&tnow);
        osal_timespecadd(&tnow, &tdelta, &deadline);
    }

    do
    {
        /* Compute remaining wait in ms for semaphore pend */
        ec_timet tnow;
        osal_get_monotonic_time(&tnow);
        uint32_t pendMs = 0U;
        if (osal_timespeccmp(&tnow, &deadline, <))
        {
            ec_timet remain;
            osal_timespecsub(&deadline, &tnow, &remain);
            uint64_t remUsec = (uint64_t)(remain.tv_sec * 1000000LL
                                         + remain.tv_nsec / 1000LL);
            pendMs = (uint32_t)(remUsec / 1000U) + 1U;
        }
        SemaphoreP_pend(&g_enetCtx.rxSem,
                        pendMs == 0U ? SystemP_NO_WAIT : pendMs);

        EnetQueue_initQ(&rxReadyQ);
        EnetQueue_initQ(&rxFreeQ);

        EnetDma_retrieveRxPktQ(g_enetCtx.hRxCh, &rxReadyQ);

        pkt = (EnetDma_Pkt *)EnetQueue_deq(&rxReadyQ);
        while (pkt)
        {
            buf       = (uint8_t *)pkt->sgList.list[0].bufPtr;
            etherType = (uint16_t)((buf[12] << 8) | buf[13]);

            if (etherType == ECAT_ETHERTYPE)
            {
                /* Extract SOEM buffer index from src MAC bytes [4:5] */
                idx = ((int)buf[10] << 8) | buf[11];

                if ((idx >= 0) && (idx < EC_MAXBUF) &&
                    (port->rxbufstat[idx] == EC_BUF_TX))
                {
                    uint16_t len = (uint16_t)pkt->sgList.list[0].segmentFilledLen;
                    if (len > EC_BUFSIZE) { len = EC_BUFSIZE; }
                    memcpy(&(port->rxbuf[idx][0]), buf, len);
                    port->rxbufstat[idx] = EC_BUF_RCVD;
                    port->rxsa[idx]      = (buf[4] << 8) | buf[5];
                    if (found < 0) { found = idx; }
                    g_rxCount++;
                    if (g_rxCount <= 5U)
                    {
                        DebugP_log("[NIC] RX idx=%d len=%d count=%u\r\n",
                                   idx, (int)pkt->sgList.list[0].segmentFilledLen, g_rxCount);
                    }
                }
            }

            ENET_UTILS_SET_PKT_APP_STATE(&pkt->pktState, ENET_PKTSTATE_APP_WITH_FREEQ);
            EnetQueue_enq(&rxFreeQ, &pkt->node);
            pkt = (EnetDma_Pkt *)EnetQueue_deq(&rxReadyQ);
        }

        /* Return all buffers to DMA */
        if (EnetQueue_getQCount(&rxFreeQ) > 0U)
        {
            EnetAppUtils_validatePacketState(&rxFreeQ,
                                             ENET_PKTSTATE_APP_WITH_FREEQ,
                                             ENET_PKTSTATE_APP_WITH_DRIVER);
            EnetDma_submitRxPktQ(g_enetCtx.hRxCh, &rxFreeQ);
        }

        if (found >= 0) { return found; }

        {
            ec_timet tnow2;
            osal_get_monotonic_time(&tnow2);
            if (osal_timespeccmp(&tnow2, &deadline, >=)) { break; }
        }
    } while (1);

    g_rxTimeoutCount++;
    if (g_rxTimeoutCount <= 5U)
    {
        DebugP_log("[NIC] RX timeout count=%u tx=%u rx=%u\r\n",
                   g_rxTimeoutCount, g_txCount, g_rxCount);
    }
    return -1;
}

void ecx_setbufstat(ecx_portt *port, uint8 idx, int bufstat)
{
    port->rxbufstat[idx] = bufstat;
}

uint8 ecx_getindex(ecx_portt *port)
{
    uint8 idx;
    uint8 cnt = 0;
    idx = port->lastidx + 1U;
    if (idx >= EC_MAXBUF)
    {
        idx = 0U;
    }
    while ((port->rxbufstat[idx] != EC_BUF_EMPTY) && (cnt < EC_MAXBUF))
    {
        idx++;
        cnt++;
        if (idx >= EC_MAXBUF)
        {
            idx = 0U;
        }
    }
    port->rxbufstat[idx] = EC_BUF_ALLOC;
    port->lastidx = idx;
    return idx;
}

int ecx_waitinframe(ecx_portt *port, uint8 idx, int timeout)
{
    int idxf;
    if ((idx < EC_MAXBUF) && (port->rxbufstat[idx] == EC_BUF_RCVD))
    {
        port->rxbufstat[idx] = EC_BUF_COMPLETE;
        return port->rxsa[idx];
    }
    idxf = ecx_inframe(port, 0, timeout);
    if ((idxf >= 0) && (idxf < EC_MAXBUF) && (port->rxbufstat[idxf] == EC_BUF_RCVD))
    {
        port->rxbufstat[idxf] = EC_BUF_COMPLETE;
        return port->rxsa[idxf];
    }
    return EC_NOFRAME;
}

int ecx_srconfirm(ecx_portt *port, uint8 idx, int timeout)
{
    int wkc;
    osal_timert timer;
    osal_timer_start(&timer, timeout);
    do
    {
        ecx_outframe(port, idx, 0);
        wkc = ecx_waitinframe(port, idx, EC_TIMEOUTRET);
    } while ((wkc <= EC_NOFRAME) && !osal_timer_is_expired(&timer));
    port->rxbufstat[idx] = EC_BUF_EMPTY;
    return wkc;
}
