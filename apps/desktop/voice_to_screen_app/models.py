from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SegmentStatus(StrEnum):
    DRAFT = "draft"
    REVISED = "revised"
    FINAL = "final"


@dataclass(slots=True)
class SessionConfig:
    input_device_id: str = ""
    source_language: str = "japanese"
    target_language: str = "English"
    model_tier: str = "balanced"
    overlay_opacity: float = 0.84
    compact_mode: bool = False
    speaker_labels_enabled: bool = True
    gender_hints_enabled: bool = False

    def to_pipeline_dict(self) -> dict[str, object]:
        return {
            "input_device_id": self.input_device_id,
            "source_language": self.source_language,
            "target_language": "en",
            "model_tier": self.model_tier,
            "compact_mode": self.compact_mode,
            "speaker_labels_enabled": self.speaker_labels_enabled,
            "gender_hints_enabled": self.gender_hints_enabled,
        }


@dataclass(slots=True)
class InputDevice:
    device_id: str
    name: str
    max_input_channels: int
    default_samplerate: int
    is_default: bool = False

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "InputDevice":
        return cls(
            device_id=str(payload["device_id"]),
            name=str(payload["name"]),
            max_input_channels=int(payload.get("max_input_channels", 0)),
            default_samplerate=int(payload.get("default_samplerate", 16000)),
            is_default=bool(payload.get("is_default", False)),
        )


@dataclass(slots=True)
class CaptionSegment:
    segment_id: str
    speaker_label: str
    source_text: str
    translated_text: str
    status: SegmentStatus

    @classmethod
    def from_event_payload(cls, payload: dict[str, object]) -> "CaptionSegment":
        return cls(
            segment_id=str(payload["segment_id"]),
            speaker_label=str(payload["speaker_label"]),
            source_text=str(payload["source_text"]),
            translated_text=str(payload["translated_text"]),
            status=SegmentStatus(str(payload["status"])),
        )
