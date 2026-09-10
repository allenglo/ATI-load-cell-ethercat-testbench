################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Add inputs and outputs from these tool invocations to the build variables 
SYSCFG_SRCS += \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/standard/rgmii/am243x-lp/r5fss0-0_freertos/example.syscfg 

C_SRCS += \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_base.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_dp83869.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/app.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/app_task.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_app.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_board.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_cpu_main.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_mem.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_os.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/cust_drivers.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/eeprom/cust_eeprom.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/ethphy/cust_ethphy.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/flash/cust_flash.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/led/cust_led.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_cfg.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/device_profile_intf.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_nvm.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_reset.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/drivers.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/board/drv_board.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/common/drv_common.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/eeprom/drv_eeprom.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/flash/drv_flash.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/led/drv_led.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/pruicss/drv_pruicss.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/uart/drv_uart.c \
./syscfg/ti_dpl_config.c \
./syscfg/ti_drivers_config.c \
./syscfg/ti_drivers_open_close.c \
./syscfg/ti_pinmux_config.c \
./syscfg/ti_power_clock_config.c \
./syscfg/ti_board_config.c \
./syscfg/ti_board_open_close.c \
./syscfg/ti_enet_config.c \
./syscfg/ti_enet_open_close.c \
./syscfg/ti_enet_soc.c \
./syscfg/ti_enet_lwipif.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/generic_device.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/generic_device_cfg.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/services/web_server/web_server.c 

GEN_CMDS += \
./syscfg/linker.cmd 

GEN_FILES += \
./syscfg/ti_dpl_config.c \
./syscfg/ti_drivers_config.c \
./syscfg/ti_drivers_open_close.c \
./syscfg/ti_pinmux_config.c \
./syscfg/ti_power_clock_config.c \
./syscfg/ti_board_config.c \
./syscfg/ti_board_open_close.c \
./syscfg/ti_enet_config.c \
./syscfg/ti_enet_open_close.c \
./syscfg/ti_enet_soc.c \
./syscfg/ti_enet_lwipif.c \
./syscfg/linker.cmd 

GEN_MISC_DIRS += \
./syscfg 

C_DEPS += \
./CUST_PHY_base.d \
./CUST_PHY_dp83869.d \
./app.d \
./app_task.d \
./cmn_app.d \
./cmn_board.d \
./cmn_cpu_main.d \
./cmn_mem.d \
./cmn_os.d \
./cust_drivers.d \
./cust_eeprom.d \
./cust_ethphy.d \
./cust_flash.d \
./cust_led.d \
./device_profile_cfg.d \
./device_profile_intf.d \
./device_profile_nvm.d \
./device_profile_reset.d \
./drivers.d \
./drv_board.d \
./drv_common.d \
./drv_eeprom.d \
./drv_flash.d \
./drv_led.d \
./drv_pruicss.d \
./drv_uart.d \
./syscfg/ti_dpl_config.d \
./syscfg/ti_drivers_config.d \
./syscfg/ti_drivers_open_close.d \
./syscfg/ti_pinmux_config.d \
./syscfg/ti_power_clock_config.d \
./syscfg/ti_board_config.d \
./syscfg/ti_board_open_close.d \
./syscfg/ti_enet_config.d \
./syscfg/ti_enet_open_close.d \
./syscfg/ti_enet_soc.d \
./syscfg/ti_enet_lwipif.d \
./generic_device.d \
./generic_device_cfg.d \
./web_server.d 

OBJS += \
./CUST_PHY_base.o \
./CUST_PHY_dp83869.o \
./app.o \
./app_task.o \
./cmn_app.o \
./cmn_board.o \
./cmn_cpu_main.o \
./cmn_mem.o \
./cmn_os.o \
./cust_drivers.o \
./cust_eeprom.o \
./cust_ethphy.o \
./cust_flash.o \
./cust_led.o \
./device_profile_cfg.o \
./device_profile_intf.o \
./device_profile_nvm.o \
./device_profile_reset.o \
./drivers.o \
./drv_board.o \
./drv_common.o \
./drv_eeprom.o \
./drv_flash.o \
./drv_led.o \
./drv_pruicss.o \
./drv_uart.o \
./syscfg/ti_dpl_config.o \
./syscfg/ti_drivers_config.o \
./syscfg/ti_drivers_open_close.o \
./syscfg/ti_pinmux_config.o \
./syscfg/ti_power_clock_config.o \
./syscfg/ti_board_config.o \
./syscfg/ti_board_open_close.o \
./syscfg/ti_enet_config.o \
./syscfg/ti_enet_open_close.o \
./syscfg/ti_enet_soc.o \
./syscfg/ti_enet_lwipif.o \
./generic_device.o \
./generic_device_cfg.o \
./web_server.o 

GEN_MISC_FILES += \
./syscfg/ti_dpl_config.h \
./syscfg/ti_drivers_config.h \
./syscfg/ti_drivers_open_close.h \
./syscfg/ti_board_config.h \
./syscfg/ti_board_open_close.h \
./syscfg/ti_enet_config.h \
./syscfg/ti_enet_open_close.h \
./syscfg/ti_enet_lwipif.h \
./syscfg/linker_defines.h 

GEN_MISC_DIRS__QUOTED += \
"syscfg" 

OBJS__QUOTED += \
"CUST_PHY_base.o" \
"CUST_PHY_dp83869.o" \
"app.o" \
"app_task.o" \
"cmn_app.o" \
"cmn_board.o" \
"cmn_cpu_main.o" \
"cmn_mem.o" \
"cmn_os.o" \
"cust_drivers.o" \
"cust_eeprom.o" \
"cust_ethphy.o" \
"cust_flash.o" \
"cust_led.o" \
"device_profile_cfg.o" \
"device_profile_intf.o" \
"device_profile_nvm.o" \
"device_profile_reset.o" \
"drivers.o" \
"drv_board.o" \
"drv_common.o" \
"drv_eeprom.o" \
"drv_flash.o" \
"drv_led.o" \
"drv_pruicss.o" \
"drv_uart.o" \
"syscfg\ti_dpl_config.o" \
"syscfg\ti_drivers_config.o" \
"syscfg\ti_drivers_open_close.o" \
"syscfg\ti_pinmux_config.o" \
"syscfg\ti_power_clock_config.o" \
"syscfg\ti_board_config.o" \
"syscfg\ti_board_open_close.o" \
"syscfg\ti_enet_config.o" \
"syscfg\ti_enet_open_close.o" \
"syscfg\ti_enet_soc.o" \
"syscfg\ti_enet_lwipif.o" \
"generic_device.o" \
"generic_device_cfg.o" \
"web_server.o" 

GEN_MISC_FILES__QUOTED += \
"syscfg\ti_dpl_config.h" \
"syscfg\ti_drivers_config.h" \
"syscfg\ti_drivers_open_close.h" \
"syscfg\ti_board_config.h" \
"syscfg\ti_board_open_close.h" \
"syscfg\ti_enet_config.h" \
"syscfg\ti_enet_open_close.h" \
"syscfg\ti_enet_lwipif.h" \
"syscfg\linker_defines.h" 

C_DEPS__QUOTED += \
"CUST_PHY_base.d" \
"CUST_PHY_dp83869.d" \
"app.d" \
"app_task.d" \
"cmn_app.d" \
"cmn_board.d" \
"cmn_cpu_main.d" \
"cmn_mem.d" \
"cmn_os.d" \
"cust_drivers.d" \
"cust_eeprom.d" \
"cust_ethphy.d" \
"cust_flash.d" \
"cust_led.d" \
"device_profile_cfg.d" \
"device_profile_intf.d" \
"device_profile_nvm.d" \
"device_profile_reset.d" \
"drivers.d" \
"drv_board.d" \
"drv_common.d" \
"drv_eeprom.d" \
"drv_flash.d" \
"drv_led.d" \
"drv_pruicss.d" \
"drv_uart.d" \
"syscfg\ti_dpl_config.d" \
"syscfg\ti_drivers_config.d" \
"syscfg\ti_drivers_open_close.d" \
"syscfg\ti_pinmux_config.d" \
"syscfg\ti_power_clock_config.d" \
"syscfg\ti_board_config.d" \
"syscfg\ti_board_open_close.d" \
"syscfg\ti_enet_config.d" \
"syscfg\ti_enet_open_close.d" \
"syscfg\ti_enet_soc.d" \
"syscfg\ti_enet_lwipif.d" \
"generic_device.d" \
"generic_device_cfg.d" \
"web_server.d" 

GEN_FILES__QUOTED += \
"syscfg\ti_dpl_config.c" \
"syscfg\ti_drivers_config.c" \
"syscfg\ti_drivers_open_close.c" \
"syscfg\ti_pinmux_config.c" \
"syscfg\ti_power_clock_config.c" \
"syscfg\ti_board_config.c" \
"syscfg\ti_board_open_close.c" \
"syscfg\ti_enet_config.c" \
"syscfg\ti_enet_open_close.c" \
"syscfg\ti_enet_soc.c" \
"syscfg\ti_enet_lwipif.c" \
"syscfg\linker.cmd" 

C_SRCS__QUOTED += \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_base.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_dp83869.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/app.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/app_task.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_app.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_board.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_cpu_main.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_mem.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_os.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/cust_drivers.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/eeprom/cust_eeprom.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/ethphy/cust_ethphy.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/flash/cust_flash.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/led/cust_led.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_cfg.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/device_profile_intf.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_nvm.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_reset.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/drivers.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/board/drv_board.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/common/drv_common.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/eeprom/drv_eeprom.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/flash/drv_flash.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/led/drv_led.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/pruicss/drv_pruicss.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/uart/drv_uart.c" \
"./syscfg/ti_dpl_config.c" \
"./syscfg/ti_drivers_config.c" \
"./syscfg/ti_drivers_open_close.c" \
"./syscfg/ti_pinmux_config.c" \
"./syscfg/ti_power_clock_config.c" \
"./syscfg/ti_board_config.c" \
"./syscfg/ti_board_open_close.c" \
"./syscfg/ti_enet_config.c" \
"./syscfg/ti_enet_open_close.c" \
"./syscfg/ti_enet_soc.c" \
"./syscfg/ti_enet_lwipif.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/generic_device.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/generic_device_cfg.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/services/web_server/web_server.c" 

SYSCFG_SRCS__QUOTED += \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/standard/rgmii/am243x-lp/r5fss0-0_freertos/example.syscfg" 


