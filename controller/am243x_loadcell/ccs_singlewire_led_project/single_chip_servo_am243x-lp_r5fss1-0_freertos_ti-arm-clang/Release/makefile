################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

CG_TOOL_ROOT := C:/ti/ti_cgt_arm_llvm_3.2.2.LTS

GEN_OPTS__FLAG := 
GEN_CMDS__FLAG := -Wl,-l"syscfg/linker.cmd" 

ORDERED_OBJS += \
"./CUST_PHY_base.o" \
"./CUST_PHY_dp83869.o" \
"./ESL_BOARD_OS_config_tidep_01032.o" \
"./ESL_OS_os.o" \
"./ESL_cia402Demo_tidep_01032.o" \
"./ESL_cia402Obd.o" \
"./ESL_eeprom_tidep_01032.o" \
"./ESL_fileHandling.o" \
"./ESL_foeDemo.o" \
"./ESL_gpioHelper.o" \
"./ESL_soeDemo.o" \
"./ESL_version.o" \
"./EtherCAT_Slave_CiA402_tidep_01032.o" \
"./ecSlvCiA402.o" \
"./syscfg/ti_dpl_config.o" \
"./syscfg/ti_drivers_config.o" \
"./syscfg/ti_drivers_open_close.o" \
"./syscfg/ti_pinmux_config.o" \
"./syscfg/ti_power_clock_config.o" \
"./syscfg/ti_board_config.o" \
"./syscfg/ti_board_open_close.o" \
"./syscfg/ti_enet_config.o" \
"./syscfg/ti_enet_open_close.o" \
"./syscfg/ti_enet_soc.o" \
"./syscfg/ti_enet_lwipif.o" \
"./nvm.o" \
"./nvm_drv_eeprom_tidep_01032.o" \
"./nvm_drv_flash.o" \
$(GEN_CMDS__FLAG) \
-Wl,-llibc.a \
-Wl,-llibsysbm.a \
-Wl,-lfreertos.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-ldrivers.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-lboard.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-lethercat_slave.am243x_lp.r5f.ti-arm-clang.release.lib \
-Wl,-lethercat_slave_bkhf_ssc.am243x_lp.r5f.ti-arm-clang.release.lib \

-include ../makefile.init

RM := DEL /F
RMDIR := RMDIR /S/Q

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir_vars.mk
-include subdir_rules.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C55_DEPS)),)
-include $(C55_DEPS)
endif
ifneq ($(strip $(C_UPPER_DEPS)),)
-include $(C_UPPER_DEPS)
endif
ifneq ($(strip $(S67_DEPS)),)
-include $(S67_DEPS)
endif
ifneq ($(strip $(S62_DEPS)),)
-include $(S62_DEPS)
endif
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(OPT_DEPS)),)
-include $(OPT_DEPS)
endif
ifneq ($(strip $(C??_DEPS)),)
-include $(C??_DEPS)
endif
ifneq ($(strip $(ASM_UPPER_DEPS)),)
-include $(ASM_UPPER_DEPS)
endif
ifneq ($(strip $(S??_DEPS)),)
-include $(S??_DEPS)
endif
ifneq ($(strip $(C64_DEPS)),)
-include $(C64_DEPS)
endif
ifneq ($(strip $(CXX_DEPS)),)
-include $(CXX_DEPS)
endif
ifneq ($(strip $(S64_DEPS)),)
-include $(S64_DEPS)
endif
ifneq ($(strip $(CLA_DEPS)),)
-include $(CLA_DEPS)
endif
ifneq ($(strip $(S55_DEPS)),)
-include $(S55_DEPS)
endif
ifneq ($(strip $(SV7A_DEPS)),)
-include $(SV7A_DEPS)
endif
ifneq ($(strip $(C62_DEPS)),)
-include $(C62_DEPS)
endif
ifneq ($(strip $(C67_DEPS)),)
-include $(C67_DEPS)
endif
ifneq ($(strip $(K_DEPS)),)
-include $(K_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
ifneq ($(strip $(CC_DEPS)),)
-include $(CC_DEPS)
endif
ifneq ($(strip $(C++_DEPS)),)
-include $(C++_DEPS)
endif
ifneq ($(strip $(C43_DEPS)),)
-include $(C43_DEPS)
endif
ifneq ($(strip $(S43_DEPS)),)
-include $(S43_DEPS)
endif
ifneq ($(strip $(ASM_DEPS)),)
-include $(ASM_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(CPP_DEPS)),)
-include $(CPP_DEPS)
endif
ifneq ($(strip $(SA_DEPS)),)
-include $(SA_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
EXE_OUTPUTS += \
single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang.out 

EXE_OUTPUTS__QUOTED += \
"single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang.out" 


# All Target
all: $(OBJS) $(GEN_CMDS)
	@$(MAKE) --no-print-directory -Onone "single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang.out"

# Tool invocations
single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang.out: $(OBJS) $(GEN_CMDS)
	@echo 'Arm Linker - building target: "$@"'
	"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/bin/tiarmclang.exe" -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -Wl,-m"single_chip_servo.Release.map" -Wl,-i"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/lib" -Wl,-i"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/kernel/freertos/lib" -Wl,-i"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/drivers/lib" -Wl,-i"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/board/lib" -Wl,-i"C:/ti/motor_control_sdk_am243x_09_02_00_12/ind_comms_sdk/source/industrial_comms/ethercat_slave/stack/lib" -Wl,--reread_libs -Wl,--diag_suppress=10063 -Wl,--diag_wrap=off -Wl,--display_error_number -Wl,--warn_sections -Wl,--xml_link_info="single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang_linkInfo.xml" -Wl,--ram_model -Wl,--use_memcpy=fast -Wl,--use_memset=fast -o "single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang.out" $(ORDERED_OBJS)
	@echo 'Finished building target: "$@"'
	@echo ' '
	@$(MAKE) --no-print-directory post-build

# Other Targets
clean:
	-$(RM) $(GEN_MISC_FILES__QUOTED)$(GEN_FILES__QUOTED)$(EXE_OUTPUTS__QUOTED)
	-$(RM) "CUST_PHY_base.o" "CUST_PHY_dp83869.o" "ESL_BOARD_OS_config_tidep_01032.o" "ESL_OS_os.o" "ESL_cia402Demo_tidep_01032.o" "ESL_cia402Obd.o" "ESL_eeprom_tidep_01032.o" "ESL_fileHandling.o" "ESL_foeDemo.o" "ESL_gpioHelper.o" "ESL_soeDemo.o" "ESL_version.o" "EtherCAT_Slave_CiA402_tidep_01032.o" "ecSlvCiA402.o" "syscfg\ti_dpl_config.o" "syscfg\ti_drivers_config.o" "syscfg\ti_drivers_open_close.o" "syscfg\ti_pinmux_config.o" "syscfg\ti_power_clock_config.o" "syscfg\ti_board_config.o" "syscfg\ti_board_open_close.o" "syscfg\ti_enet_config.o" "syscfg\ti_enet_open_close.o" "syscfg\ti_enet_soc.o" "syscfg\ti_enet_lwipif.o" "nvm.o" "nvm_drv_eeprom_tidep_01032.o" "nvm_drv_flash.o" 
	-$(RM) "CUST_PHY_base.d" "CUST_PHY_dp83869.d" "ESL_BOARD_OS_config_tidep_01032.d" "ESL_OS_os.d" "ESL_cia402Demo_tidep_01032.d" "ESL_cia402Obd.d" "ESL_eeprom_tidep_01032.d" "ESL_fileHandling.d" "ESL_foeDemo.d" "ESL_gpioHelper.d" "ESL_soeDemo.d" "ESL_version.d" "EtherCAT_Slave_CiA402_tidep_01032.d" "ecSlvCiA402.d" "syscfg\ti_dpl_config.d" "syscfg\ti_drivers_config.d" "syscfg\ti_drivers_open_close.d" "syscfg\ti_pinmux_config.d" "syscfg\ti_power_clock_config.d" "syscfg\ti_board_config.d" "syscfg\ti_board_open_close.d" "syscfg\ti_enet_config.d" "syscfg\ti_enet_open_close.d" "syscfg\ti_enet_soc.d" "syscfg\ti_enet_lwipif.d" "nvm.d" "nvm_drv_eeprom_tidep_01032.d" "nvm_drv_flash.d" 
	-$(RMDIR) $(GEN_MISC_DIRS__QUOTED)
	-@echo ' '

post-build:
	-$(MAKE) -C C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project\single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang -f makefile_ccs_bootimage_gen OUTNAME=single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang PROFILE=Release MOTOR_CONTROL_SDK_PATH=C:/ti/motor_control_sdk_am243x_09_02_00_12 CG_TOOL_ROOT=C:/ti/ti_cgt_arm_llvm_3.2.2.LTS CCS_INSTALL_DIR=C:\ti\ccs2050\ccs\ CCS_IDE_MODE=desktop DEVICE=am243x
	-@echo ' '

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets

