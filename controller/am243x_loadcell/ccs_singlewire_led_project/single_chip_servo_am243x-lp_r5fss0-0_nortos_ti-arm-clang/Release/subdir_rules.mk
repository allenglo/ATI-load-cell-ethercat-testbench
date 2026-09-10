################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
%.o: ../%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/bin/tiarmclang.exe" -c -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -I"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/include/c" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/drivers" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/board" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/cmsis/DSP/Include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/cmsis/Core/Include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/current_sense/sdfm/firmware" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/current_sense/sdfm/include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/position_sense/endat/firmware" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/position_sense/endat/include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/clarke" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/ipark" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/park" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/svgen" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/dcl" -DSOC_AM243X -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss0-0_nortos_ti-arm-clang/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

build-1785343368: ../example.syscfg
	@echo 'SysConfig - building file: "$<"'
	"C:/ti/sysconfig_1.20.0/sysconfig_cli.bat" -s "C:/ti/motor_control_sdk_am243x_09_02_00_12/.metadata/product.json" -p "ALX" -r "ALX" --script "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss0-1_nortos_ti-arm-clang/example.syscfg" --context "r5fss0-1" --script "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss1-0_freertos_ti-arm-clang/example.syscfg" --context "r5fss1-0" --script "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss0-0_nortos_ti-arm-clang/example.syscfg" --context "r5fss0-0" -o "syscfg" --compiler ticlang
	@echo 'Finished building: "$<"'
	@echo ' '

syscfg/ti_dpl_config.c: build-1785343368 ../example.syscfg
syscfg/ti_dpl_config.h: build-1785343368
syscfg/ti_drivers_config.c: build-1785343368
syscfg/ti_drivers_config.h: build-1785343368
syscfg/ti_drivers_open_close.c: build-1785343368
syscfg/ti_drivers_open_close.h: build-1785343368
syscfg/ti_pinmux_config.c: build-1785343368
syscfg/ti_power_clock_config.c: build-1785343368
syscfg/ti_board_config.c: build-1785343368
syscfg/ti_board_config.h: build-1785343368
syscfg/ti_board_open_close.c: build-1785343368
syscfg/ti_board_open_close.h: build-1785343368
syscfg/ti_enet_config.c: build-1785343368
syscfg/ti_enet_config.h: build-1785343368
syscfg/ti_enet_open_close.c: build-1785343368
syscfg/ti_enet_open_close.h: build-1785343368
syscfg/ti_enet_soc.c: build-1785343368
syscfg/ti_enet_lwipif.c: build-1785343368
syscfg/ti_enet_lwipif.h: build-1785343368
syscfg/ti_pru_io_config.inc: build-1785343368
syscfg/linker.cmd: build-1785343368
syscfg/linker_defines.h: build-1785343368
syscfg: build-1785343368

syscfg/%.o: ./syscfg/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/bin/tiarmclang.exe" -c -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -I"C:/ti/ti_cgt_arm_llvm_3.2.2.LTS/include/c" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/drivers" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/board" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/cmsis/DSP/Include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/mcu_plus_sdk/source/cmsis/Core/Include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/current_sense/sdfm/firmware" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/current_sense/sdfm/include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/position_sense/endat/firmware" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/position_sense/endat/include" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/clarke" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/ipark" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/park" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/transforms/svgen" -I"C:/ti/motor_control_sdk_am243x_09_02_00_12/source/dcl" -DSOC_AM243X -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"syscfg/$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/single_chip_servo_am243x-lp_r5fss0-0_nortos_ti-arm-clang/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


