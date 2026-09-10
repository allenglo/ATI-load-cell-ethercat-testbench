################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

CG_TOOL_ROOT := C:/ti/ti_cgt_arm_llvm_4.0.1.LTS

GEN_OPTS__FLAG := 
GEN_CMDS__FLAG := -Wl,-l"syscfg/linker.cmd" 

ORDERED_OBJS += \
"./CUST_PHY_base.o" \
"./CUST_PHY_dp83869.o" \
"./app.o" \
"./app_task.o" \
"./cmn_app.o" \
"./cmn_board.o" \
"./cmn_cpu_main.o" \
"./cmn_mem.o" \
"./cmn_os.o" \
"./cust_drivers.o" \
"./cust_eeprom.o" \
"./cust_ethphy.o" \
"./cust_flash.o" \
"./cust_led.o" \
"./device_profile_cfg.o" \
"./device_profile_intf.o" \
"./device_profile_nvm.o" \
"./device_profile_reset.o" \
"./drivers.o" \
"./drv_board.o" \
"./drv_common.o" \
"./drv_eeprom.o" \
"./drv_flash.o" \
"./drv_led.o" \
"./drv_pruicss.o" \
"./drv_uart.o" \
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
"./generic_device.o" \
"./generic_device_cfg.o" \
"./web_server.o" \
$(GEN_CMDS__FLAG) \
-Wl,-lfreertos.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-ldrivers.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-lboard.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-licss_emac.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-licss_timesync.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-lethernetip_adapter_mii_icss_fwhal.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-lethernetip_adapter_lwip_contrib.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-lethernetip_adapter_lwip_freertos.am243x.r5f.ti-arm-clang.release.lib \
-Wl,-lethernetipadapter_mii.am243x-lp.r5f.ti-arm-clang.release.lib \
-Wl,-llibc.a \
-Wl,-llibsysbm.a \

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
ethernetip_adapter_generic_device_mii_demo.out 

EXE_OUTPUTS__QUOTED += \
"ethernetip_adapter_generic_device_mii_demo.out" 


# All Target
all: $(OBJS) $(GEN_CMDS)
	@$(MAKE) --no-print-directory -Onone "ethernetip_adapter_generic_device_mii_demo.out"

# Tool invocations
ethernetip_adapter_generic_device_mii_demo.out: $(OBJS) $(GEN_CMDS)
	@echo 'Arm Linker - building target: "$@"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -Wl,-m"ethernetip_adapter_generic_device_mii_demo.Release.map" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/mcu_plus_sdk/source/kernel/freertos/lib" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/mcu_plus_sdk/source/drivers/lib" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/mcu_plus_sdk/source/board/lib" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/source/networking/icss_emac/lib" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/source/networking/icss_timesync/lib" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/source/industrial_comms/ethernetip_adapter/icss_fwhal/lib" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/source/industrial_comms/ethernetip_adapter/stack/lib" -Wl,-i"C:/ti/ind_comms_sdk_am243x_11_00_00_08/source/industrial_comms/ethernetip_adapter/stack/lwip/lib" -Wl,-i"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/lib" -Wl,--reread_libs -Wl,--diag_suppress=10063 -Wl,--diag_wrap=off -Wl,--display_error_number -Wl,--warn_sections -Wl,--gen_xml_func_hash -Wl,--xml_link_info="ethernetip_adapter_generic_device_mii_demo_linkInfo.xml" -Wl,--ram_model -Wl,--use_memcpy=fast -Wl,--use_memset=fast -o "ethernetip_adapter_generic_device_mii_demo.out" $(ORDERED_OBJS)
	@echo 'Finished building target: "$@"'
	@echo ' '
	@$(MAKE) --no-print-directory post-build

# Other Targets
clean:
	-$(RM) $(GEN_MISC_FILES__QUOTED)$(GEN_FILES__QUOTED)$(EXE_OUTPUTS__QUOTED)
	-$(RM) "CUST_PHY_base.o" "CUST_PHY_dp83869.o" "app.o" "app_task.o" "cmn_app.o" "cmn_board.o" "cmn_cpu_main.o" "cmn_mem.o" "cmn_os.o" "cust_drivers.o" "cust_eeprom.o" "cust_ethphy.o" "cust_flash.o" "cust_led.o" "device_profile_cfg.o" "device_profile_intf.o" "device_profile_nvm.o" "device_profile_reset.o" "drivers.o" "drv_board.o" "drv_common.o" "drv_eeprom.o" "drv_flash.o" "drv_led.o" "drv_pruicss.o" "drv_uart.o" "syscfg\ti_dpl_config.o" "syscfg\ti_drivers_config.o" "syscfg\ti_drivers_open_close.o" "syscfg\ti_pinmux_config.o" "syscfg\ti_power_clock_config.o" "syscfg\ti_board_config.o" "syscfg\ti_board_open_close.o" "syscfg\ti_enet_config.o" "syscfg\ti_enet_open_close.o" "syscfg\ti_enet_soc.o" "syscfg\ti_enet_lwipif.o" "generic_device.o" "generic_device_cfg.o" "web_server.o" 
	-$(RM) "CUST_PHY_base.d" "CUST_PHY_dp83869.d" "app.d" "app_task.d" "cmn_app.d" "cmn_board.d" "cmn_cpu_main.d" "cmn_mem.d" "cmn_os.d" "cust_drivers.d" "cust_eeprom.d" "cust_ethphy.d" "cust_flash.d" "cust_led.d" "device_profile_cfg.d" "device_profile_intf.d" "device_profile_nvm.d" "device_profile_reset.d" "drivers.d" "drv_board.d" "drv_common.d" "drv_eeprom.d" "drv_flash.d" "drv_led.d" "drv_pruicss.d" "drv_uart.d" "syscfg\ti_dpl_config.d" "syscfg\ti_drivers_config.d" "syscfg\ti_drivers_open_close.d" "syscfg\ti_pinmux_config.d" "syscfg\ti_power_clock_config.d" "syscfg\ti_board_config.d" "syscfg\ti_board_open_close.d" "syscfg\ti_enet_config.d" "syscfg\ti_enet_open_close.d" "syscfg\ti_enet_soc.d" "syscfg\ti_enet_lwipif.d" "generic_device.d" "generic_device_cfg.d" "web_server.d" 
	-$(RMDIR) $(GEN_MISC_DIRS__QUOTED)
	-@echo ' '

post-build:
	-$(MAKE) -C C:\CoRoot\##TASKS##\#TASK# TI_AM243x_LaunchPad_eFlex\ccs_singlewire_led_project\ethernetip_adapter_generic_device_mii_demo -f makefile_ccs_bootimage_gen OUTNAME=ethernetip_adapter_generic_device_mii_demo PROFILE=Release INDUSTRIAL_COMMUNICATIONS_SDK_PATH=C:/ti/ind_comms_sdk_am243x_11_00_00_08 CG_TOOL_ROOT=C:/ti/ti_cgt_arm_llvm_4.0.1.LTS CCS_INSTALL_DIR=C:\ti\ccs2050\ccs\ CCS_IDE_MODE=desktop DEVICE=am243x
	-@echo ' '

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets

