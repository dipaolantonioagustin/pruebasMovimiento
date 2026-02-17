"""Webcam + MediaPipe pose capture focused on right arm landmarks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import mediapipe as mp

Point3D = Tuple[float, float, float]


@dataclass(slots=True)
class ArmLandmarks:
    shoulder: Point3D
    elbow: Point3D
    wrist: Point3D


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
        shoulder = self._landmark_to_point(landmarks[self._mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
        elbow = self._landmark_to_point(landmarks[self._mp_pose.PoseLandmark.RIGHT_ELBOW.value])
        wrist = self._landmark_to_point(landmarks[self._mp_pose.PoseLandmark.RIGHT_WRIST.value])

        return ArmLandmarks(shoulder=shoulder, elbow=elbow, wrist=wrist)

    def release(self) -> None:
        self._pose.close()
        self._camera.release()

    @staticmethod
    def _landmark_to_point(landmark: mp.framework.formats.landmark_pb2.NormalizedLandmark) -> Point3D:
        return (landmark.x, landmark.y, landmark.z)
