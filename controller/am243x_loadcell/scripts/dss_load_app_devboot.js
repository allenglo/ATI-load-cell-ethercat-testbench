/*
 * dss_load_app_devboot.js
 *
 * Proper two-step DEV boot sequence for AM243x, following TI's load_dmsc_hsfs.js pattern.
 *
 * STEP 1: Load + run sciclient_ccs_init SYNCHRONOUSLY.
 *   - Uses the PRE-BUILT binary from tools/ccs_load/am243x/ (NOT the examples/ build).
 *   - target.run() blocks until the binary completes/halts (it ends by running off main
 *     or hitting a WFI after SYSFW self-reset).
 *   - SYSFW is loaded and ALL board configs (incl. RM board config for CPSW) are sent.
 *
 * STEP 2: Reset CPU (SYSFW stays alive), load app, run asynchronously.
 *   - target.reset() only resets the R5F core; SYSFW continues running on DMSC.
 *   - App calls Sciclient_init() which reconnects to the running SYSFW.
 *   - Udma_init() gets CPSW mapped RX channel from SYSFW RM.
 *
 * Usage (from dss.bat):
 *   dss.bat dss_load_app_devboot.js <ccxml> <cpu> <soc_init_out> <app_out> [run_delay_ms]
 *
 * soc_init_out should point to:
 *   C:/ti/mcu_plus_sdk_am243x_12_00_00_26/tools/ccs_load/am243x/sciclient_ccs_init.release.out
 */
importPackage(Packages.com.ti.debug.engine.scripting);
importPackage(Packages.com.ti.ccstudio.scripting.environment);
importPackage(Packages.java.lang);

function argOrDefault(index, fallback) {
    if (typeof scriptArgs === 'undefined' || scriptArgs.length <= index ||
        scriptArgs[index] === null || scriptArgs[index] === '') {
        return fallback;
    }
    return String(scriptArgs[index]);
}

var scriptArgs  = (typeof arguments !== 'undefined') ? arguments : [];
var ccxmlPath   = argOrDefault(0, '');
var cpuName     = argOrDefault(1, 'MAIN_Cortex_R5_0_0');
var socInitOut  = argOrDefault(2, 'C:/ti/mcu_plus_sdk_am243x_12_00_00_26/tools/ccs_load/am243x/sciclient_ccs_init.release.out');
var appOut      = argOrDefault(3, '');
var runDelayMs  = parseInt(argOrDefault(4, '30000'), 10);

var script      = ScriptingEnvironment.instance();
script.traceSetConsoleLevel(TraceLevel.ALL);

var debugServer = null;
var ds          = null;

try {
    script.traceWrite('[DEVBOOT] START');
    script.traceWrite('[DEVBOOT] ccxml   = ' + ccxmlPath);
    script.traceWrite('[DEVBOOT] cpu     = ' + cpuName);
    script.traceWrite('[DEVBOOT] soc_init= ' + socInitOut);
    script.traceWrite('[DEVBOOT] app     = ' + appOut);

    /* Total timeout: soc_init_wait_ms + runDelayMs + 10s buffer */
    var socInitWaitMs = 90000;  /* 90s: cold SYSFW load on GP device takes up to 60s */
    script.setScriptTimeout(socInitWaitMs + runDelayMs + 10000);

    debugServer = script.getServer('DebugServer.1');
    debugServer.setConfig(ccxmlPath);

    ds = debugServer.openSession('*', cpuName);

    /* ----------------------------------------------------------------
     * STEP 1: Load SYSFW + board config
     *
     * WHY ASYNC: sciclient_ccs_init outputs CIO (debug) data through JTAG.
     * In scripting mode, CIO data is not consumed, so blocking run() will
     * hang indefinitely. Use runAsynch() instead and wait for completion.
     *
     * WAIT TIME: on a fresh (cold) GP device, SYSFW takes 30-60s to:
     *   load firmware → boot SYSFW → ABI check → board configs (RM included)
     * After that, the binary calls Bootloader_bootSelfCpu() → WFI →
     * SYSFW module-resets R5F → R5F re-runs from ATCM (sciclient_ccs_init
     * code again) → second attempt fails → hangs in assert loop
     * 90s guarantees first run fully completed before step2.
     * ---------------------------------------------------------------- */
    script.traceWrite('[DEVBOOT] STEP1: connect + halt + reset');
    ds.target.connect();
    ds.target.halt();
    ds.target.reset();

    script.traceWrite('[DEVBOOT] STEP1: loading soc_init ELF');
    ds.memory.loadProgram(socInitOut);

    script.traceWrite('[DEVBOOT] STEP1: running soc_init asynchronously ...');
    ds.target.runAsynch();

    script.traceWrite('[DEVBOOT] STEP1: waiting ' + socInitWaitMs + 'ms for SYSFW cold boot + board configs');
    Thread.sleep(socInitWaitMs);
    script.traceWrite('[DEVBOOT] STEP1: wait complete, SYSFW + RM board config should be active');

    /* ----------------------------------------------------------------
     * STEP 2: Load + run the application
     *  - Halt CPU wherever it is (sciclient_ccs_init loop or assert)
     *  - loadProgram overwrites ATCM with app code
     *  - runAsynch starts fresh app; Sciclient_init reconnects to live SYSFW
     *  - Udma_init gets CPSW mapped RX channel from RM board config
     *  - NO reset: that would kill SYSFW state
     * ---------------------------------------------------------------- */
    script.traceWrite('[DEVBOOT] STEP2: halting CPU before app load');
    ds.target.halt();

    script.traceWrite('[DEVBOOT] STEP2: loading app ELF');
    ds.memory.loadProgram(appOut);

    script.traceWrite('[DEVBOOT] STEP2: starting app');
    ds.target.runAsynch();

    if (runDelayMs > 0) {
        Thread.sleep(runDelayMs);
    }

    script.traceWrite('[DEVBOOT] SUCCESS');

} catch (e) {
    script.traceWrite('[DEVBOOT] FAILURE: ' + e);
    throw e;
} finally {
    if (ds !== null) {
        try { ds.target.disconnect(); } catch (ignore1) {}
        try { ds.terminate();         } catch (ignore2) {}
    }
    if (debugServer !== null) {
        try { debugServer.stop(); } catch (ignore3) {}
    }
}
