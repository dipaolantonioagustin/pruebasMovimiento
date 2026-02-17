"""Feature extraction utilities for arm movement sonification."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional, Tuple


Point3D = Tuple[float, float, float]


@dataclass(slots=True)
class ArmFeatures:
    """Computed movement descriptors from pose landmarks."""

    wrist_xyz: Point3D
    wrist_speed: float
    elbow_angle_deg: float


class FeatureExtractor:
    """Compute stable features frame-by-frame."""

    def __init__(self) -> None:
        self._previous_wrist: Optional[Point3D] = None

    def compute(self, shoulder: Point3D, elbow: Point3D, wrist: Point3D) -> ArmFeatures:
        wrist_speed = self._compute_speed(wrist)
        elbow_angle = compute_angle_degrees(shoulder, elbow, wrist)
        return ArmFeatures(wrist_xyz=wrist, wrist_speed=wrist_speed, elbow_angle_deg=elbow_angle)

    def _compute_speed(self, wrist: Point3D) -> float:
        if self._previous_wrist is None:
            self._previous_wrist = wrist
            return 0.0

        dx = wrist[0] - self._previous_wrist[0]
        dy = wrist[1] - self._previous_wrist[1]
        dz = wrist[2] - self._previous_wrist[2]
        self._previous_wrist = wrist
        return math.sqrt(dx * dx + dy * dy + dz * dz)


def compute_angle_degrees(a: Point3D, b: Point3D, c: Point3D) -> float:
    """Return angle ABC in degrees."""
    ab = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    cb = (c[0] - b[0], c[1] - b[1], c[2] - b[2])

    dot = (ab[0] * cb[0]) + (ab[1] * cb[1]) + (ab[2] * cb[2])
    ab_norm = math.sqrt((ab[0] * ab[0]) + (ab[1] * ab[1]) + (ab[2] * ab[2]))
    cb_norm = math.sqrt((cb[0] * cb[0]) + (cb[1] * cb[1]) + (cb[2] * cb[2]))

    if ab_norm == 0.0 or cb_norm == 0.0:
        return 0.0

    cos_angle = dot / (ab_norm * cb_norm)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    return math.degrees(math.acos(cos_angle))
