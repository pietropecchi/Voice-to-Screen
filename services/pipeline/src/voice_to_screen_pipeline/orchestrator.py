from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

from .audio.devices import list_input_devices
from .contracts import CaptionSegment, SegmentStatus, SessionConfig
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

        for segment in self._sample_segments():
            yield PipelineEvent(
                event_type="caption_segment",
                payload=segment.to_dict(),
            )

        yield PipelineEvent(event_type="session_stopped")

    def _sample_segments(self) -> list[CaptionSegment]:
        return [
            CaptionSegment(
                segment_id=str(uuid4()),
                speaker_label="Speaker 1",
                source_text="Kore wa mada tesuto no dankai desu.",
                translated_text="This is still in the testing phase.",
                status=SegmentStatus.DRAFT,
            ),
            CaptionSegment(
                segment_id=str(uuid4()),
                speaker_label="Speaker 2",
                source_text="Demo jikkou wa mou sugu hajimarimasu.",
                translated_text="But execution will begin very soon.",
                status=SegmentStatus.REVISED,
            ),
        ]

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
