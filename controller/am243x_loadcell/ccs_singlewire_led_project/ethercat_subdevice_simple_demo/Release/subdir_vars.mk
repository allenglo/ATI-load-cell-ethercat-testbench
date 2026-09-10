################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Add inputs and outputs from these tool invocations to the build variables 
SYSCFG_SRCS += \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/am243x-lp/r5fss0-0_freertos/example.syscfg 

C_SRCS += \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_base.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_dp83869.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/board/am243x-lp/freertos/ESL_BOARD_OS_config.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_OS_os.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_eeprom.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_eoeDemo.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_fileHandling.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_foeDemo.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_gpioHelper.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_soeDemo.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/ESL_version.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/EtherCAT_SubDevice_Simple.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/ecSubDeviceSimple.c \
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
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/app/src/nvm.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/drv/src/nvm_drv_eeprom.c \
C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/drv/src/nvm_drv_flash.c 

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
./ESL_BOARD_OS_config.d \
./ESL_OS_os.d \
./ESL_eeprom.d \
./ESL_eoeDemo.d \
./ESL_fileHandling.d \
./ESL_foeDemo.d \
./ESL_gpioHelper.d \
./ESL_soeDemo.d \
./ESL_version.d \
./EtherCAT_SubDevice_Simple.d \
./ecSubDeviceSimple.d \
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
./nvm.d \
./nvm_drv_eeprom.d \
./nvm_drv_flash.d 

OBJS += \
./CUST_PHY_base.o \
./CUST_PHY_dp83869.o \
./ESL_BOARD_OS_config.o \
./ESL_OS_os.o \
./ESL_eeprom.o \
./ESL_eoeDemo.o \
./ESL_fileHandling.o \
./ESL_foeDemo.o \
./ESL_gpioHelper.o \
./ESL_soeDemo.o \
./ESL_version.o \
./EtherCAT_SubDevice_Simple.o \
./ecSubDeviceSimple.o \
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
./nvm.o \
./nvm_drv_eeprom.o \
./nvm_drv_flash.o 

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
"ESL_BOARD_OS_config.o" \
"ESL_OS_os.o" \
"ESL_eeprom.o" \
"ESL_eoeDemo.o" \
"ESL_fileHandling.o" \
"ESL_foeDemo.o" \
"ESL_gpioHelper.o" \
"ESL_soeDemo.o" \
"ESL_version.o" \
"EtherCAT_SubDevice_Simple.o" \
"ecSubDeviceSimple.o" \
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
"nvm.o" \
"nvm_drv_eeprom.o" \
"nvm_drv_flash.o" 

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
"ESL_BOARD_OS_config.d" \
"ESL_OS_os.d" \
"ESL_eeprom.d" \
"ESL_eoeDemo.d" \
"ESL_fileHandling.d" \
"ESL_foeDemo.d" \
"ESL_gpioHelper.d" \
"ESL_soeDemo.d" \
"ESL_version.d" \
"EtherCAT_SubDevice_Simple.d" \
"ecSubDeviceSimple.d" \
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
"nvm.d" \
"nvm_drv_eeprom.d" \
"nvm_drv_flash.d" 

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
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/board/am243x-lp/freertos/ESL_BOARD_OS_config.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_OS_os.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_eeprom.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_eoeDemo.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_fileHandling.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_foeDemo.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_gpioHelper.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_soeDemo.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/ESL_version.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/EtherCAT_SubDevice_Simple.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/ecSubDeviceSimple.c" \
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
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/app/src/nvm.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/drv/src/nvm_drv_eeprom.c" \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/drv/src/nvm_drv_flash.c" 

SYSCFG_SRCS__QUOTED += \
"C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/am243x-lp/r5fss0-0_freertos/example.syscfg" 


