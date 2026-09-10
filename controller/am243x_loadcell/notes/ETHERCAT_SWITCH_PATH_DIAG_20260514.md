# EtherCAT Switch-Path Diagnostic (2026-05-14)

## What was verified (no assumptions)

1. Confluence access works with local token config.
2. ATI page content was fetched from Confluence and confirms this board is EtherCAT slave and requires external EtherCAT master.
3. LaunchPad EtherCAT firmware is running and heartbeat is active over UART.
4. Live pysoem scan results:
   - Realtek Gaming USB 2.5GbE (`NPF_{1ED1...}`): detects exactly 1 slave
     - `ATI EtherCAT F/T Sensor`
     - man=1842 (`0x00000732`), prod=642265170 (`0x26483052`), rev=65809 (`0x00010111`)
     - WKC observed: 3
   - Realtek USB 2.5GbE (`NPF_{1CFF...}`): `config_init=-1` (no usable EtherCAT slave discovery)
5. ATI object-level communication confirmed via SDO read-only probe:
   - device name, identity vendor/product/revision all readable
   - proves master <-> ATI communication is working in software.

## Critical observation for LaunchPad path

Controlled test:
- Reload LaunchPad firmware to INIT (`0x1`) via DSS 2-step load.
- Run one pysoem scan on ATI-visible adapter.
- UART shows LaunchPad transitions: `0x1 -> 0x2 -> 0x12` while LaunchPad is still not enumerated by that master scan.

This means LaunchPad does receive EtherCAT control traffic but is not being enumerated on the same discovered slave chain as ATI by the current master path.

## Confluence pages used

- `125731336` Integration of ATI EtherCAT F/T sensor with KUKA KRC5 controller
- `29458471` Force/Torque Measurement

Key extracted text (summary):
- ATI EtherCAT OEM board is a slave and needs an EtherCAT master.
- Historical working setup used SOEM + Realtek USB NIC + Npcap on Windows.

## Scripts used/added

- Added: `scripts/ethercat_switch_scan.py`
- Added: `scripts/ethercat_raw_probe.py` (Scapy interface mismatch on this host still needs adapter-name mapping)
- Added: `scripts/ati_ft_testbench.py` (host pysoem master, live ATI Fx/Fy/Fz/Tx/Ty/Tz readouts)
- Reused: `scripts/uart_monitor.py`

## Single-Slave ATI Testbench Result (2026-05-14)

Command used:
- `python scripts/ati_ft_testbench.py --adapter-contains "Realtek Gaming USB 2.5GbE" --cycles 60 --period-ms 10`

Observed:
- ATI slave discovered and identified via CoE SDO reads.
- Cyclic PDO readout active with `WKC=3`.
- Input payload length: 32 bytes.
- Decoded 6-channel values printed each cycle (`Fx, Fy, Fz, Tx, Ty, Tz`) with summary statistics.

Conclusion:
- ATI communication and readout path is working end-to-end with host EtherCAT master.
- This is currently the shortest reliable validation path for force/torque data.

## Most likely blocker from measured behavior

Current physical/network path exposes ATI cleanly but not a stable dual-slave chain (ATI + LaunchPad) to one master interface.

## Next check to finish integration

1. Keep master on `NPF_{1ED1...}` (ATI-visible adapter).
2. Ensure LaunchPad is connected on the same EtherCAT forwarding path expected by the master chain.
3. Re-run:
   - `python scripts/ethercat_switch_scan.py --adapter-contains "Realtek Gaming" --expect-total-slaves 2 --expect-name-contains ATI --expect-name-contains "TI EtherCAT" --json`
4. Pass condition:
   - two slaves discovered in one scan from one adapter
   - LaunchPad UART remains in valid EtherCAT state (no persistent `0x12` error state)
