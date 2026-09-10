#include "eea_gateway_bridge.h"

#include <stddef.h>
#include <string.h>

// Register layout assumption based on EtherCAT gateway map.
// Reg[0] packs heartbeat and terminator; Reg[1] packs brightness and LEDs; Reg[2] latency sequence.
uint16_t eea_bridge_pack_control_to_registers(
    const EeaGatewayControl* in,
    uint16_t* regs,
    uint16_t regs_capacity)
{
    if (!in || !regs || regs_capacity < 3) {
        return 0;
    }

    regs[0] = (uint16_t)(in->heartbeat & 0x00FFu) | (uint16_t)((uint16_t)in->terminator << 8);

    regs[1] = (uint16_t)(in->brightness_blink & 0x00FFu)
        | (uint16_t)((uint16_t)(in->led_blue & 0x03u) << 8)
        | (uint16_t)((uint16_t)(in->led_green & 0x03u) << 10)
        | (uint16_t)((uint16_t)(in->led_red & 0x03u) << 12);

    regs[2] = in->latency_seq_input;
    return 3;
}

bool eea_bridge_unpack_registers_to_status(
    const uint16_t* regs,
    uint16_t regs_count,
    EeaGatewayStatus* out)
{
    if (!regs || !out || regs_count < 10) {
        return false;
    }

    memset(out, 0, sizeof(*out));

    out->brightness_blink = (uint8_t)(regs[0] & 0x00FFu);
    out->led_blue = (uint8_t)((regs[1] >> 0) & 0x0003u);
    out->led_green = (uint8_t)((regs[1] >> 2) & 0x0003u);
    out->led_red = (uint8_t)((regs[1] >> 4) & 0x0003u);

    out->enc_locking_position = regs[2];
    out->general_info = regs[3];
    out->latency_seq_return = regs[4];

    out->frame_seq = (uint32_t)regs[5] | ((uint32_t)regs[6] << 16);
    out->encoder_seq = (uint32_t)regs[7] | ((uint32_t)regs[8] << 16);
    out->encoder_value = regs[9];

    return true;
}

bool eea_bridge_build_rtu_write_multiple(
    uint8_t station_id,
    uint16_t start_reg,
    const uint16_t* regs,
    uint16_t regs_count,
    ModbusRtuFrame* out)
{
    uint16_t i;

    if (!regs || !out || regs_count == 0 || regs_count > 16) {
        return false;
    }

    memset(out, 0, sizeof(*out));
    out->station_id = station_id;
    out->function_code = 0x10; // Write Multiple Registers
    out->register_start = start_reg;
    out->register_count = regs_count;

    for (i = 0; i < regs_count; ++i) {
        out->registers[i] = regs[i];
    }

    // Caller computes serialized frame bytes and can reuse this crc helper.
    out->crc16 = 0;
    return true;
}

uint16_t eea_bridge_modbus_crc16(const uint8_t* data, uint16_t len)
{
    uint16_t crc = 0xFFFFu;
    uint16_t i;
    uint8_t j;

    if (!data) {
        return 0;
    }

    for (i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i];
        for (j = 0; j < 8; ++j) {
            if ((crc & 0x0001u) != 0u) {
                crc >>= 1;
                crc ^= 0xA001u;
            } else {
                crc >>= 1;
            }
        }
    }

    return crc;
}

uint8_t eea_bridge_fw_part_num(uint16_t general_info)
{
    return (uint8_t)((general_info & 0x0F00u) >> 8);
}

uint8_t eea_bridge_fw_part_rev(uint16_t general_info)
{
    return (uint8_t)((general_info & 0x00F0u) >> 4);
}

uint8_t eea_bridge_fw_build_num(uint16_t general_info)
{
    return (uint8_t)(general_info & 0x000Fu);
}
