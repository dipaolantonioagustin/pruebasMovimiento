"""Mapping layer from movement features to normalized sound controls."""

from __future__ import annotations

from dataclasses import dataclass

from .features import ArmFeatures


@dataclass(slots=True)
class SoundControls:
    cutoff: float
    resonance: float
    texture_drive: float


class EmaFilter:
    def __init__(self, alpha: float = 0.25):
        self.alpha = alpha
        self._state: float | None = None

    def apply(self, value: float) -> float:
        if self._state is None:
            self._state = value
            return value
        self._state = self.alpha * value + (1.0 - self.alpha) * self._state
        return self._state


class MovementMapper:
    """Map arm features into [0, 1] controls suitable for OSC/MIDI."""

    def __init__(self) -> None:
        self._cutoff_filter = EmaFilter(alpha=0.2)
        self._resonance_filter = EmaFilter(alpha=0.3)
        self._drive_filter = EmaFilter(alpha=0.25)

    def to_sound_controls(self, features: ArmFeatures) -> SoundControls:
        wrist_y = clamp01(1.0 - features.wrist_xyz[1])
        elbow_angle_norm = clamp01(features.elbow_angle_deg / 180.0)
        speed_norm = clamp01(features.wrist_speed * 20.0)

        cutoff = self._cutoff_filter.apply(wrist_y)
        resonance = self._resonance_filter.apply(1.0 - elbow_angle_norm)
        drive = self._drive_filter.apply(speed_norm)

        return SoundControls(cutoff=cutoff, resonance=resonance, texture_drive=drive)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
