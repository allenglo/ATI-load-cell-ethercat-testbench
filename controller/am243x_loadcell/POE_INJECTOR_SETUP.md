# Antaira LNP-0500G-BT-24 Series PoE Injector
## Quick Reference & Troubleshooting

---

## **What You Have**

- **5 RJ45 Ports:**
  - **Port 0 (INPUT):** 24V DC power barrel connector (where you plugged 24V)
  - **Ports 1-4 (OUTPUTS):** Ethernet data + PoE power combined on RJ45

- **Not a Managed Switch:** No web interface, no IP address, no VLAN config. It's purely passive.

- **Power Rating:** ~90W total PoE+ output across all 4 ports (~22W per port typical max)

---

## **LED Status Guide**

| LED | Color | Meaning |
|-----|-------|---------|
| POWER | Green | 24V input is good |
| FAULT | Red (on) | One or more outputs have a problem |
| LINK | Green (per port) | Device detected on that port, proper handshake |
| LINK | Off | No device, bad cable, or device not responding |

---

## **Why FAULT is Lit (Most Likely Causes)**

1. **Port Overload:** One device drawing too much current
   - Load cell boards can sometimes draw 1-2A if motor drivers are active
   - LaunchPad Ethernet alone is only ~100-200mA
   - USB-to-Eth is usually passive ~100mA

2. **Short Circuit:** Bare wires, wet connector, or bad RJ45 crimping

3. **Bad Cable:** Open/crossed pairs in one of the cables you're using

4. **Device Fault:** The device connected to that port is shorting the supply

---

## **Recommended Port Assignment**

Since you have the injector (low-power PoE) and three devices:

| Port | Device | Reason |
|------|--------|--------|
| **Port 1** | **Load Cell** | Higher current draw, isolated from master |
| **Port 2** | **TI LaunchPad** | Moderate draw, needs to talk to master |
| **Port 3** | **USB-to-Eth adapter (PC)** | Low draw, master control point |
| Port 4 | *unused* | Reserve for future |

---

## **Immediate Actions**

### **Action 1: Isolate the Fault**
```powershell
# Power off the injector
# Disconnect ALL three devices
# Power on injector
# Observe: Does FAULT LED turn OFF?

If YES:   One of your devices is the problem (go to Action 2)
If NO:    Power supply is the issue (check 24V barrel, cables, polarity)
```

### **Action 2: Test One Device at a Time**
```powershell
# With injector powered and FAULT off:

# Step A: Plug ONLY load cell into Port 1
# Wait 10 seconds
# Is FAULT still off? [YES=OK, NO=LOAD CELL BAD]

# Step B: Unplug load cell, plug TI LaunchPad into Port 2
# Wait 10 seconds
# Is FAULT still off? [YES=OK, NO=LAUNCHPAD BAD]

# Step C: Unplug LaunchPad, plug USB-Eth into Port 3
# Wait 10 seconds
# Is FAULT still off? [YES=OK, NO=ADAPTER BAD]
```

### **Action 3: Verify Cables**
- Use a dedicated cable tester or swap cables
- Look for any visible damage (kinks, bent pins)
- Ensure CAT6 or better (CAT5e minimum)
- The injector will fault on ANY port with a bad cable

---

## **Once FAULT is Off: Test Connectivity**

Run on your PC:
```powershell
# Open PowerShell and run:
.\discover_ethernet_devices.ps1

# OR manually:
ping 192.168.1.100    # Load cell default
ping 10.0.0.100       # Alternative default
ping 169.254.1.1      # APIPA fallback

# Check ARP to see which devices the PC has seen:
arp -a
```

---

## **Device Expected Configs**

### Load Cell Board
- Likely default IP: **192.168.1.100** or **10.0.0.100**
- Port: **502** (Modbus TCP) or **5000** (HTTP config)
- Check the label on the board or manual

### TI LaunchPad (AM243x)
- Default: **DHCP** or **169.254.x.x (APIPA)**
- You can set a static IP in `example.syscfg`
- Ethernet PHY is configured but may not respond until app is running

### USB-to-Eth Adapter
- Windows will auto-assign APIPA (169.254.x.x)
- Appears as "USB Ethernet" or "Local Area Connection" in Network Settings

---

## **Access the Injector's Managed Features (IF NEEDED)**

⚠ **Wait — Your injector is NOT managed.** The LNP-0500G-BT-24 is a pure passive injector. If you need a managed PoE switch, you'd need a different model (e.g., Antaira's managed line with SNMP/SSH).

---

## **Wiring Diagram**

```
                       ┌─────────────────────┐
                       │ LNP-0500G-BT-24     │
                       │ PoE Injector        │
                       │                     │
    24V DC Input       │  V1─────┐          │
    (Barrel Jack)──────┤  V2─────┤ PWR     │
                       │         └──┐       │
                       │            │       │
                       │ Port 1     │ ┌─────────┐
    Load Cell Board ────┤ (Eth1)    │ │ Supply  │
                       │            │ └─────────┘
                       │ Port 2     │
    TI LaunchPad ───────┤ (Eth2)    │
                       │            │
                       │ Port 3     │
    PC USB-to-Eth ──────┤ (Eth3)    │
                       │            │
                       │ Port 4     │
    (unused) ──────────┤ (Eth4)    │
                       │            │
                       └────────────┘
```

---

## **Contact Info for Support**

- **Antaira Support:** +1-714-671-9000
- **Email:** INFO@ANTAIRA.COM
- Have your model number ready: **LNP-0500G-BT-24**

