################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
%.o: ../%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

build-1961074218: ../example.syscfg
	@echo 'SysConfig - building file: "$<"'
	"C:/ti/sysconfig_1.20.0/sysconfig_cli.bat" -s "C:/ti/motor_control_sdk_am243x_09_02_00_12/.metadata/product.json" -p "ALX" -r "ALX" --script "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss0-0_nortos_ti-arm-clang/example.syscfg" --context "r5fss0-0" --script "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss0-1_nortos_ti-arm-clang/example.syscfg" --context "r5fss0-1" --script "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang/example.syscfg" --context "r5fss1-0" -o "syscfg" --compiler ticlang
	@echo 'Finished building: "$<"'
	@echo ' '

syscfg/ti_dpl_config.c: build-1961074218 ../example.syscfg
syscfg/ti_dpl_config.h: build-1961074218
syscfg/ti_drivers_config.c: build-1961074218
syscfg/ti_drivers_config.h: build-1961074218
syscfg/ti_drivers_open_close.c: build-1961074218
syscfg/ti_drivers_open_close.h: build-1961074218
syscfg/ti_pinmux_config.c: build-1961074218
syscfg/ti_power_clock_config.c: build-1961074218
syscfg/ti_board_config.c: build-1961074218
syscfg/ti_board_config.h: build-1961074218
syscfg/ti_board_open_close.c: build-1961074218
syscfg/ti_board_open_close.h: build-1961074218
syscfg/ti_enet_config.c: build-1961074218
syscfg/ti_enet_config.h: build-1961074218
syscfg/ti_enet_open_close.c: build-1961074218
syscfg/ti_enet_open_close.h: build-1961074218
syscfg/ti_enet_soc.c: build-1961074218
syscfg/ti_enet_lwipif.c: build-1961074218
syscfg/ti_enet_lwipif.h: build-1961074218
syscfg/ti_pru_io_config.inc: build-1961074218
syscfg/linker.cmd: build-1961074218
syscfg/linker_defines.h: build-1961074218
syscfg: build-1961074218

syscfg/%.o: ./syscfg/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"syscfg/$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


