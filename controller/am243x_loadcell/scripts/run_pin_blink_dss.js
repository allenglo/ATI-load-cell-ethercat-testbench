importPackage(Packages.com.ti.debug.engine.scripting);
importPackage(Packages.com.ti.ccstudio.scripting.environment);
importPackage(Packages.java.lang);

var ccxmlPath = "C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/am2434_xds110_generated.ccxml";
var cpuName = "MAIN_Cortex_R5_0_0";
var outFile = "C:/ti/mcu_plus_sdk_am243x_12_00_00_26/examples/drivers/gpio/gpio_led_blink/am243x-lp/r5fss0-0_nortos/ti-arm-clang/gpio_led_blink.release.out";

var script = ScriptingEnvironment.instance();
script.traceSetConsoleLevel(TraceLevel.ALL);

script.traceWrite("[DSS] Starting run_pin_blink_dss.js");

var debugServer = script.getServer("DebugServer.1");
debugServer.setConfig(ccxmlPath);

var debugSession = debugServer.openSession("*", cpuName);

script.traceWrite("[DSS] Connecting target");
debugSession.target.connect();

script.traceWrite("[DSS] Reset target");
debugSession.target.reset();

script.traceWrite("[DSS] Loading program: " + outFile);
debugSession.memory.loadProgram(outFile);

script.traceWrite("[DSS] Run async");
debugSession.target.runAsynch();

/* Give firmware time to print before debugger disconnect */
Thread.sleep(5000);

script.traceWrite("[DSS] Disconnect target (leave running)");
debugSession.target.disconnect();

script.traceWrite("[DSS] Terminate debug session");
debugSession.terminate();

script.traceWrite("[DSS] Stop debug server");
debugServer.stop();

script.traceWrite("[DSS] Done");
