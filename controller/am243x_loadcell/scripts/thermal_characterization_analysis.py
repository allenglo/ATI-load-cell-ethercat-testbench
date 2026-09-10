#!/usr/bin/env python3
"""
thermal_characterization_analysis.py
-------------------------------------
ATI F/T Sensor Thermal Drift Characterization

Parses a loadcell CSV + matching serial log CSV captured by launchpad_loadcell_live_gui.py
and answers:
  1. How much does each F/T channel shift per °C of temperature change?
  2. Is that sensitivity constant across the temperature range (linearity)?
  3. What are the expected zero-load readings at 10 / 25 / 40 / 55 °C?

Usage
-----
  python thermal_characterization_analysis.py
      [--ft   path/to/loadcell_slave1_*.csv]
      [--ser  path/to/serial_log_*.csv]
      [--out  reports/host_master]          # output directory, default same as --ft
      [--plateau-soak  120]                 # seconds temperature must be stable
      [--plateau-std   0.5]                 # max °C std-dev to call a window "stable"

If --ft / --ser are omitted the script picks the most-recent pair from the default
reports/host_master directory.

Output files
------------
  thermal_report_<timestamp>.txt   — human-readable summary (key metrics)
  thermal_report_<timestamp>.csv   — per-plateau statistics for every channel
  thermal_sensitivity_<timestamp>.csv — linear-fit coefficients per channel
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import NamedTuple

# ── optional numeric libraries ──────────────────────────────────────────────
try:
    import numpy as np
    _HAS_NP = True
except ImportError:
    np = None  # type: ignore[assignment]
    _HAS_NP = False

# ── constants ────────────────────────────────────────────────────────────────
CHANNELS = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
UNITS    = {"Fx": "N", "Fy": "N", "Fz": "N", "Tx": "N·mm", "Ty": "N·mm", "Tz": "N·mm"}

# Temperature setpoints the experimenter targets (used for interpolated look-up table).
TARGET_TEMPS_C = [10.0, 25.0, 40.0, 55.0]

DEFAULT_REPORTS_DIR = (
    Path(__file__).resolve().parent.parent / "reports" / "host_master"
)

# ── data structures ──────────────────────────────────────────────────────────
class FTSample(NamedTuple):
    ts:  float          # wall-clock Unix timestamp
    Fx:  float
    Fy:  float
    Fz:  float
    Tx:  float
    Ty:  float
    Tz:  float

class TempSample(NamedTuple):
    ts:   float         # wall-clock Unix timestamp
    t4c:  float         # LTC2990 @ 0x4C  (°C)
    t4f:  float         # LTC2990 @ 0x4F  (°C)

class Plateau(NamedTuple):
    start_ts: float
    end_ts:   float
    n:        int
    temp_mean: float
    temp_std:  float
    ft_mean:   dict[str, float]   # channel → mean value
    ft_std:    dict[str, float]   # channel → std dev


# ── CSV loaders ───────────────────────────────────────────────────────────────
def load_ft_csv(path: Path) -> list[FTSample]:
    """Load loadcell_slave1_*.csv.  Decoded values are in the decoded_json column."""
    samples: list[FTSample] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = float(row["timestamp"])
                blob = row.get("decoded_json", "").strip()
                if not blob:
                    continue
                d = json.loads(blob)
                samples.append(FTSample(
                    ts=ts,
                    Fx=float(d.get("Fx", math.nan)),
                    Fy=float(d.get("Fy", math.nan)),
                    Fz=float(d.get("Fz", math.nan)),
                    Tx=float(d.get("Tx", math.nan)),
                    Ty=float(d.get("Ty", math.nan)),
                    Tz=float(d.get("Tz", math.nan)),
                ))
            except Exception:
                continue
    return samples


def load_serial_csv(path: Path) -> list[TempSample]:
    """Parse serial_log_*.csv into temperature samples.

    Handles two line formats:
      ESP32S3 diode format  : [4C_DIODE] ... TINT=31.72C
                              [4F_DIODE] ... TINT=32.04C
      Compact MKR1000 format: T:29.9/30.285 H:42.1 CO2:458 ...
                              (first value = T4C, second = T4F)
    """
    t4c_last = math.nan
    t4f_last = math.nan
    samples: list[TempSample] = []
    pat_diode   = re.compile(r"\[(4[CF])_DIODE\].*TINT=([-\d.]+)C")
    pat_compact = re.compile(r"(?:^|\s)T:([-\d.]+)/([-\d.]+)")

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts   = float(row["timestamp"])
                line = row.get("line", "").strip()
            except Exception:
                continue

            # ── ESP32S3 diode format ──────────────────────────────────────
            m = pat_diode.match(line)
            if m:
                tag  = m.group(1)
                tval = float(m.group(2))
                if 10.0 <= tval <= 100.0:
                    if tag == "4C":
                        t4c_last = tval
                    elif tag == "4F":
                        t4f_last = tval
                if math.isfinite(t4c_last) and math.isfinite(t4f_last):
                    samples.append(TempSample(ts=ts, t4c=t4c_last, t4f=t4f_last))
                continue

            # ── Compact MKR1000 format: T:val1/val2 ──────────────────────
            m2 = pat_compact.search(line)
            if m2:
                try:
                    v1 = float(m2.group(1))
                    v2 = float(m2.group(2))
                    if 10.0 <= v1 <= 100.0 and 10.0 <= v2 <= 100.0:
                        samples.append(TempSample(ts=ts, t4c=v1, t4f=v2))
                    elif 10.0 <= v1 <= 100.0:
                        samples.append(TempSample(ts=ts, t4c=v1, t4f=v1))
                except Exception:
                    pass

    return samples


# ── interpolation ─────────────────────────────────────────────────────────────
def interp_temp_at(ts_ft: list[float], temp_samples: list[TempSample],
                   use_channel: str = "t4f") -> list[float]:
    """Linear interpolation of temperature onto F/T timestamps."""
    if not temp_samples:
        return [math.nan] * len(ts_ft)

    ts_t   = [s.ts  for s in temp_samples]
    vals_t = [getattr(s, use_channel) for s in temp_samples]

    result: list[float] = []
    for ts in ts_ft:
        if ts <= ts_t[0]:
            result.append(vals_t[0])
            continue
        if ts >= ts_t[-1]:
            result.append(vals_t[-1])
            continue
        # binary search
        lo, hi = 0, len(ts_t) - 1
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if ts_t[mid] <= ts:
                lo = mid
            else:
                hi = mid
        frac = (ts - ts_t[lo]) / (ts_t[hi] - ts_t[lo]) if (ts_t[hi] - ts_t[lo]) > 0 else 0.0
        result.append(vals_t[lo] + frac * (vals_t[hi] - vals_t[lo]))

    return result


# ── plateau detection ─────────────────────────────────────────────────────────
def detect_plateaus(
    ft_samples: list[FTSample],
    temp_at_ft: list[float],
    soak_window_s: float = 120.0,
    stability_std_c: float = 0.5,
    min_samples: int = 30,
) -> list[Plateau]:
    """
    Scan in a rolling window of width soak_window_s. Any consecutive window
    whose temperature std-dev < stability_std_c qualifies as a plateau region.
    Adjacent qualifying windows are merged.
    """
    n = len(ft_samples)
    if n < min_samples:
        return []

    ts_arr  = [s.ts for s in ft_samples]
    in_plat = [False] * n

    # mark samples that fall inside at least one stable window
    left = 0
    for right in range(n):
        # advance left so window width <= soak_window_s
        while ts_arr[right] - ts_arr[left] > soak_window_s:
            left += 1
        # compute temp std in [left .. right]
        temps_win = [temp_at_ft[i] for i in range(left, right + 1)
                     if math.isfinite(temp_at_ft[i])]
        if len(temps_win) < 5:
            continue
        mean_t = sum(temps_win) / len(temps_win)
        var_t  = sum((t - mean_t) ** 2 for t in temps_win) / len(temps_win)
        std_t  = math.sqrt(var_t)
        if std_t <= stability_std_c:
            for i in range(left, right + 1):
                in_plat[i] = True

    # collect contiguous runs of True
    plateaus: list[Plateau] = []
    i = 0
    while i < n:
        if not in_plat[i]:
            i += 1
            continue
        j = i
        while j < n and in_plat[j]:
            j += 1
        # segment [i, j)
        seg_len = j - i
        if seg_len < min_samples:
            i = j
            continue

        temps_seg = [temp_at_ft[k] for k in range(i, j) if math.isfinite(temp_at_ft[k])]
        mean_t = sum(temps_seg) / len(temps_seg) if temps_seg else math.nan
        var_t  = sum((t - mean_t) ** 2 for t in temps_seg) / len(temps_seg) if temps_seg else math.nan
        std_t  = math.sqrt(var_t) if math.isfinite(var_t) else math.nan

        ft_mean: dict[str, float] = {}
        ft_std:  dict[str, float] = {}
        for ch in CHANNELS:
            vals = [getattr(ft_samples[k], ch) for k in range(i, j) if math.isfinite(getattr(ft_samples[k], ch))]
            if vals:
                mv = sum(vals) / len(vals)
                sv = math.sqrt(sum((v - mv) ** 2 for v in vals) / len(vals))
                ft_mean[ch] = mv
                ft_std[ch]  = sv
            else:
                ft_mean[ch] = math.nan
                ft_std[ch]  = math.nan

        plateaus.append(Plateau(
            start_ts  = ft_samples[i].ts,
            end_ts    = ft_samples[j - 1].ts,
            n         = seg_len,
            temp_mean = mean_t,
            temp_std  = std_t,
            ft_mean   = ft_mean,
            ft_std    = ft_std,
        ))
        i = j

    return plateaus


# ── linear sensitivity fit ────────────────────────────────────────────────────
def fit_thermal_sensitivity(
    plateaus: list[Plateau],
) -> dict[str, dict]:
    """
    Fit  F/T_channel = slope * T + intercept  across all plateau mean values.
    Returns per-channel dict with keys: slope, intercept, r2, units.
    """
    results: dict[str, dict] = {}
    temps = [p.temp_mean for p in plateaus if math.isfinite(p.temp_mean)]

    for ch in CHANNELS:
        vals = [p.ft_mean[ch] for p in plateaus if math.isfinite(p.ft_mean.get(ch, math.nan))]
        t_for_ch = [p.temp_mean for p in plateaus if math.isfinite(p.ft_mean.get(ch, math.nan))]

        if len(vals) < 2:
            results[ch] = {"slope": math.nan, "intercept": math.nan, "r2": math.nan,
                           "units": UNITS[ch]}
            continue

        n = len(vals)
        mean_t = sum(t_for_ch) / n
        mean_v = sum(vals) / n
        sxx = sum((t - mean_t) ** 2 for t in t_for_ch)
        sxy = sum((t - mean_t) * (v - mean_v) for t, v in zip(t_for_ch, vals))
        slope     = sxy / sxx if sxx > 0 else math.nan
        intercept = mean_v - slope * mean_t if math.isfinite(slope) else math.nan

        # R²
        ss_tot = sum((v - mean_v) ** 2 for v in vals)
        ss_res = sum((v - (slope * t + intercept)) ** 2 for t, v in zip(t_for_ch, vals))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else math.nan

        results[ch] = {
            "slope":     slope,
            "intercept": intercept,
            "r2":        r2,
            "units":     UNITS[ch],
        }

    return results


# ── prediction table ──────────────────────────────────────────────────────────
def predict_at_targets(
    sensitivity: dict[str, dict],
    targets: list[float],
) -> dict[float, dict[str, float]]:
    """Predict F/T value for each channel at each target temperature."""
    table: dict[float, dict[str, float]] = {}
    for t in targets:
        table[t] = {}
        for ch in CHANNELS:
            s = sensitivity[ch]["slope"]
            i = sensitivity[ch]["intercept"]
            table[t][ch] = s * t + i if math.isfinite(s) and math.isfinite(i) else math.nan
    return table


# ── report writers ────────────────────────────────────────────────────────────
def write_plateau_csv(plateaus: list[Plateau], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["start_ts", "end_ts", "duration_s", "n_samples",
                    "temp_mean_C", "temp_std_C"]
                   + [f"{ch}_mean_{UNITS[ch]}" for ch in CHANNELS]
                   + [f"{ch}_std_{UNITS[ch]}"  for ch in CHANNELS])
        for p in plateaus:
            row = [
                f"{p.start_ts:.3f}", f"{p.end_ts:.3f}",
                f"{p.end_ts - p.start_ts:.1f}", p.n,
                f"{p.temp_mean:.3f}", f"{p.temp_std:.4f}",
            ]
            for ch in CHANNELS:
                row.append(f"{p.ft_mean[ch]:.6f}" if math.isfinite(p.ft_mean[ch]) else "")
            for ch in CHANNELS:
                row.append(f"{p.ft_std[ch]:.6f}"  if math.isfinite(p.ft_std[ch])  else "")
            w.writerow(row)


def write_sensitivity_csv(sens: dict[str, dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["channel", "units", "slope_per_C", "intercept", "R2",
                    "sensitivity_per_10C"])
        for ch in CHANNELS:
            s = sens[ch]
            slope10 = s["slope"] * 10 if math.isfinite(s["slope"]) else math.nan
            w.writerow([
                ch, s["units"],
                f"{s['slope']:.6f}",
                f"{s['intercept']:.6f}",
                f"{s['r2']:.4f}",
                f"{slope10:.6f}",
            ])


def write_text_report(
    plateaus: list[Plateau],
    sens: dict[str, dict],
    pred_table: dict[float, dict[str, float]],
    ft_path: Path,
    ser_path: Path,
    output_path: Path,
) -> None:
    lines: list[str] = []
    hr = "=" * 70

    lines += [
        hr,
        "  ATI F/T SENSOR — THERMAL DRIFT CHARACTERIZATION REPORT",
        hr,
        f"  F/T capture  : {ft_path.name}",
        f"  Serial log   : {ser_path.name}",
        f"  Generated    : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"  Stable plateaus detected : {len(plateaus)}",
        "",
    ]

    # ── Plateau table ──────────────────────────────────────────────────────
    lines.append("SECTION 1 — STABLE TEMPERATURE PLATEAUS")
    lines.append("-" * 70)
    hdr = f"{'#':>3} {'Temp(°C)':>9} {'±std':>6} {'dur(s)':>7} {'n':>6}  " + \
          "  ".join(f"{ch:>10}" for ch in CHANNELS)
    lines.append(hdr)
    for idx, p in enumerate(plateaus, 1):
        row  = f"{idx:>3} {p.temp_mean:>9.2f} {p.temp_std:>6.3f} "
        row += f"{p.end_ts-p.start_ts:>7.0f} {p.n:>6}  "
        row += "  ".join(
            f"{p.ft_mean[ch]:>10.4f}" if math.isfinite(p.ft_mean[ch]) else f"{'N/A':>10}"
            for ch in CHANNELS
        )
        lines.append(row)

    lines += ["",
              "  Values above are zero-load means (N / N·mm).  These ARE the",
              "  thermal offset at each temperature — the 'empty palm' baseline.",
              ""]

    # ── Sensitivity table ──────────────────────────────────────────────────
    lines.append("SECTION 2 — THERMAL SENSITIVITY (linear fit across all plateaus)")
    lines.append("-" * 70)
    lines.append(f"  {'Channel':>8}  {'Slope/°C':>12}  {'Shift/10°C':>12}  "
                 f"{'Intercept':>12}  {'R²':>6}  Units")
    for ch in CHANNELS:
        s = sens[ch]
        slope10 = s["slope"] * 10 if math.isfinite(s["slope"]) else math.nan
        lines.append(
            f"  {ch:>8}  {s['slope']:>12.6f}  {slope10:>12.5f}  "
            f"{s['intercept']:>12.4f}  {s['r2']:>6.4f}  {s['units']}"
        )

    lines += [
        "",
        "  Interpretation:",
        "    • Slope/°C  = shift in measured value for every 1°C change",
        "    • Shift/10°C = shift over a 10°C span (practical comparison unit)",
        "    • R²        = linearity quality  (1.0 = perfectly linear)",
        "    • Low R² means thermal response is nonlinear — segment-fit needed.",
        "",
    ]

    # ── Predicted zero-load table ─────────────────────────────────────────
    lines.append("SECTION 3 — PREDICTED ZERO-LOAD VALUES AT TARGET TEMPERATURES")
    lines.append("-" * 70)
    hdr2 = f"  {'Temp(°C)':>9}  " + "  ".join(f"{ch:>10}" for ch in CHANNELS)
    lines.append(hdr2)
    for t in sorted(pred_table.keys()):
        row = f"  {t:>9.1f}  "
        row += "  ".join(
            f"{pred_table[t][ch]:>10.4f}" if math.isfinite(pred_table[t][ch]) else f"{'--':>10}"
            for ch in CHANNELS
        )
        lines.append(row)

    lines += [
        "",
        "  These are extrapolated / interpolated from the linear fit.",
        "  Cross-check with actual plateau values in Section 1 where available.",
        "",
    ]

    # ── Experimental range summary ─────────────────────────────────────────
    lines.append("SECTION 4 — MEASUREMENT RANGE ANALYSIS")
    lines.append("-" * 70)
    for ch in CHANNELS:
        preds = [pred_table[t][ch] for t in sorted(pred_table.keys())
                 if math.isfinite(pred_table[t][ch])]
        if len(preds) >= 2:
            span = max(preds) - min(preds)
            lines.append(
                f"  {ch}: total span across {TARGET_TEMPS_C[0]}–{TARGET_TEMPS_C[-1]}°C "
                f"= {span:.4f} {UNITS[ch]}"
            )

    lines += ["", hr, "  END OF REPORT", hr, ""]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


# ── file discovery ────────────────────────────────────────────────────────────
def find_latest_pair(reports_dir: Path) -> tuple[Path | None, Path | None]:
    ft_files  = sorted(reports_dir.glob("loadcell_slave1_*.csv"),  key=lambda p: p.stat().st_mtime)
    ser_files = sorted(reports_dir.glob("serial_log_*.csv"),        key=lambda p: p.stat().st_mtime)
    ft  = ft_files[-1]  if ft_files  else None
    ser = ser_files[-1] if ser_files else None
    return ft, ser


# ── main ──────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="ATI F/T thermal drift characterization")
    ap.add_argument("--ft",            help="Path to loadcell_slave1_*.csv")
    ap.add_argument("--ser",           help="Path to serial_log_*.csv")
    ap.add_argument("--out",           help="Output directory (default: same as --ft)")
    ap.add_argument("--plateau-soak",  type=float, default=120.0,
                    help="Seconds temperature must be stable to count as a plateau (default: 120)")
    ap.add_argument("--plateau-std",   type=float, default=0.5,
                    help="Max °C std-dev within plateau window (default: 0.5)")
    ap.add_argument("--temp-channel",  default="t4f", choices=["t4c", "t4f"],
                    help="Which temperature sensor to use (default: t4f)")
    args = ap.parse_args(argv)

    # ── locate files ──────────────────────────────────────────────────────
    reports_dir = DEFAULT_REPORTS_DIR
    if args.ft:
        ft_path = Path(args.ft)
    else:
        ft_path, _ = find_latest_pair(reports_dir)
    if args.ser:
        ser_path = Path(args.ser)
    else:
        _, ser_path = find_latest_pair(reports_dir)

    if ft_path is None or not ft_path.exists():
        print("ERROR: Could not find loadcell CSV. Pass --ft <path>", file=sys.stderr)
        sys.exit(1)
    if ser_path is None or not ser_path.exists():
        print("ERROR: Could not find serial log CSV. Pass --ser <path>", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out) if args.out else ft_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    ts_tag = time.strftime("%Y%m%d_%H%M%S")

    print(f"Loading F/T data   : {ft_path}")
    print(f"Loading serial log : {ser_path}")

    # ── load & align data ─────────────────────────────────────────────────
    ft_samples   = load_ft_csv(ft_path)
    temp_samples = load_serial_csv(ser_path)

    if not ft_samples:
        print("ERROR: No valid F/T samples found in loadcell CSV.", file=sys.stderr)
        sys.exit(1)
    if not temp_samples:
        print("ERROR: No valid temperature samples found in serial log.", file=sys.stderr)
        sys.exit(1)

    print(f"  F/T samples : {len(ft_samples)}")
    print(f"  Temp samples: {len(temp_samples)}")

    ts_ft       = [s.ts for s in ft_samples]
    temp_at_ft  = interp_temp_at(ts_ft, temp_samples, use_channel=args.temp_channel)

    valid_temps = [t for t in temp_at_ft if math.isfinite(t)]
    if not valid_temps:
        print("ERROR: No temperature data overlaps the F/T timestamp range.", file=sys.stderr)
        sys.exit(1)

    print(f"  Temperature range: {min(valid_temps):.1f}°C – {max(valid_temps):.1f}°C")

    # ── detect plateaus ───────────────────────────────────────────────────
    plateaus = detect_plateaus(
        ft_samples, temp_at_ft,
        soak_window_s  = args.plateau_soak,
        stability_std_c = args.plateau_std,
    )

    if len(plateaus) < 2:
        print(
            f"\nWARNING: Only {len(plateaus)} stable plateau(s) detected.\n"
            f"  The experiment may not have run long enough at each temperature,\n"
            f"  or the temperature did not stabilize within ±{args.plateau_std}°C.\n"
            f"  Try --plateau-std 1.0 or --plateau-soak 60 to relax detection.\n",
            file=sys.stderr,
        )
        if len(plateaus) < 2:
            sys.exit(1)

    print(f"  Detected {len(plateaus)} plateau(s):")
    for p in plateaus:
        print(f"    {p.temp_mean:5.1f}°C ± {p.temp_std:.3f}  "
              f"  dur={p.end_ts-p.start_ts:.0f}s  n={p.n}")

    # ── sensitivity fit ───────────────────────────────────────────────────
    sens = fit_thermal_sensitivity(plateaus)

    # ── prediction table ──────────────────────────────────────────────────
    pred_table = predict_at_targets(sens, TARGET_TEMPS_C)

    # ── write outputs ─────────────────────────────────────────────────────
    plateau_csv_path = out_dir / f"thermal_plateaus_{ts_tag}.csv"
    sens_csv_path    = out_dir / f"thermal_sensitivity_{ts_tag}.csv"
    report_txt_path  = out_dir / f"thermal_report_{ts_tag}.txt"

    write_plateau_csv(plateaus, plateau_csv_path)
    write_sensitivity_csv(sens, sens_csv_path)
    write_text_report(plateaus, sens, pred_table, ft_path, ser_path, report_txt_path)

    print(f"\nOutput files written to: {out_dir}")
    print(f"  {plateau_csv_path.name}")
    print(f"  {sens_csv_path.name}")
    print(f"  {report_txt_path.name}")


if __name__ == "__main__":
    main()
