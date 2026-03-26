from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class SegmentStatus(StrEnum):
    DRAFT = "draft"
    REVISED = "revised"
    FINAL = "final"


@dataclass(slots=True)
class SessionConfig:
    source_language: str
    target_language: str = "en"
    model_tier: str = "balanced"
    compact_mode: bool = False
    speaker_labels_enabled: bool = True
    gender_hints_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CaptionSegment:
    segment_id: str
    speaker_label: str
    source_text: str
    translated_text: str
    status: SegmentStatus

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload
