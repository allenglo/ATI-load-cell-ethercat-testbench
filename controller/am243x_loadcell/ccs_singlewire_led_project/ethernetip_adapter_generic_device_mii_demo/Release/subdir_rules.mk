################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
CUST_PHY_base.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_base.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"CUST_PHY_base.d_raw" -MT"CUST_PHY_base.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

CUST_PHY_dp83869.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_dp83869.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"CUST_PHY_dp83869.d_raw" -MT"CUST_PHY_dp83869.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

app.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/app.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"app.d_raw" -MT"app.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

app_task.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/app_task.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"app_task.d_raw" -MT"app_task.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cmn_app.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_app.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cmn_app.d_raw" -MT"cmn_app.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cmn_board.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_board.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cmn_board.d_raw" -MT"cmn_board.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cmn_cpu_main.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_cpu_main.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cmn_cpu_main.d_raw" -MT"cmn_cpu_main.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cmn_mem.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_mem.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cmn_mem.d_raw" -MT"cmn_mem.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cmn_os.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/os/freertos/cmn_os.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cmn_os.d_raw" -MT"cmn_os.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cust_drivers.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/cust_drivers.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cust_drivers.d_raw" -MT"cust_drivers.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cust_eeprom.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/eeprom/cust_eeprom.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cust_eeprom.d_raw" -MT"cust_eeprom.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cust_ethphy.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/ethphy/cust_ethphy.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cust_ethphy.d_raw" -MT"cust_ethphy.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cust_flash.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/flash/cust_flash.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cust_flash.d_raw" -MT"cust_flash.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

cust_led.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/custom/led/cust_led.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"cust_led.d_raw" -MT"cust_led.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

device_profile_cfg.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_cfg.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"device_profile_cfg.d_raw" -MT"device_profile_cfg.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

device_profile_intf.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/device_profile_intf.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"device_profile_intf.d_raw" -MT"device_profile_intf.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

device_profile_nvm.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_nvm.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"device_profile_nvm.d_raw" -MT"device_profile_nvm.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

device_profile_reset.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/common/device_profile_reset.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"device_profile_reset.d_raw" -MT"device_profile_reset.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drivers.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/drivers.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drivers.d_raw" -MT"drivers.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drv_board.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/board/drv_board.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drv_board.d_raw" -MT"drv_board.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drv_common.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/common/drv_common.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drv_common.d_raw" -MT"drv_common.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drv_eeprom.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/eeprom/drv_eeprom.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drv_eeprom.d_raw" -MT"drv_eeprom.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drv_flash.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/flash/drv_flash.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drv_flash.d_raw" -MT"drv_flash.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drv_led.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/led/drv_led.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drv_led.d_raw" -MT"drv_led.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drv_pruicss.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/pruicss/drv_pruicss.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drv_pruicss.d_raw" -MT"drv_pruicss.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

drv_uart.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/drivers/uart/drv_uart.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"drv_uart.d_raw" -MT"drv_uart.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

build-132792547: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/standard/mii/am243x-lp/r5fss0-0_freertos/example.syscfg
	@echo 'SysConfig - building file: "$<"'
	"C:/ti/sysconfig_1.22.0/sysconfig_cli.bat" -s "C:/ti/ind_comms_sdk_am243x_11_00_00_08/.metadata/product.json" -p "ALX" -r "ALX" --script "C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/standard/mii/am243x-lp/r5fss0-0_freertos/example.syscfg" --context "r5fss0-0" -o "syscfg" --compiler ticlang
	@echo 'Finished building: "$<"'
	@echo ' '

syscfg/ti_dpl_config.c: build-132792547 C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/standard/mii/am243x-lp/r5fss0-0_freertos/example.syscfg
syscfg/ti_dpl_config.h: build-132792547
syscfg/ti_drivers_config.c: build-132792547
syscfg/ti_drivers_config.h: build-132792547
syscfg/ti_drivers_open_close.c: build-132792547
syscfg/ti_drivers_open_close.h: build-132792547
syscfg/ti_pinmux_config.c: build-132792547
syscfg/ti_power_clock_config.c: build-132792547
syscfg/ti_board_config.c: build-132792547
syscfg/ti_board_config.h: build-132792547
syscfg/ti_board_open_close.c: build-132792547
syscfg/ti_board_open_close.h: build-132792547
syscfg/ti_enet_config.c: build-132792547
syscfg/ti_enet_config.h: build-132792547
syscfg/ti_enet_open_close.c: build-132792547
syscfg/ti_enet_open_close.h: build-132792547
syscfg/ti_enet_soc.c: build-132792547
syscfg/ti_enet_lwipif.c: build-132792547
syscfg/ti_enet_lwipif.h: build-132792547
syscfg/linker.cmd: build-132792547
syscfg/linker_defines.h: build-132792547
syscfg: build-132792547

syscfg/%.o: ./syscfg/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"syscfg/$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

generic_device.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/generic_device.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"generic_device.d_raw" -MT"generic_device.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

generic_device_cfg.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/device_profiles/generic_device/generic_device_cfg.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"generic_device_cfg.d_raw" -MT"generic_device_cfg.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

web_server.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethernetip_adapter_demo/services/web_server/web_server.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DCUST_PHY_DP83869=1 -DOSAL_FREERTOS=1 -DEIP_TIME_SYNC=1 -DEIP_QUICK_CONNECT=0 -DCPU_LOAD_MONITOR=0 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -mllvm -align-all-functions=2 -MMD -MP -MF"web_server.d_raw" -MT"web_server.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethernetip_adapter_generic_device_mii_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


