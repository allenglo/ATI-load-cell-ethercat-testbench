/*
 * eea_ecat_main.c
 *
 * EtherCAT master task for the EEA / Hilscher EFlexEthercatModbusRTUGateway.
 *
 * Runs on AM243x LaunchPad using SOEM (ecx_contextt).
 * Finds the gateway slave, enters OP state, and runs a cyclic loop that:
 *  - Writes output PDO from a live command struct (updated via UART commands).
 *  - Reads input PDO and prints decoded gateway status at configurable intervals.
 *  - Supports "ESTOP" command to zero all outputs immediately.
 *
 * Debug macros intentionally verbose — trace every meaningful transition.
 *
 * Wire-up notes:
 *  - Connect AM243x CPSW0 Ethernet port to EtherCAT slave chain.
 *  - Gateway slave must be the only (or first) slave on the bus.
 *  - UART0 @ 115200 for host commands and decoded output.
 */

#include "soem/soem.h"
#include "osal.h"

#include <kernel/dpl/DebugP.h>
#include <kernel/dpl/ClockP.h>

#include <stdint.h>
#include <string.h>

/* ---- Bridge module ---- */
#include "eea_gateway_bridge.h"

/* ======================================================================
 * Constants
 * ====================================================================== */
#define EEA_GW_SLAVE_NAME_HINT      "EFlex"          /* substring match */
#define EEA_LOOP_PERIOD_US          (1000U)           /* 1 ms cycle */
#define EEA_PRINT_EVERY_CYCLES      (50U)             /* print every 50 ms */
#define EEA_MAX_SLAVES              (16U)

/* PDO sizes in bytes derived from process image (320 bits out, 672 bits in) */
#define EEA_PDO_OUT_BYTES           (40U)
#define EEA_PDO_IN_BYTES            (84U)

/* ======================================================================
 * Output PDO layout (gateway slave.output local byte 0 = global bit 208)
 * ====================================================================== */
typedef struct __attribute__((packed))
{
    /* ToROI block */
    uint8_t  roi_heartbeat;           /* byte 0  */
    uint8_t  roi_terminator;          /* byte 1  */
    uint8_t  roi_brightness_blink;    /* byte 2  */
    uint8_t  roi_led_blue;            /* byte 3  */
    uint8_t  roi_led_green;           /* byte 4  */
    uint8_t  roi_led_red;             /* byte 5  */
    uint16_t roi_latency_sqn_in;      /* bytes 6-7  */
    /* ToEEA S3 block */
    uint8_t  s3_heartbeat;            /* byte 8  */
    uint8_t  s3_terminator;           /* byte 9  */
    uint8_t  s3_brightness_blink;     /* byte 10 */
    uint8_t  s3_led_blue;             /* byte 11 */
    uint8_t  s3_led_green;            /* byte 12 */
    uint8_t  s3_led_red;              /* byte 13 */
    uint16_t s3_latency_sqn_in;       /* bytes 14-15 */
    /* ToEEA latency-only stations */
    uint16_t s2_latency_sqn_in;       /* bytes 16-17 */
    uint16_t s1_latency_sqn_in;       /* bytes 18-19 */
    /* Additional channels (ToS1..S10) */
    uint16_t additional[10];          /* bytes 20-39 */
} EeaOutPdo;

/* ======================================================================
 * Input PDO layout (gateway slave.input local byte 0 = global bit 688)
 * ====================================================================== */
typedef struct __attribute__((packed))
{
    /* FromROI S4 */
    uint8_t  roi_brightness_blink;    /* byte 0  */
    uint8_t  roi_led_blue;            /* byte 1  */
    uint8_t  roi_led_green;           /* byte 2  */
    uint8_t  roi_led_red;             /* byte 3  */
    uint16_t roi_general_info;        /* bytes 4-5  */
    uint16_t roi_latency_sqn_ret;     /* bytes 6-7  */
    uint32_t roi_frame_sqn;           /* bytes 8-11 */
    /* FromEEA S3 */
    uint8_t  s3_brightness_blink;     /* byte 12 */
    uint8_t  s3_led_blue;             /* byte 13 */
    uint8_t  s3_led_green;            /* byte 14 */
    uint8_t  s3_led_red;              /* byte 15 */
    uint16_t s3_enc_lock_pos;         /* bytes 16-17 */
    uint16_t s3_general_info;         /* bytes 18-19 */
    uint16_t s3_latency_sqn_ret;      /* bytes 20-21 */
    uint32_t s3_frame_sqn;            /* bytes 22-25 */
    uint32_t s3_encoder_sqn;          /* bytes 26-29 */
    uint16_t s3_encoder_value;        /* bytes 30-31 */
    /* FromEEA S2 */
    uint16_t s2_enc_lock_pos;         /* bytes 32-33 */
    uint16_t s2_general_info;         /* bytes 34-35 */
    uint16_t s2_latency_sqn_ret;      /* bytes 36-37 */
    uint32_t s2_frame_sqn;            /* bytes 38-41 */
    uint32_t s2_encoder_sqn;          /* bytes 42-45 */
    uint16_t s2_encoder_value;        /* bytes 46-47 */
    /* FromEEA S1 */
    uint16_t s1_enc_lock_pos;         /* bytes 48-49 */
    uint16_t s1_general_info;         /* bytes 50-51 */
    uint16_t s1_latency_sqn_ret;      /* bytes 52-53 */
    uint32_t s1_frame_sqn;            /* bytes 54-57 */
    uint32_t s1_encoder_sqn;          /* bytes 58-61 */
    uint16_t s1_encoder_value;        /* bytes 62-63 */
    /* Additional channels (FromC1..C10) */
    uint16_t additional[10];          /* bytes 64-83 */
} EeaInPdo;

/* ======================================================================
 * Static state
 * ====================================================================== */
#define TRACE_EEA(fmt, ...) DebugP_log("[EEA][TRACE] %s:%d " fmt "\r\n", __FUNCTION__, __LINE__, ##__VA_ARGS__)
#define ERROR_EEA(fmt, ...) DebugP_log("[EEA][ERROR] %s:%d " fmt "\r\n", __FUNCTION__, __LINE__, ##__VA_ARGS__)
#define INFO_EEA(fmt, ...)  DebugP_log("[EEA][INFO]  " fmt "\r\n", ##__VA_ARGS__)

static ecx_contextt  g_ctx;
static EeaOutPdo     g_cmd;   /* live command image updated by UART or default */
static uint8_t       g_estop = 0U;

/* ======================================================================
 * Helpers
 * ====================================================================== */
static int find_gateway_slave(void)
{
    int s;
    TRACE_EEA("find_gateway_slave slavecount=%d", g_ctx.slavecount);
    for (s = 1; s <= g_ctx.slavecount; s++)
    {
        const char *name = (const char *)g_ctx.slavelist[s].name;
        TRACE_EEA("  slave[%d] name='%s' eep_man=0x%08x eep_id=0x%08x",
                  s, name ? name : "<null>",
                  (unsigned int)g_ctx.slavelist[s].eep_man,
                  (unsigned int)g_ctx.slavelist[s].eep_id);
        if (name && strstr(name, EEA_GW_SLAVE_NAME_HINT))
        {
            TRACE_EEA("  gateway match at slave=%d", s);
            return s;
        }
    }
    /* Fall back to first slave if hint not found */
    if (g_ctx.slavecount > 0)
    {
        TRACE_EEA("  hint not found; falling back to slave 1");
        return 1;
    }
    return -1;
}

static void print_decoded_input(const EeaInPdo *in, int wkc)
{
    INFO_EEA("wkc=%d", wkc);

    /* ROI */
    INFO_EEA("  ROI  fw=%u.%u.%u bright=0x%02x blue=%u grn=%u red=%u frm=%lu latRet=%u",
             (unsigned)eea_bridge_fw_part_num(in->roi_general_info),
             (unsigned)eea_bridge_fw_part_rev(in->roi_general_info),
             (unsigned)eea_bridge_fw_build_num(in->roi_general_info),
             (unsigned)in->roi_brightness_blink,
             (unsigned)in->roi_led_blue,
             (unsigned)in->roi_led_green,
             (unsigned)in->roi_led_red,
             (unsigned long)in->roi_frame_sqn,
             (unsigned)in->roi_latency_sqn_ret);

    /* S3 */
    INFO_EEA("  S3   fw=%u.%u.%u bright=0x%02x enc=%u lock=%u frm=%lu encSQN=%lu latRet=%u",
             (unsigned)eea_bridge_fw_part_num(in->s3_general_info),
             (unsigned)eea_bridge_fw_part_rev(in->s3_general_info),
             (unsigned)eea_bridge_fw_build_num(in->s3_general_info),
             (unsigned)in->s3_brightness_blink,
             (unsigned)in->s3_encoder_value,
             (unsigned)in->s3_enc_lock_pos,
             (unsigned long)in->s3_frame_sqn,
             (unsigned long)in->s3_encoder_sqn,
             (unsigned)in->s3_latency_sqn_ret);

    /* S2 */
    INFO_EEA("  S2   fw=%u.%u.%u enc=%u lock=%u frm=%lu encSQN=%lu",
             (unsigned)eea_bridge_fw_part_num(in->s2_general_info),
             (unsigned)eea_bridge_fw_part_rev(in->s2_general_info),
             (unsigned)eea_bridge_fw_build_num(in->s2_general_info),
             (unsigned)in->s2_encoder_value,
             (unsigned)in->s2_enc_lock_pos,
             (unsigned long)in->s2_frame_sqn,
             (unsigned long)in->s2_encoder_sqn);

    /* S1 */
    INFO_EEA("  S1   fw=%u.%u.%u enc=%u lock=%u frm=%lu encSQN=%lu",
             (unsigned)eea_bridge_fw_part_num(in->s1_general_info),
             (unsigned)eea_bridge_fw_part_rev(in->s1_general_info),
             (unsigned)eea_bridge_fw_build_num(in->s1_general_info),
             (unsigned)in->s1_encoder_value,
             (unsigned)in->s1_enc_lock_pos,
             (unsigned long)in->s1_frame_sqn,
             (unsigned long)in->s1_encoder_sqn);
}

/* ======================================================================
 * Main task
 * ====================================================================== */
void eea_ecat_master_task(void *args)
{
    uint8_t   IOmap[4096];
    int       wkc;
    int       gwSlv;
    int       retry;
    uint32_t  cycle     = 0U;
    EeaOutPdo *out_pdo  = NULL;
    EeaInPdo  *in_pdo   = NULL;

    (void)args;

    memset(&g_cmd, 0, sizeof(g_cmd));
    g_cmd.roi_heartbeat   = 1U;
    g_cmd.s3_heartbeat    = 1U;
    g_cmd.s3_brightness_blink = 0x11U;  /* brightness=1, blink_period=1 */

    TRACE_EEA("task enter");
    INFO_EEA("EEA EtherCAT master starting...");

    TRACE_EEA("ecx_init(cpsw0) begin");
    if (!ecx_init(&g_ctx, "cpsw0"))
    {
        ERROR_EEA("ecx_init failed");
        return;
    }
    TRACE_EEA("ecx_init OK");

    INFO_EEA("Waiting for PHY link...");
    osal_usleep(2000000U);

    for (retry = 0; retry < 5; retry++)
    {
        TRACE_EEA("ecx_config_init try=%d", retry);
        if (ecx_config_init(&g_ctx) > 0)
        {
            TRACE_EEA("ecx_config_init OK slaves=%d", g_ctx.slavecount);
            break;
        }
        TRACE_EEA("ecx_config_init returned 0, retry in 500ms");
        osal_usleep(500000U);
    }

    if (g_ctx.slavecount < 1)
    {
        ERROR_EEA("No slaves found after retries");
        return;
    }
    INFO_EEA("Found %d slave(s)", g_ctx.slavecount);

    gwSlv = find_gateway_slave();
    if (gwSlv < 0)
    {
        ERROR_EEA("Gateway slave not found");
        return;
    }
    INFO_EEA("Gateway slave index = %d  name='%s'",
             gwSlv, (char *)g_ctx.slavelist[gwSlv].name);

    ecx_config_map_group(&g_ctx, IOmap, 0);
    TRACE_EEA("IOmap config done");

    ecx_statecheck(&g_ctx, 0, EC_STATE_SAFE_OP, EC_TIMEOUTSTATE);
    TRACE_EEA("State check SAFE_OP done");

    g_ctx.slavelist[0].state = EC_STATE_OPERATIONAL;
    ecx_writestate(&g_ctx, 0);
    ecx_statecheck(&g_ctx, 0, EC_STATE_OPERATIONAL, EC_TIMEOUTSTATE);
    TRACE_EEA("State check OP done");

    if (g_ctx.slavelist[0].state != EC_STATE_OPERATIONAL)
    {
        ERROR_EEA("Failed to reach OP state (actual=0x%x)",
                  (unsigned)g_ctx.slavelist[0].state);
        return;
    }
    INFO_EEA("All slaves in OP state");

    out_pdo = (EeaOutPdo *)g_ctx.slavelist[gwSlv].outputs;
    in_pdo  = (EeaInPdo  *)g_ctx.slavelist[gwSlv].inputs;

    if (!out_pdo || !in_pdo)
    {
        ERROR_EEA("Slave output/input pointers are NULL");
        return;
    }

    INFO_EEA("Entering cyclic loop (period=%u us)", (unsigned)EEA_LOOP_PERIOD_US);

    for (;;)
    {
        /* Apply command image (or zero on estop) */
        if (g_estop)
        {
            memset(out_pdo, 0, sizeof(EeaOutPdo));
        }
        else
        {
            memcpy(out_pdo, &g_cmd, sizeof(EeaOutPdo));
            /* Increment heartbeat every cycle */
            g_cmd.roi_heartbeat++;
            g_cmd.s3_heartbeat++;
        }

        wkc = ecx_send_processdata(&g_ctx);
        ecx_receive_processdata(&g_ctx, EC_TIMEOUTRET);

        cycle++;
        if ((cycle % EEA_PRINT_EVERY_CYCLES) == 0U)
        {
            print_decoded_input(in_pdo, wkc);
        }

        osal_usleep(EEA_LOOP_PERIOD_US);
    }
}
