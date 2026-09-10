################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
build-1646919315: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_cpsw/am243x-lp/r5fss0-0_freertos/example.syscfg
	@echo 'SysConfig - building file: "$<"'
	"C:/ti/sysconfig_1.23.0/sysconfig_cli.bat" -s "C:/ti/mcu_plus_sdk_am243x_11_01_00_19/.metadata/product.json" -p "ALX" -r "ALX" --script "C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_cpsw/am243x-lp/r5fss0-0_freertos/example.syscfg" --context "r5fss0-0" -o "syscfg" --compiler ticlang
	@echo 'Finished building: "$<"'
	@echo ' '

syscfg/ti_dpl_config.c: build-1646919315 C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_cpsw/am243x-lp/r5fss0-0_freertos/example.syscfg
syscfg/ti_dpl_config.h: build-1646919315
syscfg/ti_drivers_config.c: build-1646919315
syscfg/ti_drivers_config.h: build-1646919315
syscfg/ti_drivers_open_close.c: build-1646919315
syscfg/ti_drivers_open_close.h: build-1646919315
syscfg/ti_pinmux_config.c: build-1646919315
syscfg/ti_power_clock_config.c: build-1646919315
syscfg/ti_board_config.c: build-1646919315
syscfg/ti_board_config.h: build-1646919315
syscfg/ti_board_open_close.c: build-1646919315
syscfg/ti_board_open_close.h: build-1646919315
syscfg/ti_enet_config.c: build-1646919315
syscfg/ti_enet_config.h: build-1646919315
syscfg/ti_enet_open_close.c: build-1646919315
syscfg/ti_enet_open_close.h: build-1646919315
syscfg/ti_enet_soc.c: build-1646919315
syscfg/ti_enet_lwipif.c: build-1646919315
syscfg/ti_enet_lwipif.h: build-1646919315
syscfg/linker.cmd: build-1646919315
syscfg/linker_defines.h: build-1646919315
syscfg: build-1646919315

syscfg/%.o: ./syscfg/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -I"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/include/c" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/enet/rtos_drivers/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/port" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/FreeRTOS-Kernel/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/portable/TI_ARM_CLANG/ARM_CR5F" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/config/am243x/r5f" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/V3" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/phy" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/soc/k3/am64x_am243x" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include/mdio/V4" -DSOC_AM243X -DENET_ENABLE_PER_CPSW=1 -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"syscfg/$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_l2_cpsw/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

l2_cpsw_cfg.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_cpsw/V0/l2_cpsw_cfg.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -I"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/include/c" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/enet/rtos_drivers/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/port" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/FreeRTOS-Kernel/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/portable/TI_ARM_CLANG/ARM_CR5F" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/config/am243x/r5f" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/V3" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/phy" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/soc/k3/am64x_am243x" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include/mdio/V4" -DSOC_AM243X -DENET_ENABLE_PER_CPSW=1 -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"l2_cpsw_cfg.d_raw" -MT"l2_cpsw_cfg.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_l2_cpsw/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

l2_cpsw_dataflow.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_cpsw/V0/l2_cpsw_dataflow.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -I"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/include/c" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/enet/rtos_drivers/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/port" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/FreeRTOS-Kernel/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/portable/TI_ARM_CLANG/ARM_CR5F" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/config/am243x/r5f" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/V3" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/phy" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/soc/k3/am64x_am243x" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include/mdio/V4" -DSOC_AM243X -DENET_ENABLE_PER_CPSW=1 -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"l2_cpsw_dataflow.d_raw" -MT"l2_cpsw_dataflow.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_l2_cpsw/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

l2_cpsw_main.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_cpsw/V0/l2_cpsw_main.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -I"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/include/c" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/enet/rtos_drivers/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/port" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/FreeRTOS-Kernel/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/portable/TI_ARM_CLANG/ARM_CR5F" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/config/am243x/r5f" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/V3" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/phy" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/soc/k3/am64x_am243x" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include/mdio/V4" -DSOC_AM243X -DENET_ENABLE_PER_CPSW=1 -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"l2_cpsw_main.d_raw" -MT"l2_cpsw_main.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_l2_cpsw/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

main.o: C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_cpsw/am243x-lp/r5fss0-0_freertos/main.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -I"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/include/c" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/enet/rtos_drivers/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/board/ethphy/port" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/FreeRTOS-Kernel/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/portable/TI_ARM_CLANG/ARM_CR5F" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/kernel/freertos/config/am243x/r5f" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/utils/V3" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/phy" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/include/core" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/soc/k3/am64x_am243x" -I"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/hw_include/mdio/V4" -DSOC_AM243X -DENET_ENABLE_PER_CPSW=1 -DOS_FREERTOS -D_DEBUG_=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -MMD -MP -MF"main.d_raw" -MT"main.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/enet_l2_cpsw/Debug/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


