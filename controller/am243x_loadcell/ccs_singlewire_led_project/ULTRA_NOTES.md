# Ultra Notes (Keep Short)

- Work here now: ccs_singlewire_led_project (not SDK in-place edits).
- Data pin for addressable chain: board pin 55 = SPI0_D0.
- Current app file: mcspi_loopback.c (dual mode: WS2812 + Dialight 587 timing).
- Build command must set CCS_PATH and SYSCFG_PATH to ccs2050.
- If gmake fails generating .mcelf with missing construct, .out is still valid for JTAG load.
- Use loadti with -r to run after load. -l is load-only.
- CCS Copilot plugins should be official only: GitHub.copilot and GitHub.copilot-chat.
- CCS plugin path: C:\Users\zwu\AppData\Local\Texas Instruments\CCS\ccs2050\0\theia\deployedPlugins.
