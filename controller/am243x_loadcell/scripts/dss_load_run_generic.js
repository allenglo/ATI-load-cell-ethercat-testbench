importPackage(Packages.com.ti.debug.engine.scripting);
importPackage(Packages.com.ti.ccstudio.scripting.environment);
importPackage(Packages.java.lang);

function argOrDefault(index, fallback) {
    if (typeof scriptArgs === 'undefined' || scriptArgs.length <= index || scriptArgs[index] === null || scriptArgs[index] === '') {
        return fallback;
    }
    return String(scriptArgs[index]);
}

var scriptArgs = (typeof arguments !== 'undefined') ? arguments : [];

var ccxmlPath = argOrDefault(0, 'C:/CoRoot/##TASKS##/#TASK# TI_AM243x_LaunchPad_eFlex/am2434_xds110_generated.ccxml');
var cpuName = argOrDefault(1, 'MAIN_Cortex_R5_0_0');
var outFile = argOrDefault(2, 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26/examples/drivers/gpio/gpio_led_blink/am243x-lp/r5fss0-0_nortos/ti-arm-clang/gpio_led_blink.release.out');
var runDelayMs = parseInt(argOrDefault(3, '2000'), 10);

var script = ScriptingEnvironment.instance();
script.traceSetConsoleLevel(TraceLevel.ALL);

var debugServer = null;
var debugSession = null;

try {
    script.traceWrite('[DSS] START');
    script.traceWrite('[DSS] ccxml=' + ccxmlPath);
    script.traceWrite('[DSS] cpu=' + cpuName);
    script.traceWrite('[DSS] out=' + outFile);

    debugServer = script.getServer('DebugServer.1');
    debugServer.setConfig(ccxmlPath);

    debugSession = debugServer.openSession('*', cpuName);
    debugSession.target.connect();
    debugSession.target.reset();
    debugSession.memory.loadProgram(outFile);
    debugSession.target.runAsynch();

    if (runDelayMs > 0) {
        Thread.sleep(runDelayMs);
    }

    script.traceWrite('[DSS] RUNNING');

    if (debugSession !== null) {
        debugSession.target.disconnect();
    }

    script.traceWrite('[DSS] SUCCESS');
} catch (e) {
    script.traceWrite('[DSS] FAILURE: ' + e);
    throw e;
} finally {
    if (debugSession !== null) {
        try { debugSession.terminate(); } catch (ignore1) {}
    }
    if (debugServer !== null) {
        try { debugServer.stop(); } catch (ignore2) {}
    }
}
