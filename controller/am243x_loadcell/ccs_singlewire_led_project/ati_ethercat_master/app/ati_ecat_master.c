#include "soem/soem.h"
#include "osal.h"

#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/ClockP.h>
#include <stdint.h>

#define ATI_VENDOR_ID             (0x00000732U)
#define ATI_PRODUCT_CODE_A        (0x26483052U)
#define ATI_PRODUCT_CODE_B        (0x2647F902U)
#define ECAT_LOOP_PERIOD_US       (1000U)
#define ATI_PRINT_EVERY_CYCLES    (10U)
#define ATI_TARE_SAMPLES          (200U)

typedef struct __attribute__((packed))
{
    int32_t Fx;
    int32_t Fy;
    int32_t Fz;
    int32_t Tx;
    int32_t Ty;
    int32_t Tz;
} AtiPdo;

static ecx_contextt g_ctx;

#define TRACE_ECAT(fmt, ...) DebugP_log("[ECAT][TRACE] %s:%d " fmt "\r\n", __FUNCTION__, __LINE__, ##__VA_ARGS__)
#define ERROR_ECAT(fmt, ...) DebugP_log("[ECAT][ERROR] %s:%d " fmt "\r\n", __FUNCTION__, __LINE__, ##__VA_ARGS__)

static int find_ati_slave(void)
{
    int s;
    int vendorMatch = -1;

    TRACE_ECAT("find_ati_slave() start slavecount=%d", g_ctx.slavecount);
    for (s = 1; s <= g_ctx.slavecount; s++)
    {
        TRACE_ECAT("scan slave=%d eep_man=0x%08x eep_id=0x%08x", s,
                   (unsigned int)g_ctx.slavelist[s].eep_man,
                   (unsigned int)g_ctx.slavelist[s].eep_id);
        if (g_ctx.slavelist[s].eep_man == ATI_VENDOR_ID)
        {
            if (vendorMatch < 0)
            {
                vendorMatch = s;
            }

            if ((g_ctx.slavelist[s].eep_id == ATI_PRODUCT_CODE_A) ||
                (g_ctx.slavelist[s].eep_id == ATI_PRODUCT_CODE_B))
            {
                TRACE_ECAT("ATI exact match at slave=%d", s);
                return s;
            }
        }
    }

    if (vendorMatch > 0)
    {
        TRACE_ECAT("ATI vendor-only match at slave=%d", vendorMatch);
        return vendorMatch;
    }

    TRACE_ECAT("ATI vendor/product not found");
    return -1;
}

void ati_ecat_master_task(void *args)
{
    uint8_t IOmap[4096];
    int expectedWKC;
    int atiSlv;
    int wkc;
    int ioMapSize;
    uint16_t stateSafeOp;
    uint16_t stateOp;
    AtiPdo *pdo;
    uint32_t cycle = 0;
    uint32_t sampleIdx = 0;
    uint64_t tsUsec = 0;
    uint32_t tsMsec = 0;
    int32_t fxNet, fyNet, fzNet, txNet, tyNet, tzNet;
    int64_t tareSumFx = 0;
    int64_t tareSumFy = 0;
    int64_t tareSumFz = 0;
    int64_t tareSumTx = 0;
    int64_t tareSumTy = 0;
    int64_t tareSumTz = 0;
    int32_t tareOffFx = 0;
    int32_t tareOffFy = 0;
    int32_t tareOffFz = 0;
    int32_t tareOffTx = 0;
    int32_t tareOffTy = 0;
    int32_t tareOffTz = 0;
    uint32_t tareCount = 0;
    uint8_t tareDone = 0;
    uint16_t inputBytes = 0;

    int slaveCount = 0;
    int retry;

    (void)args;

    TRACE_ECAT("task enter args=%p", args);
    DebugP_log("[ECAT] init...\r\n");
    TRACE_ECAT("ecx_init(cpsw0) begin");
    if (!ecx_init(&g_ctx, "cpsw0"))
    {
        ERROR_ECAT("ecx_init failed for netif=cpsw0");
        return;
    }
    TRACE_ECAT("ecx_init success");

    /* Wait up to 3 s for PHY link-up then retry slave scan */
    DebugP_log("[ECAT] waiting for link...\r\n");
    TRACE_ECAT("sleep 2s for link settle");
    osal_usleep(2000000U);   /* 2 s: let PHY auto-neg finish */

    for (retry = 0; retry < 5; retry++)
    {
        TRACE_ECAT("ecx_config_init try=%d begin", retry);
        slaveCount = ecx_config_init(&g_ctx);
        DebugP_log("[ECAT] scan try %d: slaves=%d\r\n", retry, slaveCount);
        TRACE_ECAT("ecx_config_init try=%d result slaveCount=%d", retry, slaveCount);
        if (slaveCount > 0) { break; }
        TRACE_ECAT("no slaves yet, sleep 500ms");
        osal_usleep(500000U);
    }

    if (slaveCount <= 0)
    {
        ERROR_ECAT("no slaves after retries - check cable to ATI IN port");
        ecx_closenic(&g_ctx.port);
        TRACE_ECAT("ecx_closenic done");
        return;
    }

    DebugP_log("[ECAT] slaves=%d\r\n", g_ctx.slavecount);
    TRACE_ECAT("find_ati_slave begin");
    atiSlv = find_ati_slave();
    if (atiSlv < 0)
    {
        atiSlv = 1;
        TRACE_ECAT("ATI match not found, fallback atiSlv=1");
    }
    else
    {
        TRACE_ECAT("ATI slave selected atiSlv=%d", atiSlv);
    }

    inputBytes = g_ctx.slavelist[atiSlv].Ibytes;
    DebugP_log("[ECAT] slave=%d man=0x%08x id=0x%08x Ibytes=%u Obytes=%u\r\n",
               atiSlv,
               (unsigned int)g_ctx.slavelist[atiSlv].eep_man,
               (unsigned int)g_ctx.slavelist[atiSlv].eep_id,
               (unsigned int)g_ctx.slavelist[atiSlv].Ibytes,
               (unsigned int)g_ctx.slavelist[atiSlv].Obytes);
    if (inputBytes < sizeof(AtiPdo))
    {
        ERROR_ECAT("ATI input payload too small: %u bytes", (unsigned int)inputBytes);
    }

    TRACE_ECAT("ecx_config_map_group begin");
    ioMapSize = ecx_config_map_group(&g_ctx, &IOmap, 0);
    TRACE_ECAT("ecx_config_map_group done ioMapSize=%d", ioMapSize);

    TRACE_ECAT("ecx_configdc begin");
    ecx_configdc(&g_ctx);
    TRACE_ECAT("ecx_configdc done");

    TRACE_ECAT("request SAFE_OP begin");
    g_ctx.slavelist[0].state = EC_STATE_SAFE_OP;
    ecx_writestate(&g_ctx, 0);
    stateSafeOp = ecx_statecheck(&g_ctx, 0, EC_STATE_SAFE_OP, EC_TIMEOUTSTATE);
    DebugP_log("[ECAT] state after safe_op request=0x%02x\r\n", (unsigned int)stateSafeOp);
    TRACE_ECAT("request SAFE_OP done");

    TRACE_ECAT("prime process data begin");
    ecx_send_processdata(&g_ctx);
    wkc = ecx_receive_processdata(&g_ctx, EC_TIMEOUTRET);
    DebugP_log("[ECAT] prime receive wkc=%d\r\n", wkc);
    TRACE_ECAT("prime process data done");

    TRACE_ECAT("request OPERATIONAL begin");
    g_ctx.slavelist[0].state = EC_STATE_OPERATIONAL;
    ecx_writestate(&g_ctx, 0);
    stateOp = ecx_statecheck(&g_ctx, 0, EC_STATE_OPERATIONAL, EC_TIMEOUTSTATE);
    DebugP_log("[ECAT] state after op request=0x%02x\r\n", (unsigned int)stateOp);
    TRACE_ECAT("request OPERATIONAL done");

    expectedWKC = (g_ctx.grouplist[0].outputsWKC * 2) + g_ctx.grouplist[0].inputsWKC;
    DebugP_log("[ECAT] OP, expectedWKC=%d\r\n", expectedWKC);
    TRACE_ECAT("enter cyclic loop");

    while (1)
    {
        cycle++;
        TRACE_ECAT("cycle=%lu send", (unsigned long)cycle);
        ecx_send_processdata(&g_ctx);

        TRACE_ECAT("cycle=%lu receive", (unsigned long)cycle);
        wkc = ecx_receive_processdata(&g_ctx, EC_TIMEOUTRET);
        TRACE_ECAT("cycle=%lu wkc=%d expectedWKC=%d", (unsigned long)cycle, wkc, expectedWKC);

        if (wkc <= 0)
        {
            ERROR_ECAT("cycle=%lu bad wkc=%d", (unsigned long)cycle, wkc);
            if (ecx_iserror(&g_ctx))
            {
                const char *errStr = ecx_elist2string(&g_ctx);
                DebugP_log("[ECAT][ERROR] cycle=%lu soem=%s\r\n", (unsigned long)cycle,
                           (errStr != NULL) ? errStr : "(null)");
            }

            osal_usleep(ECAT_LOOP_PERIOD_US);
            continue;
        }

        pdo = (AtiPdo *)g_ctx.slavelist[atiSlv].inputs;
        if (pdo == NULL)
        {
            ERROR_ECAT("cycle=%lu slave=%d inputs pointer NULL", (unsigned long)cycle, atiSlv);
            osal_usleep(ECAT_LOOP_PERIOD_US);
            continue;
        }

        if (!tareDone)
        {
            tareSumFx += pdo->Fx;
            tareSumFy += pdo->Fy;
            tareSumFz += pdo->Fz;
            tareSumTx += pdo->Tx;
            tareSumTy += pdo->Ty;
            tareSumTz += pdo->Tz;
            tareCount++;

            if ((tareCount % 50U) == 0U)
            {
                DebugP_log("[ATI] tare %lu/%u raw Fx=%d Fy=%d Fz=%d Tx=%d Ty=%d Tz=%d\r\n",
                           (unsigned long)tareCount,
                           (unsigned int)ATI_TARE_SAMPLES,
                           (int)pdo->Fx, (int)pdo->Fy, (int)pdo->Fz,
                           (int)pdo->Tx, (int)pdo->Ty, (int)pdo->Tz);
            }

            if (tareCount >= ATI_TARE_SAMPLES)
            {
                tareOffFx = (int32_t)(tareSumFx / (int64_t)ATI_TARE_SAMPLES);
                tareOffFy = (int32_t)(tareSumFy / (int64_t)ATI_TARE_SAMPLES);
                tareOffFz = (int32_t)(tareSumFz / (int64_t)ATI_TARE_SAMPLES);
                tareOffTx = (int32_t)(tareSumTx / (int64_t)ATI_TARE_SAMPLES);
                tareOffTy = (int32_t)(tareSumTy / (int64_t)ATI_TARE_SAMPLES);
                tareOffTz = (int32_t)(tareSumTz / (int64_t)ATI_TARE_SAMPLES);
                tareDone = 1U;
                DebugP_log("[ATI] tare done off Fx=%d Fy=%d Fz=%d Tx=%d Ty=%d Tz=%d\r\n",
                           (int)tareOffFx, (int)tareOffFy, (int)tareOffFz,
                           (int)tareOffTx, (int)tareOffTy, (int)tareOffTz);
            }

            osal_usleep(ECAT_LOOP_PERIOD_US);
            continue;
        }

        sampleIdx++;
        tsUsec = ClockP_getTimeUsec();
        tsMsec = (uint32_t)(tsUsec / 1000ULL);

        fxNet = pdo->Fx - tareOffFx;
        fyNet = pdo->Fy - tareOffFy;
        fzNet = pdo->Fz - tareOffFz;
        txNet = pdo->Tx - tareOffTx;
        tyNet = pdo->Ty - tareOffTy;
        tzNet = pdo->Tz - tareOffTz;

        if ((cycle % ATI_PRINT_EVERY_CYCLES) == 0U)
        {
            DebugP_log("[ATI] %04lu ts_ms=%lu wkc=%d Fx=%d Fy=%d Fz=%d Tx=%d Ty=%d Tz=%d\r\n",
                       (unsigned long)sampleIdx,
                       (unsigned long)tsMsec,
                       wkc,
                       (int)fxNet, (int)fyNet, (int)fzNet,
                       (int)txNet, (int)tyNet, (int)tzNet);
        }

        if ((cycle % 100U) == 0U)
        {
            DebugP_log("[ECAT] heartbeat cycle=%lu slave=%d state=0x%02x expectedWKC=%d\r\n",
                       (unsigned long)cycle, atiSlv,
                       (unsigned int)g_ctx.slavelist[atiSlv].state,
                       expectedWKC);
        }

        osal_usleep(ECAT_LOOP_PERIOD_US);
    }
}
