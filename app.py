"""Aplicación única para controlar REAPER con movimiento de brazo.

Uso:
    python app.py --osc-host 127.0.0.1 --osc-port 9000 --camera 0 --fps 30
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import mediapipe as mp
from pythonosc.udp_client import SimpleUDPClient

Point3D = Tuple[float, float, float]


@dataclass(slots=True)
class ArmLandmarks:
    shoulder: Point3D
    elbow: Point3D
    wrist: Point3D


@dataclass(slots=True)
class ArmFeatures:
    wrist_xyz: Point3D
    wrist_speed: float
    elbow_angle_deg: float


@dataclass(slots=True)
class SoundControls:
    cutoff: float
    resonance: float
    texture_drive: float


class ArmCapture:
    def __init__(self, camera_index: int = 0) -> None:
        self._camera = cv2.VideoCapture(camera_index)
        self._mp_pose = mp.solutions.pose
        self._pose = self._mp_pose.Pose(
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def read_arm_landmarks(self) -> Optional[ArmLandmarks]:
        ok, frame = self._camera.read()
        if not ok:
            return None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._pose.process(rgb)
        if not result.pose_landmarks:
            return None

        landmarks = result.pose_landmarks.landmark
        shoulder = self._to_point(landmarks[self._mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
        elbow = self._to_point(landmarks[self._mp_pose.PoseLandmark.RIGHT_ELBOW.value])
        wrist = self._to_point(landmarks[self._mp_pose.PoseLandmark.RIGHT_WRIST.value])
        return ArmLandmarks(shoulder=shoulder, elbow=elbow, wrist=wrist)

    def release(self) -> None:
        self._pose.close()
        self._camera.release()

    @staticmethod
    def _to_point(landmark: mp.framework.formats.landmark_pb2.NormalizedLandmark) -> Point3D:
        return (landmark.x, landmark.y, landmark.z)


class FeatureExtractor:
    def __init__(self) -> None:
        self._prev_wrist: Optional[Point3D] = None

    def compute(self, shoulder: Point3D, elbow: Point3D, wrist: Point3D) -> ArmFeatures:
        speed = self._compute_speed(wrist)
        angle = compute_angle_degrees(shoulder, elbow, wrist)
        return ArmFeatures(wrist_xyz=wrist, wrist_speed=speed, elbow_angle_deg=angle)

    def _compute_speed(self, wrist: Point3D) -> float:
        if self._prev_wrist is None:
            self._prev_wrist = wrist
            return 0.0
        dx = wrist[0] - self._prev_wrist[0]
        dy = wrist[1] - self._prev_wrist[1]
        dz = wrist[2] - self._prev_wrist[2]
        self._prev_wrist = wrist
        return math.sqrt(dx * dx + dy * dy + dz * dz)


class EmaFilter:
    def __init__(self, alpha: float = 0.25) -> None:
        self.alpha = alpha
        self._state: Optional[float] = None

    def apply(self, value: float) -> float:
        if self._state is None:
            self._state = value
            return value
        self._state = self.alpha * value + (1.0 - self.alpha) * self._state
        return self._state


class MovementMapper:
    def __init__(self) -> None:
        self._cutoff_filter = EmaFilter(alpha=0.2)
        self._resonance_filter = EmaFilter(alpha=0.3)
        self._drive_filter = EmaFilter(alpha=0.25)

    def to_controls(self, features: ArmFeatures) -> SoundControls:
        wrist_y = clamp01(1.0 - features.wrist_xyz[1])
        elbow_angle_norm = clamp01(features.elbow_angle_deg / 180.0)
        speed_norm = clamp01(features.wrist_speed * 20.0)

        cutoff = self._cutoff_filter.apply(wrist_y)
        resonance = self._resonance_filter.apply(1.0 - elbow_angle_norm)
        drive = self._drive_filter.apply(speed_norm)
        return SoundControls(cutoff=cutoff, resonance=resonance, texture_drive=drive)


class OscOut:
    def __init__(self, host: str, port: int) -> None:
        self._client = SimpleUDPClient(host, port)

    def send(self, controls: SoundControls) -> None:
        self._client.send_message("/arm/cutoff", controls.cutoff)
        self._client.send_message("/arm/resonance", controls.resonance)
        self._client.send_message("/arm/texture_drive", controls.texture_drive)


def compute_angle_degrees(a: Point3D, b: Point3D, c: Point3D) -> float:
    ab = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    cb = (c[0] - b[0], c[1] - b[1], c[2] - b[2])
    dot = (ab[0] * cb[0]) + (ab[1] * cb[1]) + (ab[2] * cb[2])
    ab_norm = math.sqrt((ab[0] * ab[0]) + (ab[1] * ab[1]) + (ab[2] * ab[2]))
    cb_norm = math.sqrt((cb[0] * cb[0]) + (cb[1] * cb[1]) + (cb[2] * cb[2]))
    if ab_norm == 0.0 or cb_norm == 0.0:
        return 0.0
    cos_angle = max(-1.0, min(1.0, dot / (ab_norm * cb_norm)))
    return math.degrees(math.acos(cos_angle))


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Movimiento de brazo a OSC para REAPER")
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=9000)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--fps", type=float, default=30.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    capture = ArmCapture(camera_index=args.camera)
    extractor = FeatureExtractor()
    mapper = MovementMapper()
    osc = OscOut(host=args.osc_host, port=args.osc_port)

    sleep_s = 1.0 / max(1.0, args.fps)
    print("App iniciada. Ctrl+C para salir.")

    try:
        while True:
            landmarks = capture.read_arm_landmarks()
            if landmarks is None:
                time.sleep(sleep_s)
                continue

            features = extractor.compute(landmarks.shoulder, landmarks.elbow, landmarks.wrist)
            controls = mapper.to_controls(features)
            osc.send(controls)
            time.sleep(sleep_s)
    except KeyboardInterrupt:
        print("Fin de sesión.")
    finally:
        capture.release()


if __name__ == "__main__":
    main()
