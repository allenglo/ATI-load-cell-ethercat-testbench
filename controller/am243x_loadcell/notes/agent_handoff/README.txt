Date: 2026-06-10 12:10:28

What was saved:
1) Firmware snapshot under firmware_snapshots/...
2) GUI serial stability improvements in scripts/launchpad_loadcell_live_gui.py

GUI serial anti-freeze changes:
- ScrolledText undo disabled (maxundo=0)
- Queue overflow no longer kills serial reader thread
- Batched UI inserts + capped terminal lines to control RAM

Upload note:
- Firmware project itself is not a git repo; snapshot is stored here for GitHub backup and future agent continuity.
