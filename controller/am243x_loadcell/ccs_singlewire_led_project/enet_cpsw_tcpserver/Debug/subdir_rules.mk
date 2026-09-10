################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
app_cpswconfighandler.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/lwip/enet_cpsw_tcpserver/app_cpswconfighandler.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -DSOC_AM243X -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"app_cpswconfighandler.d_raw" -MT"app_cpswconfighandler.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_cpsw_tcpserver/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

app_main.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/lwip/enet_cpsw_tcpserver/app_main.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -DSOC_AM243X -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"app_main.d_raw" -MT"app_main.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_cpsw_tcpserver/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

app_tcpserver.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/lwip/enet_cpsw_tcpserver/app_tcpserver.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -DSOC_AM243X -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"app_tcpserver.d_raw" -MT"app_tcpserver.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_cpsw_tcpserver/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

build-1145925067: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/lwip/enet_cpsw_tcpserver/am243x-lp/r5fss0-0_freertos/example.syscfg
	@echo 'SysConfig - building file: "$<"'
	"C:/ti/sysconfig_1.23.0/sysconfig_cli.bat" -s "C:/ti/mcu_plus_sdk_am243x_11_01_00_19/.metadata/product.json" -p "ALX" -r "ALX" --script "C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/lwip/enet_cpsw_tcpserver/am243x-lp/r5fss0-0_freertos/example.syscfg" --context "r5fss0-0" -o "syscfg" --compiler ticlang
	@echo 'Finished building: "$<"'
	@echo ' '

syscfg/ti_dpl_config.c: build-1145925067 C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/lwip/enet_cpsw_tcpserver/am243x-lp/r5fss0-0_freertos/example.syscfg
syscfg/ti_dpl_config.h: build-1145925067
syscfg/ti_drivers_config.c: build-1145925067
syscfg/ti_drivers_config.h: build-1145925067
syscfg/ti_drivers_open_close.c: build-1145925067
syscfg/ti_drivers_open_close.h: build-1145925067
syscfg/ti_pinmux_config.c: build-1145925067
syscfg/ti_power_clock_config.c: build-1145925067
syscfg/ti_board_config.c: build-1145925067
syscfg/ti_board_config.h: build-1145925067
syscfg/ti_board_open_close.c: build-1145925067
syscfg/ti_board_open_close.h: build-1145925067
syscfg/ti_enet_config.c: build-1145925067
syscfg/ti_enet_config.h: build-1145925067
syscfg/ti_enet_open_close.c: build-1145925067
syscfg/ti_enet_open_close.h: build-1145925067
syscfg/ti_enet_soc.c: build-1145925067
syscfg/ti_enet_lwipif.c: build-1145925067
syscfg/ti_enet_lwipif.h: build-1145925067
syscfg/linker.cmd: build-1145925067
syscfg/linker_defines.h: build-1145925067
syscfg: build-1145925067

syscfg/%.o: ./syscfg/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -DSOC_AM243X -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"syscfg/$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_cpsw_tcpserver/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

main.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/lwip/enet_cpsw_tcpserver/am243x-lp/r5fss0-0_freertos/main.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -DSOC_AM243X -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"main.d_raw" -MT"main.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_cpsw_tcpserver/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


