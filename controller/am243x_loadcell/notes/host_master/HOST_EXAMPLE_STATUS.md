# Host Example Status (AM2434-LP)

## Updated: 2026-05-14

### New CCS Imports (installed via CCS Resource Explorer)

All imported into CCS workspace (located inside `ccs_singlewire_led_project/` — inherited name, treat as general AM243x workspace):

| Project | Core | OS | Notes |
|---------|------|----|-------|
| ethercat_subdevice_simple_demo | R5FSS0-0 | FreeRTOS | Best subdevice code reference |
| ethercat_subdevice_ctt_demo | R5FSS0-0 | FreeRTOS | CTT compliance ref |
| ethercat_subdevice_cia402_demo | R5FSS0-0 | FreeRTOS | CiA402 drive profile ref |
| single_chip_servo (system) | R5FSS0-0/0-1/1-0 | NORTOS+FreeRTOS | EtherCAT-connected dual servo motor system |
| uart_echo | R5FSS0-0 | NORTOS | UART baseline for COM10 printout |
| dpl_demo | R5FSS0-0 | NORTOS | Hello World / DPL baseline |

Auto-installed dependencies (from CCS installer dialog):
- MOTOR CONTROL SDK for AM243x v09.02.00.12
- SysConfig v1.20.0
- TI Arm Clang Compiler v3.02.02.00

### Original Result (still true for MainDevice)
- No EtherCAT host/main-device example is present in any installed SDK.

Checked:
1. C:\ti\ind_comms_sdk_am243x_11_00_00_08\examples\industrial_comms
- ethercat_iolink_gateway_demo
- ethercat_slave_beckhoff_ssc_demo
- ethercat_subdevice_demo
- (all EtherCAT entries are slave/subdevice side)

2. Project metadata search (example.projectspec)
- Titles/descriptions found only:
  - Ethercat Subdevice *
  - Ethercat Slave Beckhoff SSC *
  - Ethercat Iolink Gateway *
- No "master" or "maindevice" project target.

3. Source/API symbol search
- Found EC slave API references (EC_API_SLV_*) and comments about EtherCAT master requests.
- No EC_API_MD or EtherCAT main-device API implementation found.

Meaning:
- We should NOT edit subdevice examples pretending they are host examples.

Single next action:
- Install/import an actual AM243x EtherCAT main-device/host stack example package first.
- After that, patch that host example to print ATI Fx/Fy/Fz/Tx/Ty/Tz over COM10.
