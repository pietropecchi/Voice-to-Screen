from __future__ import annotations

from collections.abc import Iterator

from .audio.devices import list_input_devices
from .audio.source import AudioSource, AudioSourceConfig
from .contracts import SessionConfig
from .events import PipelineEvent


class PipelineOrchestrator:
    """Contract-first stub for the local speech pipeline."""

    def __init__(self, config: SessionConfig) -> None:
        self.config = config

    def start(self) -> Iterator[PipelineEvent]:
        selected_device = self._resolve_selected_device()
        yield PipelineEvent(
            event_type="session_started",
            payload={
                "config": self.config.to_dict(),
                "selected_input_device": selected_device,
            },
        )

        if selected_device is None:
            yield PipelineEvent(
                event_type="error",
                payload={"message": "No input device selected"},
            )
            yield PipelineEvent(event_type="session_stopped")
            return

        audio_source = AudioSource(
            AudioSourceConfig(
                device_id=str(selected_device["device_id"]),
                sample_rate=int(selected_device.get("default_samplerate", 16000)),
                channels=1,
            )
        )

        audio_source.start()
        for level in audio_source.iter_levels():
            yield PipelineEvent(
                event_type="audio_level",
                payload={"level": round(level, 4)},
            )
        audio_source.stop()

    def _resolve_selected_device(self) -> dict[str, object] | None:
        if not self.config.input_device_id:
            return None

        for device in list_input_devices():
            if device.device_id == self.config.input_device_id:
                return device.to_dict()

        return {
            "device_id": self.config.input_device_id,
            "name": "Unknown device",
        }
