#ifndef EEA_GATEWAY_BRIDGE_H
#define EEA_GATEWAY_BRIDGE_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Gateway control fields sent from EtherCAT host to EEA/ROI serial lane.
typedef struct {
    uint8_t heartbeat;
    uint8_t terminator;
    uint8_t brightness_blink;
    uint8_t led_blue;
    uint8_t led_green;
    uint8_t led_red;
    uint16_t latency_seq_input;
} EeaGatewayControl;

// Gateway status fields returned from EEA/ROI serial lane back to EtherCAT host.
typedef struct {
    uint8_t brightness_blink;
    uint8_t led_blue;
    uint8_t led_green;
    uint8_t led_red;
    uint16_t enc_locking_position;
    uint16_t general_info;
    uint16_t latency_seq_return;
    uint32_t frame_seq;
    uint32_t encoder_seq;
    uint16_t encoder_value;
} EeaGatewayStatus;

// Serial payload used by LaunchPad UART side.
typedef struct {
    uint8_t station_id;
    uint8_t function_code;
    uint16_t register_start;
    uint16_t register_count;
    uint16_t registers[16];
    uint16_t crc16;
} ModbusRtuFrame;

// Pack EtherCAT control data into Modbus register payload (host -> LaunchPad -> serial bus).
uint16_t eea_bridge_pack_control_to_registers(
    const EeaGatewayControl* in,
    uint16_t* regs,
    uint16_t regs_capacity);

// Unpack Modbus status registers into EtherCAT status data (serial bus -> LaunchPad -> host).
bool eea_bridge_unpack_registers_to_status(
    const uint16_t* regs,
    uint16_t regs_count,
    EeaGatewayStatus* out);

// Build an RTU request frame (without transport timing control).
bool eea_bridge_build_rtu_write_multiple(
    uint8_t station_id,
    uint16_t start_reg,
    const uint16_t* regs,
    uint16_t regs_count,
    ModbusRtuFrame* out);

// Standard Modbus CRC16 helper.
uint16_t eea_bridge_modbus_crc16(const uint8_t* data, uint16_t len);

// Utility decoders for diagnostics.
uint8_t eea_bridge_fw_part_num(uint16_t general_info);
uint8_t eea_bridge_fw_part_rev(uint16_t general_info);
uint8_t eea_bridge_fw_build_num(uint16_t general_info);

#ifdef __cplusplus
}
#endif

#endif
