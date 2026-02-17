"""OSC output helper for REAPER parameter control."""

from __future__ import annotations

from pythonosc.udp_client import SimpleUDPClient

from .mapping import SoundControls


class OscOut:
    def __init__(self, host: str = "127.0.0.1", port: int = 9000) -> None:
        self._client = SimpleUDPClient(host, port)

    def send_controls(self, controls: SoundControls) -> None:
        self._client.send_message("/arm/cutoff", controls.cutoff)
        self._client.send_message("/arm/resonance", controls.resonance)
        self._client.send_message("/arm/texture_drive", controls.texture_drive)
