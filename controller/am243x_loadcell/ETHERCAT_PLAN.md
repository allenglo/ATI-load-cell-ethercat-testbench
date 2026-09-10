# EtherCAT Slave Integration Plan - AM243x LaunchPad + Kuka + ATI Mini45

> Status note (2026-05-18): This file is historical planning content for an older slave-focused lane.
> Active execution for current host-lane work is tracked in `notes/host_master/EXECUTION_PLAN_20260518.md`.

**Date Started:** May 6, 2026  
**Status:** Planning Phase  
**Objective:** Port dual RGB LED control functions into EtherCAT slave stack for Kuka robotics + ATI Mini45 Blue board

---

## 1. Executive Summary

Transform AM243x LaunchPad from standalone LED controller (SPI + GPIO chains) into an industrial EtherCAT slave that:
- Acts as **slave to Kuka robotics controller** (master)
- Provides RGB LED control via EtherCAT Process Data Objects (PDOs)
- Communicates with **ATI Industrial Automation Mini45 EtherCAT Blue board** (next-layer slave)
- Maintains existing serial debug interface for offline testing

**Key Architecture:** Kuka Master ← EtherCAT Link → AM243x Slave ← EtherCAT Link → ATI Mini45 Blue Slave

---

## 2. Technical Foundation

### 2.1 Hardware Inventory
- **Master Compute:** AM243x LaunchPad, Cortex-R5 @ 800 MHz
- **Networking:** Dual Ethernet ports (Gigabit capable)
- **LED Chains (retained from Phase 4):**
  - SPI0 MCSPI0 @ 10 MHz → 16× WS2812 on pin 55 (SPI0_D0)
  - GPIO1_13 (pin 15) bit-bang → 6× RGB 645/587 on pin 15 (J2.15)
  - Shared brightness control (0-255), separate animation patterns
- **Debug Interface:** UART COM10 @ 115200 (polling-based commands)
- **Boot Modes:**
  - `0100 0100` = OSPI normal (production)
  - `1110 0000` = UART flash (for persistent storage)

### 2.2 EtherCAT Stack Choice: **SOES** (Simple Open Source EtherCAT Slave)
**Rationale:**
- Pure C, minimal footprint (~40K flash, ~4K RAM in CherryECAT sibling)
- Feature-rich: CoE, SDO, dynamic PDO mapping, DC sync
- 797 stars on GitHub, actively maintained
- Production-ready examples (XMC4800, ARM Cortex-M/R)
- BSD-style license, open contribution model

**Key Capabilities:**
- Address offset HAL → easy integration with TI EMAC driver
- Mailbox + data link layer → handles master/slave handshake
- Object Dictionary → CiA 402 and custom objects
- CANopen over EtherCAT (CoE) → standardized PDO descriptors
- Distributed Clock (DC) sync → sub-microsecond timing

### 2.3 Reference Implementations
1. **SOES on GitHub:** https://github.com/OpenEtherCATsociety/SOES
   - Full stack with multiple application examples
   - Supports Infineon XMC, Beckhoff, ARM STM32

2. **XMC4800 Minimal Example:** https://github.com/lzptr/xmc4800_ethercat_example
   - Complete CMake build setup
   - SOES integrated, minimal dependencies
   - Debugging with J-Link (similar to AM243x CCS flow)

3. **CherryECAT Master Stack** (reference for DC timing, multi-domain PDO):
   - Supports HPM6800, STM32H7
   - < 40 µs cycle time, < 3 µs DC jitter
   - RTOS-friendly queue-based architecture

---

## 3. Architecture Design

### 3.1 Module Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│ ecat_slave_main()                                               │
│ Entry point: Initialize ESC, PDO, main loop                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
       ┌─────────────┴─────────────┐
       │                           │
┌──────▼──────────────────┐  ┌────▼──────────────────────┐
│ ecat_esc_hal.c/h        │  │ ecat_pdo_handler.c/h      │
│ HAL layer: ESC access   │  │ PDO in/out callbacks      │
│ (EMAC + ESC register)   │  │ Input: RGB commands       │
│                         │  │ Output: Status, telemetry │
└──────────────────────────┘  └────┬───────────────────────┘
                                   │
                      ┌────────────┴────────────┐
                      │                         │
              ┌───────▼─────────┐     ┌────────▼──────────┐
              │ led_control.c/h │     │ mini45_comms.c/h  │
              │ RGB animation   │     │ EtherCAT → Mini45 │
              │ (wraps existing │     │ Secondary slave   │
              │ addressable_led)│     │ control/status    │
              └─────────────────┘     └───────────────────┘
                      │
              ┌───────▼─────────────────────┐
              │ dual_spi_leds_simple.c      │
              │ Existing LED driver logic   │
              │ (SPI + GPIO bit-bang)       │
              └─────────────────────────────┘
```

### 3.2 EtherCAT PDO Layout (Process Data Objects)

**Master → Slave Input (Kuka writes, AM243x reads):**
```
CoE PDO Index: 0x1602 (RxPDO1 - receive from master)
┌─────────────────────────────────────────────────────┐
│ Byte 0    │ Red value (0-255)                       │
│ Byte 1    │ Green value (0-255)                     │
│ Byte 2    │ Blue value (0-255)                      │
│ Byte 3    │ Control flags:                          │
│           │   Bit 0: Enable animation               │
│           │   Bit 1: Reserved                       │
│           │   Bits 2-7: Animation mode (0-6)        │
│ Byte 4    │ Brightness multiplier (0-255)           │
│ Byte 5    │ Animation speed (step interval ms)      │
│ Byte 6    │ Chain select (bit 0=SPI, bit 1=GPIO)    │
│ Byte 7    │ Reserved                                │
└─────────────────────────────────────────────────────┘
Total: 8 bytes
```

**Slave → Master Output (AM243x writes, Kuka reads):**
```
CoE PDO Index: 0x1A02 (TxPDO1 - transmit to master)
┌──────────────────────────────────────────────────────┐
│ Byte 0    │ Current brightness (readback)            │
│ Byte 1    │ Current R, G, B values (snapshot)        │
│ Byte 2    │ Current G                                │
│ Byte 3    │ Current B                                │
│ Byte 4-5  │ Frame counter (uint16_t, wraps every 18h)│
│ Byte 6    │ Status flags:                            │
│           │   Bit 0: Animation running               │
│           │   Bit 1: Mini45 link up                  │
│           │   Bits 2-7: Error flags                  │
│ Byte 7    │ Mini45 telemetry (FX component, scaled)  │
└──────────────────────────────────────────────────────┘
Total: 8 bytes
```

**Cyclic Timing:**
- **EtherCAT Cycle:** 1 ms (typical for Kuka, configurable via CoE)
- **LED Animation:** 40 ms base (existing code), will sync to EtherCAT cycle
- **Mini45 Polling:** Every EtherCAT cycle if Mini45 is secondary slave, or asynchronous if external

### 3.3 Object Dictionary (OD) - CoE Entries

```
0x1000:  Device Type (uint32_t) = 0x0000002B (Generic I/O)
0x1001:  Error Register (uint8_t)
0x1008:  Device Name (string) = "AM243x-EtherCAT-RGB-LED"
0x1009:  Hardware Version (string)
0x100A:  Firmware Version (string)

0x1600:  RxPDO1 Index (PDO mapping table)
0x1602:  RxPDO1 - 8 bytes (Kuka → RGB control)

0x1A00:  TxPDO1 Index (PDO mapping table)
0x1A02:  TxPDO1 - 8 bytes (Status → Kuka)

0x2000-0x20FF: Vendor-specific LED config (read-only PDO params)
  0x2000: Max LED count per chain
  0x2001: SPI frequency
  0x2002: GPIO bit-bang timing
```

### 3.4 Integration Points with Existing Code

**Retain from Phase 4:**
- `addressable_led.h/c` — HSV→GRB, SPI/GPIO abstraction
- `dual_spi_leds_simple.c` — LED animation logic, brightness control
- Serial debug interface (`poll_uart_commands()`) for offline testing

**New Wrapper Layer:**
- `ecat_slave.c/h` — Main EtherCAT entry point, init + main loop
- `ecat_pdo_handler.c/h` — PDO input/output callbacks
- `led_control.c/h` — Converts EtherCAT RGB commands → existing LED functions
- `mini45_comms.c/h` — (Optional) Secondary EtherCAT slave communication or async Ethernet to ATI board

**Modification Plan:**
1. Replace `dual_spi_leds_main()` call from `main.c` with `ecat_slave_main()`
2. Inside EtherCAT main loop, trigger LED updates on PDO receive
3. Keep serial polling for debug commands (non-blocking, lower priority)
4. Share `gBrightness`, `gStepIntervalUs` globals with EtherCAT PDO handlers

---

## 4. Implementation Roadmap

### Phase 1: Research & Setup ✅ (Today)
- [x] Search for SOES + examples
- [x] Identify key integration points
- [x] Document architecture

### Phase 2: SOES Integration (Est. 2-3 sessions)
**Tasks:**
1. Clone SOES repo, study XMC4800 example structure
2. Create AM243x-specific HAL layer (`ecat_esc_hal.c`)
   - Configure ESC (Ethernet Switch Controller) register access
   - Integrate with TI Ethernet driver (CPSW or EMAC)
   - Implement mailbox ISR (or polling fallback)
3. Port SII (Slave Information Interface) EEPROM config
   - Define PDO descriptors
   - Create Object Dictionary entries

### Phase 3: LED Module Wrapper (Est. 1-2 sessions)
**Tasks:**
1. Create `led_control.c/h` — wraps existing `addressable_led` functions
2. Implement PDO input handler:
   - Parse RGB command from Kuka PDO
   - Apply brightness multiplier
   - Update animation state
3. Implement PDO output handler:
   - Read current LED state
   - Pack status + mini45 telemetry into TxPDO

### Phase 4: Mini45 Integration (Est. 2-3 sessions)
**Tasks:**
1. Research ATI Mini45 EtherCAT Blue board (if available locally) or assume async interface
2. Create `mini45_comms.c/h`:
   - If Mini45 is secondary EtherCAT slave: implement slave chaining (daisy-chain logic)
   - If Mini45 is standalone: implement external Ethernet passthrough or query
3. Map force/torque telemetry → TxPDO byte 7 (scaled)

### Phase 5: Testing & Tuning (Est. 2-3 sessions)
**Tasks:**
1. Flash to AM243x, boot into EtherCAT slave mode
2. Configure Kuka master via TwinCAT or CLI
3. Validate PDO sync:
   - RGB command response latency
   - Animation smoothness at 1 ms cycle
4. Verify Mini45 status passthrough
5. Stress test: sustained operation, sync jitter measurement

---

## 5. Key Technical Decisions

### Decision 1: SOES vs. Alternatives
| Stack | Pros | Cons | Verdict |
|-------|------|------|---------|
| **SOES** | Minimal, C, production-ready | Limited RTOS examples | ✅ **CHOSEN** |
| CherryECAT | Tiny, RTOS-native | Master-focused, less slave examples | Reference only |
| TI Industrial Comms SDK | TI-native | Not yet installed, proprietary | Fallback if SOES issues |

### Decision 2: PDO Mapping Strategy
- **Fixed PDO:** 8 bytes for both RxPDO + TxPDO → No runtime reconfiguration
- **Rationale:** Simplifies EEPROM, fast sync, matches typical Kuka master expectations
- **Flexibility:** Serial debug override if needed

### Decision 3: Mini45 Integration
- **Assumption:** Daisy-chain secondary slave on AM243x's second Ethernet port (if available)
- **Fallback:** Async serial/Ethernet query to Mini45, results cached in TxPDO
- **Status:** Pending hardware availability + Kuka topology feedback

### Decision 4: LED Animation Timing
- **Sync Method:** Tie animation step to EtherCAT cycle (1 ms)
- **Rationale:** Deterministic, avoids jitter, master can adjust speed via PDO
- **Existing Code:** Minimal changes to `dual_spi_leds_simple.c` — just replace timer with EtherCAT event

---

## 6. Compilation & Build Integration

### 6.1 New Build Targets
```bash
# Build SOES slave + LED control
./build_load_run_dual.ps1 -BuildOnly -EtherCAT

# Compile, sign, stage to boot image (OSPI-ready)
./build_load_run_dual.ps1 -BuildOnly -EtherCAT -FlashBoot

# Deploy to board in UART boot mode
./build_load_run_dual.ps1 -FlashOnly -ComPort COM10 -EtherCAT
```

### 6.2 SysConfig Updates
- Enable CPSW (Cyclic Processor Switch) or EMAC for Ethernet
- Leave SPI0, GPIO1_13 as-is (LED chains unchanged)
- Keep UART console active (debug)

### 6.3 TI SDK Dependencies
- **MCU+ SDK v12.00.00.26** (already present)
- **Drivers needed:** CPSW Ethernet, ESC register HAL
- **Optional:** TI Industrial Comms SDK (for Alt. EtherCAT slave if SOES fails)

---

## 7. Testing Strategy

### Phase 1: Offline (No Master)
- [ ] Compile SOES + LED wrapper successfully
- [ ] UART serial commands still work (debug mode)
- [ ] LED chains blink on command

### Phase 2: Isolated Slave
- [ ] Boot in EtherCAT slave mode, LED heartbeat
- [ ] CCS/debugger: Verify ESC state machine transitions
- [ ] Ethernet link status (green LED on board if available)

### Phase 3: With Kuka Master
- [ ] TwinCAT/IgH master discovers AM243x slave
- [ ] PDO sync established (1 ms cycle visible)
- [ ] Send RGB command, verify LED response within 2 ms

### Phase 4: Mini45 Integration
- [ ] ATI Mini45 appears as secondary slave on bus (if daisy-chain)
- [ ] Force/torque data flows to AM243x → Kuka
- [ ] Status flags show Mini45 link health

### Phase 5: Endurance
- [ ] Run 24h animation loop with Kuka PDO updates
- [ ] Monitor Ethernet link, sync jitter, LED stability
- [ ] Confirm no firmware crashes or watchdog resets

---

## 8. Debugging & Troubleshooting

### Common Issues & Resolutions

| Issue | Cause | Resolution |
|-------|-------|------------|
| Master doesn't discover slave | ESC init failed, wrong Ethernet port | Check CCS debugger: CPSW DMA, ESC registers 0x0000 |
| PDO not syncing | Cycle timer misconfigured | Verify SM (Sync Manager) configuration in OD |
| LED lag > 5 ms | Animation priority too high, starving network | Reduce LED update frequency, decouple from PDO |
| Mini45 data missing | Secondary slave not initialized | Debug mini45_comms.c, check Ethernet daisy-chain |
| Frequent sync loss | Jitter > 1 ms | Profile CPU load, reduce LED calculation, enable DC |

### Debug Hooks
- UART still active: `?` command prints EtherCAT cycle count, last PDO timestamp
- CCS breakpoints in `ecat_pdo_handler()` → pause on RGB command
- Ethernet analyzer (Wireshark): Capture EtherCAT frames, verify PDO payload

---

## 9. Success Criteria

✅ **Minimum Viable Product (MVP):**
- AM243x boots as EtherCAT slave
- Kuka master discovers it via ESC
- RGB LED responds to PDO commands within 5 ms
- No crashes over 1-hour continuous operation

✅ **Production Ready:**
- < 1 ms PDO latency
- DC sync jitter < 100 µs
- Mini45 telemetry integrated + status reported
- Persistent OSPI flash stores slave config
- Serial debug interface functional for troubleshooting

---

## 10. Reference Links & Downloads

### Code Repositories
- **SOES:** https://github.com/OpenEtherCATsociety/SOES
- **XMC4800 Example:** https://github.com/lzptr/xmc4800_ethercat_example
- **CherryECAT (for timing inspiration):** https://github.com/cherry-embedded/CherryECAT

### Documentation
- SOES GitHub Wiki: Object Dictionary, CoE, PDO mapping
- EtherCAT Specification (IEC 61158-12) — Ask Kuka for master PDO profile
- ATI Mini45 EtherCAT Manual (to obtain from hardware provider)

### Tools
- **TwinCAT (Windows, free):** Kuka master emulator, ESI file generator
- **IgH EtherCAT Master (Linux):** ethercat CLI for diagnostics
- **Wireshark + EtherCAT dissector:** Network frame analysis

---

## 11. Progress Log

### 2026-05-06 (Today)
- ✅ Research complete: SOES identified as primary stack
- ✅ XMC4800 example studied for architecture template
- ✅ Architecture plan drafted (this document)
- ✅ PDO layout designed for RGB + Mini45
- **Next:** Clone SOES, begin HAL implementation

### Session Notes (To be updated as work progresses)
- [Session 1] SOES HAL layer + AM243x Ethernet integration
- [Session 2] Object Dictionary, EEPROM SII configuration
- [Session 3] PDO handler, LED wrapper module
- [Session 4] Mini45 communication strategy
- [Session 5] End-to-end integration test with mock Kuka master

---

**Document Maintainer:** AI Agent  
**Last Updated:** 2026-05-06  
**Status:** DRAFT — Awaiting SOES integration begin
