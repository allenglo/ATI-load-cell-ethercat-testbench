# Demo Plan

The first demo should stay boring and deterministic: use TI's `hello_world` on `am243x-lp` and prove that command-line build plus CCS load works before touching networking or EtherCAT examples.

## Demo 1

- Example: `examples/hello_world/am243x-lp/r5fss0-0_freertos/ti-arm-clang`
- Build method: `gmake`
- Run method: CCS load and run
- Expected output: `Hello World!` on the LaunchPad UART console

## Demo 2

After Demo 1 is clean, move to one of these based on actual eFlex interest:

- industrial Ethernet or networking example
- USB example
- multicore IPC example

## Reason for this order

If hello world fails, the problem is almost always environment, drivers, target config, or board mode. It is better to isolate that first than to debug a more complex example.