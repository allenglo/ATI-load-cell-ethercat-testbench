# LoadCell GUI High-Flow Notes (2026-05-29)

## Completed Today

### Phase 1 — Packaging + stability (session start)
- Backed up source before packaging:
  - scripts/backups/launchpad_loadcell_live_gui_20260529_180618.py
- Built and published exe:
  - `#RELEASE#/TI_AM243x_LaunchPad_eFlex/LaunchPad_LoadCell_Live_GUI_win64_20260529_1807/`
- Added long-run stability guard: Tk log trimmed to 6 000 lines (trims to 4 000).
- Added two-ATI-slave selection via numeric hint in `Slave name contains`.

### Phase 2 — High-flow library integration (2026-05-29 ~18:12)
- **orjson**: CSV capture path now uses orjson for serialization (faster, graceful fallback to stdlib json).
- **tsdownsample** (`MinMaxLTTBDownsampler`): Live plot path now downsamples to 2 000 points when history exceeds that threshold. Reduces matplotlib draw time at high sample counts. Analysis panel uses full-resolution data (no downsampling there).
- **psutil**: `ui_tick` samples process RSS every 5 s. Adaptive intervals applied:
  - RSS ≥ 800 MB → analysis refresh × 3 (from 2 s to 6 s).
  - RSS ≥ 1 400 MB → log trim forced + analysis refresh × 8 (16 s).
- Backup of integrated source: scripts/backups/launchpad_loadcell_live_gui_20260529_181157.py
- New exe published:
  - `#RELEASE#/TI_AM243x_LaunchPad_eFlex/LaunchPad_LoadCell_Live_GUI_win64_20260529_1812/`
  - Size: ~104.8 MB (includes PySide6 + Qt runtimes from prior venv install)

## Installed High-Flow Libraries (venv)
- pyqtgraph
- PySide6
- numpy-ringbuffer (available, not integrated — deques still used; integrate if allocator pressure noticed)
- orjson  ✅ integrated
- psutil  ✅ integrated
- tsdownsample  ✅ integrated

## Install Attempt Notes
- `lttbc` failed on this machine due to missing Visual C++ build tools.
- Replacement selected: `tsdownsample` (wheel-friendly).

## Why These Libraries
- pyqtgraph + PySide6:
  - Best practical route for very high-refresh live plotting if migrating from Tk to Qt.
- numpy-ringbuffer:
  - Efficient fixed-size ring buffers; lower allocator churn than Python deques.
- tsdownsample:
  - Fast downsampling for large windows without UI stutter.
- orjson:
  - Faster JSON serialization for CSV capture.
- psutil:
  - Runtime memory monitoring and adaptive throttling.

## Remaining Integration Path
1. numpy-ringbuffer swap for deques (low priority — deques are adequate at current sample rates).
2. If live plotting still stutters at very high rates, migrate live tab to pyqtgraph/PySide6 while keeping analysis tab logic in matplotlib.

## Two Load Cells Topology Notes
- Current network now has two ATI load-cell slaves on one switch.
- Selection behavior in code now supports explicit target choice using existing hint field.
- Recommendation for operation:
  - Set `Slave name contains` to `1` or `2` to lock the chosen ATI slave.

## Operational Recommendation
- Live tab is for smooth real-time scrolling view.
- Analysis tab remains window-driven verification.
- For multi-day run, keep log volume moderate and CSV capture path on fast local SSD.
