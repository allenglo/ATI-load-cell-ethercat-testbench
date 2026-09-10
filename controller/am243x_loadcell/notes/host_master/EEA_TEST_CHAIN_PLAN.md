# EEA Test Chain Plan (Same GUI Path)

## Current state

- Existing GUI is now upgraded to a unified EtherCAT GUI.
- Supports two profiles:
  - ATI Load Cell
  - EEA Reverse Engineering
- EEA packet conversion scheme is not explicitly documented in local notes yet.

## What works now

1. Connect to EtherCAT adapter.
2. Select profile:
   - `ATI Load Cell` uses known 6x int32 decode (Fx/Fy/Fz/Tx/Ty/Tz).
   - `EEA Reverse Engineering` decodes candidate channels (`C1..C6`) from raw PDO payload.
3. Watch live raw hex and decoded lines in one stream.
4. Enable CSV capture for reverse-engineering (`timestamp, profile, wkc, raw_hex, decoded_json`).
5. Use control hooks in the same GUI:
   - PDO output write (hex)
   - SDO read
   - SDO write (`u8/u16/u32/i32/f32`)

## Reverse-engineering workflow

1. Connect with `EEA Reverse Engineering` profile.
2. Enter slave-name hint (optional) to force target selection.
3. Start capture to CSV.
4. Apply one control action at a time (PDO or SDO).
5. Correlate command vs returned payload changes.
6. Build final conversion map from stable correlations.

## Final target

- Replace provisional `C1..C6` fields with validated EEA semantic fields.
- Keep same GUI, just switch profile to `EEA` with final decoder + command map.
