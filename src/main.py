"""Entry point for arm movement to sound texture control."""

from __future__ import annotations

import argparse
import time

from .capture import ArmCapture
from .features import FeatureExtractor
from .mapping import MovementMapper
from .osc_out import OscOut


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Arm movement sonification to REAPER via OSC")
    parser.add_argument("--osc-host", default="127.0.0.1", help="OSC host for REAPER")
    parser.add_argument("--osc-port", type=int, default=9000, help="OSC port for REAPER")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--fps", type=float, default=30.0, help="Loop target FPS")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    capture = ArmCapture(camera_index=args.camera)
    features = FeatureExtractor()
    mapper = MovementMapper()
    osc = OscOut(host=args.osc_host, port=args.osc_port)

    frame_sleep = 1.0 / max(args.fps, 1.0)

    print("Running. Press Ctrl+C to stop.")
    try:
        while True:
            landmarks = capture.read_arm_landmarks()
            if landmarks is None:
                time.sleep(frame_sleep)
                continue

            current = features.compute(
                shoulder=landmarks.shoulder,
                elbow=landmarks.elbow,
                wrist=landmarks.wrist,
            )
            controls = mapper.to_sound_controls(current)
            osc.send_controls(controls)
            time.sleep(frame_sleep)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        capture.release()


if __name__ == "__main__":
    main()
