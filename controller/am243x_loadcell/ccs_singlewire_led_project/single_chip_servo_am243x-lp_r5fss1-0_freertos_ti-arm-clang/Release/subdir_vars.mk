################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Add inputs and outputs from these tool invocations to the build variables 
SYSCFG_SRCS += \
../example.syscfg 

C_SRCS += \
../CUST_PHY_base.c \
../CUST_PHY_dp83869.c \
../ESL_BOARD_OS_config_tidep_01032.c \
../ESL_OS_os.c \
../ESL_cia402Demo_tidep_01032.c \
../ESL_cia402Obd.c \
../ESL_eeprom_tidep_01032.c \
../ESL_fileHandling.c \
../ESL_foeDemo.c \
../ESL_gpioHelper.c \
../ESL_soeDemo.c \
../ESL_version.c \
../EtherCAT_Slave_CiA402_tidep_01032.c \
../ecSlvCiA402.c \
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
../nvm.c \
../nvm_drv_eeprom_tidep_01032.c \
../nvm_drv_flash.c 

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
./ESL_BOARD_OS_config_tidep_01032.d \
./ESL_OS_os.d \
./ESL_cia402Demo_tidep_01032.d \
./ESL_cia402Obd.d \
./ESL_eeprom_tidep_01032.d \
./ESL_fileHandling.d \
./ESL_foeDemo.d \
./ESL_gpioHelper.d \
./ESL_soeDemo.d \
./ESL_version.d \
./EtherCAT_Slave_CiA402_tidep_01032.d \
./ecSlvCiA402.d \
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
./nvm_drv_eeprom_tidep_01032.d \
./nvm_drv_flash.d 

OBJS += \
./CUST_PHY_base.o \
./CUST_PHY_dp83869.o \
./ESL_BOARD_OS_config_tidep_01032.o \
./ESL_OS_os.o \
./ESL_cia402Demo_tidep_01032.o \
./ESL_cia402Obd.o \
./ESL_eeprom_tidep_01032.o \
./ESL_fileHandling.o \
./ESL_foeDemo.o \
./ESL_gpioHelper.o \
./ESL_soeDemo.o \
./ESL_version.o \
./EtherCAT_Slave_CiA402_tidep_01032.o \
./ecSlvCiA402.o \
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
./nvm_drv_eeprom_tidep_01032.o \
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
./syscfg/ti_pru_io_config.inc \
./syscfg/linker_defines.h 

GEN_MISC_DIRS__QUOTED += \
"syscfg" 

OBJS__QUOTED += \
"CUST_PHY_base.o" \
"CUST_PHY_dp83869.o" \
"ESL_BOARD_OS_config_tidep_01032.o" \
"ESL_OS_os.o" \
"ESL_cia402Demo_tidep_01032.o" \
"ESL_cia402Obd.o" \
"ESL_eeprom_tidep_01032.o" \
"ESL_fileHandling.o" \
"ESL_foeDemo.o" \
"ESL_gpioHelper.o" \
"ESL_soeDemo.o" \
"ESL_version.o" \
"EtherCAT_Slave_CiA402_tidep_01032.o" \
"ecSlvCiA402.o" \
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
"nvm_drv_eeprom_tidep_01032.o" \
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
"syscfg\ti_pru_io_config.inc" \
"syscfg\linker_defines.h" 

C_DEPS__QUOTED += \
"CUST_PHY_base.d" \
"CUST_PHY_dp83869.d" \
"ESL_BOARD_OS_config_tidep_01032.d" \
"ESL_OS_os.d" \
"ESL_cia402Demo_tidep_01032.d" \
"ESL_cia402Obd.d" \
"ESL_eeprom_tidep_01032.d" \
"ESL_fileHandling.d" \
"ESL_foeDemo.d" \
"ESL_gpioHelper.d" \
"ESL_soeDemo.d" \
"ESL_version.d" \
"EtherCAT_Slave_CiA402_tidep_01032.d" \
"ecSlvCiA402.d" \
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
"nvm_drv_eeprom_tidep_01032.d" \
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
"../CUST_PHY_base.c" \
"../CUST_PHY_dp83869.c" \
"../ESL_BOARD_OS_config_tidep_01032.c" \
"../ESL_OS_os.c" \
"../ESL_cia402Demo_tidep_01032.c" \
"../ESL_cia402Obd.c" \
"../ESL_eeprom_tidep_01032.c" \
"../ESL_fileHandling.c" \
"../ESL_foeDemo.c" \
"../ESL_gpioHelper.c" \
"../ESL_soeDemo.c" \
"../ESL_version.c" \
"../EtherCAT_Slave_CiA402_tidep_01032.c" \
"../ecSlvCiA402.c" \
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
"../nvm.c" \
"../nvm_drv_eeprom_tidep_01032.c" \
"../nvm_drv_flash.c" 

SYSCFG_SRCS__QUOTED += \
"../example.syscfg" 


