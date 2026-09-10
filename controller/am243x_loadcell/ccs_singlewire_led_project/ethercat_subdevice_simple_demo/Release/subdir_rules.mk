################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
CUST_PHY_base.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_base.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"CUST_PHY_base.d_raw" -MT"CUST_PHY_base.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

CUST_PHY_dp83869.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/custom_phy/src/CUST_PHY_dp83869.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"CUST_PHY_dp83869.d_raw" -MT"CUST_PHY_dp83869.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_BOARD_OS_config.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/board/am243x-lp/freertos/ESL_BOARD_OS_config.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_BOARD_OS_config.d_raw" -MT"ESL_BOARD_OS_config.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_OS_os.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_OS_os.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_OS_os.d_raw" -MT"ESL_OS_os.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_eeprom.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_eeprom.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_eeprom.d_raw" -MT"ESL_eeprom.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_eoeDemo.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_eoeDemo.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_eoeDemo.d_raw" -MT"ESL_eoeDemo.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_fileHandling.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_fileHandling.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_fileHandling.d_raw" -MT"ESL_fileHandling.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_foeDemo.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_foeDemo.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_foeDemo.d_raw" -MT"ESL_foeDemo.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_gpioHelper.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_gpioHelper.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_gpioHelper.d_raw" -MT"ESL_gpioHelper.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_soeDemo.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/os/freertos/ESL_soeDemo.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_soeDemo.d_raw" -MT"ESL_soeDemo.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ESL_version.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/common/ESL_version.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ESL_version.d_raw" -MT"ESL_version.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

EtherCAT_SubDevice_Simple.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/EtherCAT_SubDevice_Simple.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"EtherCAT_SubDevice_Simple.d_raw" -MT"EtherCAT_SubDevice_Simple.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

ecSubDeviceSimple.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/ecSubDeviceSimple.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"ecSubDeviceSimple.d_raw" -MT"ecSubDeviceSimple.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

build-1239071612: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/am243x-lp/r5fss0-0_freertos/example.syscfg
	@echo 'SysConfig - building file: "$<"'
	"C:/ti/sysconfig_1.22.0/sysconfig_cli.bat" -s "C:/ti/ind_comms_sdk_am243x_11_00_00_08/.metadata/product.json" -p "ALX" -r "ALX" --script "C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/am243x-lp/r5fss0-0_freertos/example.syscfg" --context "r5fss0-0" -o "syscfg" --compiler ticlang
	@echo 'Finished building: "$<"'
	@echo ' '

syscfg/ti_dpl_config.c: build-1239071612 C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/ethercat_subdevice_demo/device_profiles/401_simple/am243x-lp/r5fss0-0_freertos/example.syscfg
syscfg/ti_dpl_config.h: build-1239071612
syscfg/ti_drivers_config.c: build-1239071612
syscfg/ti_drivers_config.h: build-1239071612
syscfg/ti_drivers_open_close.c: build-1239071612
syscfg/ti_drivers_open_close.h: build-1239071612
syscfg/ti_pinmux_config.c: build-1239071612
syscfg/ti_power_clock_config.c: build-1239071612
syscfg/ti_board_config.c: build-1239071612
syscfg/ti_board_config.h: build-1239071612
syscfg/ti_board_open_close.c: build-1239071612
syscfg/ti_board_open_close.h: build-1239071612
syscfg/ti_enet_config.c: build-1239071612
syscfg/ti_enet_config.h: build-1239071612
syscfg/ti_enet_open_close.c: build-1239071612
syscfg/ti_enet_open_close.h: build-1239071612
syscfg/ti_enet_soc.c: build-1239071612
syscfg/ti_enet_lwipif.c: build-1239071612
syscfg/ti_enet_lwipif.h: build-1239071612
syscfg/linker.cmd: build-1239071612
syscfg/linker_defines.h: build-1239071612
syscfg: build-1239071612

syscfg/%.o: ./syscfg/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"syscfg/$(basename $(<F)).d_raw" -MT"$(@)" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

nvm.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/app/src/nvm.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"nvm.d_raw" -MT"nvm.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

nvm_drv_eeprom.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/drv/src/nvm_drv_eeprom.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"nvm_drv_eeprom.d_raw" -MT"nvm_drv_eeprom.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '

nvm_drv_flash.o: C:/ti/ind_comms_sdk_am243x_11_00_00_08/examples/industrial_comms/nvm/drv/src/nvm_drv_flash.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Arm Compiler - building file: "$<"'
	"C:/ti/ti_cgt_arm_llvm_4.0.1.LTS/bin/tiarmclang.exe" -c @"ccsIncludes.opt"  -mcpu=cortex-r5 -mfloat-abi=hard -mfpu=vfpv3-d16 -mlittle-endian -mthumb -Os -DSOC_AM243X -DSOC_AM243X=1 -DOSAL_FREERTOS=1 -Dcore0 -Dam243x -Dam243x_lp -DSSC_CHECKTIMER=1 -DUSE_ECAT_TIMER=1 -DCUST_PHY_DP83869=1 -g -Wall -Wno-gnu-variable-sized-type-not-at-end -Wno-unused-function -Wno-unused-but-set-variable -MMD -MP -MF"nvm_drv_flash.d_raw" -MT"nvm_drv_flash.o" -I"C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/ccs_singlewire_led_project/ethercat_subdevice_simple_demo/Release/syscfg"  $(GEN_OPTS__FLAG) -o"$@" "$<"
	@echo 'Finished building: "$<"'
	@echo ' '


