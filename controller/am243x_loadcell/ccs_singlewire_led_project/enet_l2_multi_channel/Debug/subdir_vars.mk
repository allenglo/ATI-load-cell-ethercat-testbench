################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Add inputs and outputs from these tool invocations to the build variables 
SYSCFG_SRCS += \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/am243x-lp/r5fss0-0_freertos/example.syscfg 

C_SRCS += \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/am243x-lp/r5fss0-0_freertos/enet_custom_board_config.c \
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
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/am243x-lp/r5fss0-0_freertos/main.c \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/V0/multi_channel_cfg.c \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/V0/multi_channel_dataflow.c \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/V0/multi_channel_main.c \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_ptp.c \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_ptp_init_priv.c \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_ptp_osal_priv.c \
C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_tools.c 

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
./enet_custom_board_config.d \
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
./main.d \
./multi_channel_cfg.d \
./multi_channel_dataflow.d \
./multi_channel_main.d \
./timeSync_ptp.d \
./timeSync_ptp_init_priv.d \
./timeSync_ptp_osal_priv.d \
./timeSync_tools.d 

OBJS += \
./enet_custom_board_config.o \
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
./main.o \
./multi_channel_cfg.o \
./multi_channel_dataflow.o \
./multi_channel_main.o \
./timeSync_ptp.o \
./timeSync_ptp_init_priv.o \
./timeSync_ptp_osal_priv.o \
./timeSync_tools.o 

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
"enet_custom_board_config.o" \
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
"main.o" \
"multi_channel_cfg.o" \
"multi_channel_dataflow.o" \
"multi_channel_main.o" \
"timeSync_ptp.o" \
"timeSync_ptp_init_priv.o" \
"timeSync_ptp_osal_priv.o" \
"timeSync_tools.o" 

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
"enet_custom_board_config.d" \
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
"main.d" \
"multi_channel_cfg.d" \
"multi_channel_dataflow.d" \
"multi_channel_main.d" \
"timeSync_ptp.d" \
"timeSync_ptp_init_priv.d" \
"timeSync_ptp_osal_priv.d" \
"timeSync_tools.d" 

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
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/am243x-lp/r5fss0-0_freertos/enet_custom_board_config.c" \
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
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/am243x-lp/r5fss0-0_freertos/main.c" \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/V0/multi_channel_cfg.c" \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/V0/multi_channel_dataflow.c" \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/V0/multi_channel_main.c" \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_ptp.c" \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_ptp_init_priv.c" \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_ptp_osal_priv.c" \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/ptp_stack/timeSync_tools.c" 

SYSCFG_SRCS__QUOTED += \
"C:/ti/mcu_plus_sdk_am243x_11_01_00_19/source/networking/enet/core/examples/enet_layer2_multi_channel/am243x-lp/r5fss0-0_freertos/example.syscfg" 


