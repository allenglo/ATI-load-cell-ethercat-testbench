/*
 * dss_load_run_noreset.js
 *
 * Like dss_load_run_generic.js but does NOT reset the CPU before loading.
 * Use for step 2 of the DEV-boot sequence (app load) so the SYSFW board
 * config installed by sciclient_ccs_init (step 1) is preserved.
 *
 * Usage:
 *   dss.bat dss_load_run_noreset.js <ccxml> <cpu> <out_file> [run_delay_ms]
 */
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

var ccxmlPath  = argOrDefault(0, '');
var cpuName    = argOrDefault(1, 'MAIN_Cortex_R5_0_0');
var outFile    = argOrDefault(2, '');
var runDelayMs = parseInt(argOrDefault(3, '3000'), 10);

var script = ScriptingEnvironment.instance();
script.traceSetConsoleLevel(TraceLevel.ALL);

var debugServer  = null;
var debugSession = null;

try {
    script.traceWrite('[DSS-NORESET] START');
    script.traceWrite('[DSS-NORESET] ccxml='  + ccxmlPath);
    script.traceWrite('[DSS-NORESET] cpu='    + cpuName);
    script.traceWrite('[DSS-NORESET] out='    + outFile);

    debugServer = script.getServer('DebugServer.1');
    debugServer.setConfig(ccxmlPath);

    debugSession = debugServer.openSession('*', cpuName);
    debugSession.target.connect();
    /* NO reset here – preserve SYSFW/board-config state from step 1 */
    debugSession.memory.loadProgram(outFile);
    debugSession.target.runAsynch();

    if (runDelayMs > 0) {
        Thread.sleep(runDelayMs);
    }

    script.traceWrite('[DSS-NORESET] RUNNING');

    if (debugSession !== null) {
        debugSession.target.disconnect();
    }

    script.traceWrite('[DSS-NORESET] SUCCESS');
} catch (e) {
    script.traceWrite('[DSS-NORESET] FAILURE: ' + e);
    throw e;
} finally {
    if (debugSession !== null) {
        try { debugSession.terminate(); } catch (ignore1) {}
    }
    if (debugServer !== null) {
        try { debugServer.stop(); } catch (ignore2) {}
    }
}
