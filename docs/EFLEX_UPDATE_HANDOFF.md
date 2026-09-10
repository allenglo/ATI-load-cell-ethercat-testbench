# EFlex EEA/Palm Update Task Handoff

Last updated: 2026-08-19

## Start Here

This folder contains the investigation, recovered CalibrationBench source, firmware images, build projects, logs, and the published Giga flasher release.

Current standalone release:

- GitHub: https://github.com/allenglo/GENU-Calibration-Testbench-Flasher
- Local project: `calibrationbench_giga\`
- Published source/artifact copy: `source\calibration_bench\INR_mechatronics\INR_mechatronics-main\GENU-Calibration-Testbench-Flasher_publish\`
- Giga firmware: `1.2.0`
- Binary: `release\CalibrationBench_Giga_1.2.0.bin`
- SHA-256: `403E92A2C5A1BECF2017F80EB8D557EC4352D6309217721EBF2F8E2D0BAFD229`
- Latest published commit: `f6a370d Add LED Palm verification action`

## Timeline

- **2026-08-14:** Reproduced the original PC/USB-to-RS-485 update path. COM11 and the first COM13 attempts timed out before the first bootloader status read. This was recorded as a transport/polling failure, not a successful flash.
- **2026-08-14:** Corrected the target/address workflow and flashed controlled EEA Kit firmware `6221.5000.0270 Rev 2` to EEA nodes 1, 2, and 3. Pages 64-159, image CRC `0x78FF9E8A`; independent FC4 reads confirmed application response after flashing.
- **2026-08-14:** Restored the original CalibrationBench source from `INR_mechatronics-main.zip` into a separate PlatformIO Arduino Giga project. Display, touch, LVGL 8 compatibility, DFRobot RTU, calibration state machine, ROI, board, and EEA workflows were restored.
- **2026-08-14:** Added the onboard updater so the Giga contains the controlled image and no longer needs a PC Python loader for normal EEA/Palm updates. Modbus polling pauses while flashing to prevent Failure Mode 1 interference.
- **2026-08-14:** Updated the visible menu after Hongbo's review. EEA Rev 2 is limited to addresses 1-3; Palm Rev 1 is limited to address 4. The old EEA Rev 1 option is hidden.
- **2026-08-14:** Added non-destructive `READ / VERIFY` actions for the EEA Kit and LED Palm board.
- **2026-08-14 onward:** Published the source, binary, checksum, and operator notes to GitHub. Additional Giga gateway boxes were successfully updated on COM21, COM23, COM20, and COM26, each entering DFU `2341:0366` and returning as a normal Giga `2341:0266` device. COM28 was also successfully updated on 2026-08-19.

## What Changed

### Old workflow

A PC Python loader streamed a HEX file through a USB-to-RS-485 bridge. The bridge and the CalibrationBench application could compete for `Serial1`/RS-485 traffic, causing timeouts and misleading loader exit results.

### Current workflow

The Arduino Giga runs the CalibrationBench UI and contains both approved application images:

| UI choice | Target | Image | Pages | CRC-32 |
|---|---|---|---:|---:|
| EEA Kit Firmware | Slave/address 1, 2, or 3 | `6221.5000.0270 Rev 2` | 64-159 | `0x78FF9E8A` |
| LED Palm Firmware | Palm board/address 4 | `6258.5000.0653 Rev 1` | 64-154 | `0x82FF69B1` |

The updater performs bootloader entry, erase, page writes, CRC verification, EEPROM CRC write, and application restart. It validates the image/address pairing and pauses normal Modbus polling during the operation.

## Field Service Procedure: EEA and Palm Firmware

The current field-service reference named by the release documentation is:

- **6221.9100.0302 Rev 1 - Field procedure, EFlex-TKA Planar End Effector Calibration**
- Confluence reference: https://docs.globusmedical.com/confluence/spaces/GRS/pages/266866019/Obsolete+REPLACEMENT+LINK+ON+PAGE+6221.9100.0302+Rev+1+-+Field+procedure+EFlex-TKA+Planar+End+Effector+Calibration

The page requires authenticated Confluence access and its title identifies it as an obsolete replacement-link page. Treat the authenticated/current controlled document as the authority for the full calibration sequence, fixture setup, acceptance criteria, and release records. The local release notes only define the firmware-update portion below.

### Firmware-update portion

1. Use a powered CalibrationBench/Giga fixture with the correct EEA or Palm target physically connected. Keep power and RS-485 connected during the update.
2. On the Giga touch screen, open the firmware/update menu.
3. Before writing, use the matching `READ / VERIFY` action:
   - `READ / VERIFY EEA KIT` checks addresses 1-3.
   - `READ / VERIFY LED PALM` checks address 4.
4. For an EEA Kit update, choose `EEA Kit Firmware - 6221.5000.0270 Rev 2`, then select only the physical slave being updated: address 1, 2, or 3.
5. For a Palm update, choose `LED Palm Firmware - 6258.5000.0653 Rev 1`, then select `PALM BOARD: ADDRESS 4`.
6. Start the update and wait for the display to report completion. Do not disconnect power, USB, or RS-485. The display reports bootloader entry, erase, page progress, CRC, completion, or communication failure.
7. Run the matching `READ / VERIFY` action again after the update and confirm the target responds.
8. Continue with the authenticated `6221.9100.0302 Rev 1` field procedure for calibration and acceptance testing. Record the target address, image/revision, result, and any required service traceability.

### Important restrictions

- Do not use the hidden EEA Rev 1 path.
- Do not use the EEA image on address 4.
- Do not use the Palm image on addresses 1-3.
- A completion message alone is not sufficient evidence; perform the read/verify step after flashing.
- Do not disconnect during an active update.
- `1.1.1` refers to the older historical CalibrationBench software revision that changed the S1 lock and offset position. The current standalone Giga flasher release is `1.2.0`.

## Build / Recovery Notes

For source work, use PlatformIO environment `giga_calibrationbench` in `calibrationbench_giga`:

```powershell
Set-Location 'C:\CoRoot\##TASKS##\#End Effector Update\calibrationbench_giga'
& 'C:\CoRoot\.venv\Scripts\python.exe' -m platformio run -e giga_calibrationbench
```

For a Giga upload, first identify the port and confirm `VID_2341&PID_0266` with bus description `Giga`. Then use:

```powershell
& 'C:\CoRoot\.venv\Scripts\python.exe' -m platformio run -e giga_calibrationbench --target upload --upload-port COM##
```

Expected DFU identity is `2341:0366`. The current successful build uses about 80.4% flash and 21.0% RAM.

## Source of Truth

- Local working source: `calibrationbench_giga\`
- Published source and release: `source\calibration_bench\INR_mechatronics\INR_mechatronics-main\GENU-Calibration-Testbench-Flasher_publish\`
- Controlled EEA source/image evidence: `source\6221.5000.0270_rev2\`
- Historical PC loader: `source\flash_loader\sharepoint_2026-08-12\flash_loader\`
- Detailed release notes: `...\GENU-Calibration-Testbench-Flasher_publish\CalibrationBench_README.md`

Do not modify the controlled firmware images or claim a field update succeeded without target communication evidence.
