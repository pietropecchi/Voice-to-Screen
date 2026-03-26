from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AudioSourceConfig:
    device_id: str
    sample_rate: int = 16000
    channels: int = 1


class AudioSource:
    """Placeholder capture interface for the next milestone."""

    def __init__(self, config: AudioSourceConfig) -> None:
        self.config = config

    def start(self) -> None:
        """Start ingesting audio from the selected device."""

    def stop(self) -> None:
        """Stop ingesting audio."""
