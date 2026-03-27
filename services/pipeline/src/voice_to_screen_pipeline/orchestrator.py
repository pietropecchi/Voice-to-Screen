from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import sys

from .audio.devices import list_input_devices
from .audio.source import AudioSource, AudioSourceConfig
from .contracts import CaptionSegment, SegmentStatus, SessionConfig
from .events import PipelineEvent
from .translation.argos_engine import ArgosTranslationEngine
from .transcription.vosk_engine import VoskTranscriptionEngine


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
                sample_rate=16000,
                channels=1,
            )
        )

        audio_source.start()
        if audio_source.last_error:
            yield PipelineEvent(
                event_type="error",
                payload={
                    "message": f"Unable to open input device: {audio_source.last_error}",
                },
            )
            yield PipelineEvent(event_type="session_stopped")
            return

        transcription = VoskTranscriptionEngine(
            source_language=self.config.source_language,
            model_tier=self.config.model_tier,
            sample_rate=audio_source.active_sample_rate,
            models_root=self._models_root(),
        )
        transcription.start()
        if transcription.last_error:
            yield PipelineEvent(
                event_type="error",
                payload={"message": transcription.last_error},
            )
            audio_source.stop()
            yield PipelineEvent(event_type="session_stopped")
            return

        translation = ArgosTranslationEngine(
            source_language=self.config.source_language,
            target_language=self.config.target_language,
        )
        translation.start()
        if translation.last_error:
            print(translation.last_error, file=sys.stderr)

        for packet in audio_source.iter_packets():
            yield PipelineEvent(
                event_type="audio_level",
                payload={"level": round(packet.level, 4)},
            )
            if not packet.pcm_bytes:
                continue

            update = transcription.process_chunk(packet.pcm_bytes)
            if update is None:
                continue

            translated_text = ""
            if update.is_final:
                translated_text = translation.translate_text(update.text)

            yield PipelineEvent(
                event_type="caption_segment",
                payload=CaptionSegment(
                    segment_id=update.segment_id,
                    speaker_label="Speaker 1",
                    source_text=update.text,
                    translated_text=translated_text,
                    status=SegmentStatus.FINAL if update.is_final else SegmentStatus.DRAFT,
                ).to_dict(),
            )

    @staticmethod
    def _models_root() -> Path:
        return Path(__file__).resolve().parents[4] / "models"

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
