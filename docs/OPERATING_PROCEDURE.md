# Peltier thermal testbench operating procedure

## Purpose

Use this bench to correlate ATI force/torque output with controlled temperature changes on the EFlex Palm assembly. The GUI records EtherCAT load-cell data, ESP32 temperature data, and thermal output state on one timeline.

This is an engineering characterization bench. It is not an environmental-chamber qualification system or a safety-rated thermal controller.

## Bench configuration

- Dedicated Windows laptop running the Python GUI.
- USB 2.5 GbE adapter to PoE switch.
- PoE switch to the custom Palm/ATI bench harness.
- ATI EtherCAT F/T sensor and EFlex Palm assembly.
- ESP32-S3 on USB serial, normally COM33.
- Two LTC2990 devices at `0x4C` and `0x4F`; MPU6050 at `0x68`.
- External Peltier driver controlled by active-high GPIO13 HEAT and GPIO14 COOL.

See [Physical setup](PHYSICAL_SETUP.md) for wiring and pinout.

## Before use

1. Inspect the Peltier stack, cold plate, thermal interfaces, sensor strip, harnesses, and cooling path.
2. Keep Peltier power disabled.
3. Confirm external pull-downs keep HEAT and COOL off when the ESP32 is reset or unpowered.
4. Connect the dedicated USB Ethernet adapter, PoE switch, custom Palm/ATI harness, and ESP32 USB cable.
5. Confirm the expected network adapter and ESP32 COM port appear in Windows.

## Start the bench

1. Start `host-tools/launchpad_loadcell_live_gui.py`.
2. Select the dedicated Realtek USB 2.5 GbE adapter and **ATI Load Cell** profile.
3. Connect ESP32 serial at 115200 baud.
4. Confirm both LTC2990 devices report `GOOD` and the thermal state is `IDLE`.
5. Connect EtherCAT. Confirm the ATI sensor reaches OP and the working counter is nonzero.
6. Enable load-cell and serial CSV logging.
7. Enable external Peltier power only after the checks above pass.

## Hold mode

1. Select **Hold**.
2. Enter target temperature, idle window, and sensor source (`AVG`, `4C`, or `4F`).
3. Select **Apply Hold**.
4. Confirm the status bar, dotted graph thresholds, and HEAT/IDLE/COOL strip agree with the command.

The target may be changed while Hold is active. The GUI applies edits after 600 ms, or immediately when Enter or **Apply Hold** is used.

## Cycle mode

1. Select **Cycle**.
2. Enter high target and high hold time.
3. Enter low target and low hold time.
4. Select **Start Cycle**.
5. Confirm the phase countdown advances HIGH to LOW and repeats.

Cycle timing starts when each goal is sent. It does not wait for measured temperature to reach the goal. Settings are captured when the cycle starts; stop and restart the cycle to apply changed cycle settings.

## Manual control

- **Heat:** requests active-high GPIO13.
- **Cool:** requests active-high GPIO14.
- **Idle:** sets both outputs low.

A manual command stops Cycle first. Firmware prevents simultaneous HEAT and COOL and inserts a 500 ms all-off interval before reversing direction.

## Shutdown

1. Stop Cycle if active.
2. Select **Idle** and confirm `heat=0 cool=0`.
3. Disable external Peltier power.
4. Stop CSV capture and disconnect EtherCAT.
5. Close the GUI, then disconnect bench cables as needed.

## Run acceptance checks

- Both LTC2990 devices remain `GOOD`.
- ATI EtherCAT working counter remains nonzero.
- Force/torque and temperature traces advance continuously.
- Thermal output history matches the commanded mode.
- HEAT and COOL are never active together.
- The run ends in IDLE.

## References

- [Confluence operating procedure](https://docs.globusmedical.com/confluence/spaces/EFLEX/pages/456894964/Peltier+thermal+testbench+-+operating+procedure)
- [Development notes and purchase estimate](https://docs.globusmedical.com/confluence/spaces/EFLEX/pages/446904027/Peltier+thermal+testbench+dev+notes+and+purchase+estimate)
- [GitHub repository](https://github.com/allenglo/ATI-load-cell-ethercat-testbench)
- [Physical setup](https://github.com/allenglo/ATI-load-cell-ethercat-testbench/blob/main/docs/PHYSICAL_SETUP.md)
- [Python GUI](https://github.com/allenglo/ATI-load-cell-ethercat-testbench/blob/main/host-tools/launchpad_loadcell_live_gui.py)
- [ESP32-S3 firmware](https://github.com/allenglo/ATI-load-cell-ethercat-testbench/blob/main/firmware/esp32s3/src/main.cpp)
