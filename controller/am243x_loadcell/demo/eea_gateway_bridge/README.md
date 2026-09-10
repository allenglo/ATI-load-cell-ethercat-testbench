# EEA Gateway Bridge (Host + LaunchPad)

## What this folder contains

- `eea_gateway_bridge.h`: clean API for EtherCAT-to-Modbus bridge logic.
- `eea_gateway_bridge.c`: conversion helpers, register packing, status unpacking, CRC16.

This module is intentionally hardware-agnostic so future agents can wire it to TI UART drivers,
FreeRTOS tasks, or existing board support code without rewriting conversion logic.

## Data flow

1. PC EtherCAT host writes gateway output process image fields.
2. LaunchPad receives mapped control fields and converts to Modbus register writes.
3. LaunchPad sends RTU requests to EEA/ROI devices.
4. LaunchPad collects responses and converts registers back to gateway status fields.
5. PC host reads status and decodes firmware/status fields for UI + logging.

## Integration on LaunchPad

1. Include this module in your CCS project.
2. Call `eea_bridge_pack_control_to_registers()` before each Modbus write cycle.
3. Build RTU frame metadata with `eea_bridge_build_rtu_write_multiple()`.
4. Serialize and transmit with your UART HAL.
5. After receive/decode of RTU response registers, call `eea_bridge_unpack_registers_to_status()`.
6. Publish `EeaGatewayStatus` fields back into your EtherCAT process image.

## Debug strategy

- Log both raw register arrays and decoded struct fields.
- Validate nibble-level decode using `eea_bridge_fw_part_num`, `eea_bridge_fw_part_rev`, and `eea_bridge_fw_build_num`.
- If status is unstable, compare host decoded values with LaunchPad decoded values at the same sequence index.

## Known assumption to verify on hardware

- Register word packing in `eea_bridge_pack_control_to_registers()` uses a best-fit map from recovered XML and reverse engineering.
- Confirm register endianness and exact bit packing with on-target captures before production release.
