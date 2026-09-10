#!/usr/bin/env python3
"""
Webcam + serial validator for LP-AM243 LED demo.

Checks two things in one run:
1) Firmware function activity from UART logs.
2) Color activity from webcam ROI(s).

Writes JSON + text report and exits non-zero on failure.
"""

from __future__ import annotations

import argparse
import json
import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import serial


EXPECTED_COLORS_DEFAULT = ["RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE", "OFF"]


@dataclass
class RoiSpec:
    name: str
    x: int
    y: int
    w: int
    h: int


@dataclass
class SerialState:
    connected: bool = False
    error: Optional[str] = None
    started: bool = False
    completed: bool = False
    rgb_step_count: int = 0
    lines_seen: int = 0
    key_lines: List[str] = field(default_factory=list)


@dataclass
class CameraState:
    opened: bool = False
    error: Optional[str] = None
    frames_seen: int = 0
    rois: Dict[str, Dict[str, object]] = field(default_factory=dict)


class SerialMonitor(threading.Thread):
    def __init__(self, port: str, baud: int, stop_evt: threading.Event) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.stop_evt = stop_evt
        self.state = SerialState()
        self._line_q: "queue.Queue[str]" = queue.Queue()

    def run(self) -> None:
        try:
            with serial.Serial(self.port, self.baud, timeout=0.25) as ser:
                self.state.connected = True
                while not self.stop_evt.is_set():
                    data = ser.read(1024)
                    if not data:
                        continue
                    text = data.decode(errors="replace")
                    for line in text.splitlines():
                        self._line_q.put(line)
        except Exception as exc:  # pragma: no cover
            self.state.error = str(exc)

    def drain(self) -> None:
        while True:
            try:
                line = self._line_q.get_nowait()
            except queue.Empty:
                return
            self.state.lines_seen += 1
            self._handle_line(line)

    def _handle_line(self, line: str) -> None:
        if "[DEMO] Combined LED show started" in line:
            self.state.started = True
            self.state.key_lines.append(line)
        elif "[DEMO] Combined LED show completed" in line:
            self.state.completed = True
            self.state.key_lines.append(line)
        elif "[RGBx6] Step" in line:
            self.state.rgb_step_count += 1
            if self.state.rgb_step_count <= 10:
                self.state.key_lines.append(line)


def parse_roi_spec(raw: str) -> RoiSpec:
    # Format: name:x,y,w,h
    if ":" not in raw:
        raise ValueError(f"Invalid ROI '{raw}'. Use name:x,y,w,h")
    name, box = raw.split(":", 1)
    parts = [p.strip() for p in box.split(",")]
    if len(parts) != 4:
        raise ValueError(f"Invalid ROI '{raw}'. Use name:x,y,w,h")
    x, y, w, h = (int(p) for p in parts)
    if w <= 0 or h <= 0:
        raise ValueError(f"Invalid ROI '{raw}'. Width and height must be > 0")
    return RoiSpec(name=name.strip(), x=x, y=y, w=w, h=h)


def classify_color_bgr(mean_bgr: np.ndarray) -> str:
    pixel = np.uint8([[mean_bgr]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0, 0]
    h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

    if v < 40:
        return "OFF"
    if s < 35 and v >= 170:
        return "WHITE"

    if h <= 12 or h >= 165:
        return "RED"
    if 20 <= h <= 35:
        return "YELLOW"
    if 36 <= h <= 89:
        return "GREEN"
    if 90 <= h <= 105:
        return "CYAN"
    if 106 <= h <= 140:
        return "BLUE"
    if 141 <= h <= 164:
        return "MAGENTA"
    return "UNKNOWN"


def ensure_roi_bounds(roi: RoiSpec, frame_w: int, frame_h: int) -> RoiSpec:
    x = max(0, min(roi.x, frame_w - 1))
    y = max(0, min(roi.y, frame_h - 1))
    w = min(roi.w, frame_w - x)
    h = min(roi.h, frame_h - y)
    return RoiSpec(name=roi.name, x=x, y=y, w=w, h=h)


def make_report_dir(base_dir: Path) -> Path:
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out = base_dir / f"webcam_validation_{now}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def run_simulation(duration_sec: float, rois: List[RoiSpec], expected_colors: List[str]) -> Tuple[SerialState, CameraState]:
    serial_state = SerialState(connected=True, started=True)
    camera_state = CameraState(opened=True)

    timeline = ["RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE", "OFF"]
    loops = max(1, int(duration_sec))
    camera_state.frames_seen = loops

    for roi in rois:
        observed = set()
        samples: List[Dict[str, object]] = []
        for i in range(loops):
            color = timeline[i % len(timeline)]
            observed.add(color)
            samples.append({"t_sec": float(i), "color": color})
            serial_state.rgb_step_count += 1
            serial_state.lines_seen += 1
            serial_state.key_lines.append(f"[RGBx6] Step {i} color={color}")
        camera_state.rois[roi.name] = {
            "observed_colors": sorted(observed),
            "samples": samples,
        }

    serial_state.completed = True
    return serial_state, camera_state


def run_camera_capture(
    camera_index: int,
    rois: List[RoiSpec],
    duration_sec: float,
    show: bool,
    sample_interval: float,
    save_images: bool,
    out_dir: Path,
) -> CameraState:
    state = CameraState()
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        state.error = f"Cannot open webcam index {camera_index}"
        return state

    state.opened = True
    images_dir: Optional[Path] = None
    if save_images:
        images_dir = out_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

    for roi in rois:
        state.rois[roi.name] = {
            "observed_colors": set(),
            "samples": [],
        }

    t_start = time.time()
    t_next = t_start

    while True:
        now = time.time()
        if now - t_start >= duration_sec:
            break

        ok, frame = cap.read()
        if not ok:
            continue

        state.frames_seen += 1
        frame_h, frame_w = frame.shape[:2]

        if now >= t_next:
            sample_idx = int((now - t_start) / max(sample_interval, 1e-3))
            annotated = frame.copy()
            for roi in rois:
                clipped = ensure_roi_bounds(roi, frame_w, frame_h)
                crop = frame[clipped.y : clipped.y + clipped.h, clipped.x : clipped.x + clipped.w]
                if crop.size == 0:
                    continue
                mean_bgr = crop.mean(axis=(0, 1))
                color = classify_color_bgr(mean_bgr)

                cv2.rectangle(annotated, (clipped.x, clipped.y), (clipped.x + clipped.w, clipped.y + clipped.h), (0, 255, 0), 2)
                cv2.putText(
                    annotated,
                    f"{roi.name}:{color}",
                    (clipped.x, max(20, clipped.y - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2,
                )

                item = state.rois[roi.name]
                item["observed_colors"].add(color)
                item["samples"].append({
                    "t_sec": round(now - t_start, 3),
                    "color": color,
                    "mean_bgr": [round(float(x), 2) for x in mean_bgr],
                })

                if images_dir is not None:
                    roi_file = images_dir / f"sample_{sample_idx:04d}_{roi.name}_{color}.png"
                    cv2.imwrite(str(roi_file), crop)

            if images_dir is not None:
                frame_file = images_dir / f"sample_{sample_idx:04d}_frame.png"
                cv2.imwrite(str(frame_file), annotated)

            t_next = now + sample_interval

        if show:
            disp = frame.copy()
            for roi in rois:
                clipped = ensure_roi_bounds(roi, frame_w, frame_h)
                cv2.rectangle(disp, (clipped.x, clipped.y), (clipped.x + clipped.w, clipped.y + clipped.h), (0, 255, 0), 2)
                cv2.putText(
                    disp,
                    roi.name,
                    (clipped.x, max(20, clipped.y - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            cv2.imshow("webcam_led_validator", disp)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

    cap.release()
    if show:
        cv2.destroyAllWindows()

    # Convert sets to sorted lists for serialization.
    for roi_name, item in state.rois.items():
        item["observed_colors"] = sorted(item["observed_colors"])

    return state


def evaluate(
    serial_state: SerialState,
    camera_state: CameraState,
    expected_colors: List[str],
    min_rgb_steps: int,
    camera_only: bool,
) -> Dict[str, object]:
    if camera_only:
        function_pass = True
    else:
        function_pass = (
            serial_state.connected
            and serial_state.started
            and serial_state.rgb_step_count >= min_rgb_steps
            and (serial_state.completed or serial_state.rgb_step_count >= min_rgb_steps)
        )

    roi_results: Dict[str, Dict[str, object]] = {}
    color_pass_all = True
    for roi_name, item in camera_state.rois.items():
        observed = set(item.get("observed_colors", []))
        missing = [c for c in expected_colors if c not in observed]
        roi_pass = len(missing) == 0
        color_pass_all = color_pass_all and roi_pass
        roi_results[roi_name] = {
            "observed_colors": sorted(observed),
            "missing_colors": missing,
            "pass": roi_pass,
            "sample_count": len(item.get("samples", [])),
        }

    camera_ok = camera_state.opened and camera_state.frames_seen > 0
    overall_pass = function_pass and color_pass_all and camera_ok

    return {
        "pass": overall_pass,
        "function_pass": function_pass,
        "color_pass": color_pass_all,
        "camera_pass": camera_ok,
        "roi_results": roi_results,
    }


def write_reports(
    out_dir: Path,
    serial_state: SerialState,
    camera_state: CameraState,
    eval_result: Dict[str, object],
    args: argparse.Namespace,
) -> Tuple[Path, Path]:
    report_json = {
        "timestamp": datetime.now().isoformat(),
        "args": {
            "camera_index": args.camera_index,
            "serial_port": args.serial_port,
            "baud": args.baud,
            "duration_sec": args.duration_sec,
            "sample_interval_sec": args.sample_interval_sec,
            "expected_colors": args.expected_colors,
            "min_rgb_steps": args.min_rgb_steps,
            "camera_only": args.camera_only,
            "simulate": args.simulate,
        },
        "serial": {
            "connected": serial_state.connected,
            "error": serial_state.error,
            "started": serial_state.started,
            "completed": serial_state.completed,
            "rgb_step_count": serial_state.rgb_step_count,
            "lines_seen": serial_state.lines_seen,
            "key_lines": serial_state.key_lines,
        },
        "camera": {
            "opened": camera_state.opened,
            "error": camera_state.error,
            "frames_seen": camera_state.frames_seen,
            "rois": camera_state.rois,
        },
        "evaluation": eval_result,
    }

    json_path = out_dir / "validation_report.json"
    txt_path = out_dir / "validation_report.txt"

    json_path.write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    lines = [
        "LP-AM243 LED Webcam Validation Report",
        "=" * 40,
        f"Timestamp: {report_json['timestamp']}",
        "",
        f"Overall PASS: {eval_result['pass']}",
        f"Function PASS: {eval_result['function_pass']}",
        f"Color PASS: {eval_result['color_pass']}",
        f"Camera PASS: {eval_result['camera_pass']}",
        "",
        "Function Summary:",
        f"- Serial connected: {serial_state.connected}",
        f"- Demo started marker seen: {serial_state.started}",
        f"- Demo completed marker seen: {serial_state.completed}",
        f"- RGB step lines seen: {serial_state.rgb_step_count}",
        "",
        "Color Summary by ROI:",
    ]

    for roi_name, roi_eval in eval_result["roi_results"].items():
        lines.append(f"- {roi_name}: pass={roi_eval['pass']}")
        lines.append(f"  observed={', '.join(roi_eval['observed_colors'])}")
        lines.append(f"  missing={', '.join(roi_eval['missing_colors']) if roi_eval['missing_colors'] else '(none)'}")

    lines.append("")
    lines.append("Key Serial Lines:")
    for line in serial_state.key_lines[:40]:
        lines.append(f"- {line}")

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate LP-AM243 LED demo with webcam + UART logs")
    p.add_argument("--camera-index", type=int, default=0, help="OpenCV camera index")
    p.add_argument("--serial-port", default="COM10", help="UART port for firmware logs")
    p.add_argument("--baud", type=int, default=115200, help="UART baud rate")
    p.add_argument("--duration-sec", type=float, default=20.0, help="Capture duration")
    p.add_argument("--sample-interval-sec", type=float, default=0.15, help="Color sample period")
    p.add_argument("--min-rgb-steps", type=int, default=6, help="Minimum RGB step lines for function pass")
    p.add_argument("--expected-colors", nargs="+", default=EXPECTED_COLORS_DEFAULT, help="Expected color names")
    p.add_argument("--roi", action="append", default=[], help="ROI as name:x,y,w,h (repeatable)")
    p.add_argument("--output-dir", default="reports", help="Output base folder")
    p.add_argument("--show", action="store_true", help="Show webcam preview with ROI overlays")
    p.add_argument("--save-images", action="store_true", help="Save sampled webcam frames/crops into report folder")
    p.add_argument("--camera-only", action="store_true", help="Pass function check without serial markers (webcam-only verification)")
    p.add_argument("--simulate", action="store_true", help="Use simulation mode (no hardware needed)")
    return p


def main() -> int:
    args = build_arg_parser().parse_args()

    rois = [parse_roi_spec(raw) for raw in args.roi]
    if not rois:
        # Full-frame fallback to avoid extra setup friction.
        rois = [RoiSpec("full_frame", 0, 0, 640, 480)]

    out_dir = make_report_dir(Path(args.output_dir))

    if args.simulate:
        serial_state, camera_state = run_simulation(args.duration_sec, rois, args.expected_colors)
    else:
        stop_evt = threading.Event()
        serial_mon = SerialMonitor(args.serial_port, args.baud, stop_evt)
        serial_mon.start()

        camera_state = run_camera_capture(
            camera_index=args.camera_index,
            rois=rois,
            duration_sec=args.duration_sec,
            show=args.show,
            sample_interval=args.sample_interval_sec,
            save_images=args.save_images,
            out_dir=out_dir,
        )

        stop_evt.set()
        serial_mon.join(timeout=2.0)
        serial_mon.drain()
        serial_state = serial_mon.state

    eval_result = evaluate(
        serial_state=serial_state,
        camera_state=camera_state,
        expected_colors=args.expected_colors,
        min_rgb_steps=args.min_rgb_steps,
        camera_only=args.camera_only,
    )

    json_path, txt_path = write_reports(
        out_dir=out_dir,
        serial_state=serial_state,
        camera_state=camera_state,
        eval_result=eval_result,
        args=args,
    )

    print(f"[REPORT] JSON: {json_path}")
    print(f"[REPORT] TEXT: {txt_path}")
    print(f"[RESULT] PASS={eval_result['pass']}")

    return 0 if eval_result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
