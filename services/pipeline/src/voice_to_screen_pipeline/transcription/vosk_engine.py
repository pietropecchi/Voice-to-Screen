from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

try:
    from vosk import KaldiRecognizer, Model
except Exception:  # pragma: no cover
    KaldiRecognizer = None
    Model = None

from ..models import resolve_model_path


@dataclass(slots=True)
class TranscriptUpdate:
    segment_id: str
    text: str
    is_final: bool


class VoskTranscriptionEngine:
    def __init__(self, source_language: str, model_tier: str, sample_rate: int, models_root: Path) -> None:
        self.source_language = source_language
        self.model_tier = model_tier
        self.sample_rate = sample_rate
        self.models_root = models_root
        self._recognizer: KaldiRecognizer | None = None
        self.last_error: str | None = None

    def start(self) -> None:
        self.last_error = None
        if Model is None or KaldiRecognizer is None:
            self.last_error = "Vosk is not installed"
            return

        model_path, options = resolve_model_path(
            models_root=self.models_root,
            language=self.source_language,
            tier=self.model_tier,
        )
        if not options:
            self.last_error = f"No local Vosk model configured for '{self.source_language}'"
            return

        if model_path is None:
            installed_tiers = [option.label for option in options if option.installed]
            if installed_tiers:
                self.last_error = (
                    f"Requested {self.model_tier} model is not installed for {self.source_language}. "
                    f"Available: {', '.join(installed_tiers)}"
                )
            else:
                self.last_error = f"No installed local Vosk models found for {self.source_language}"
            return

        model = Model(str(model_path))
        recognizer = KaldiRecognizer(model, float(self.sample_rate))
        recognizer.SetWords(True)
        recognizer.SetPartialWords(True)
        self._recognizer = recognizer

    def process_chunk(self, pcm_bytes: bytes) -> TranscriptUpdate | None:
        if self._recognizer is None:
            return None

        if self._recognizer.AcceptWaveform(pcm_bytes):
            payload = json.loads(self._recognizer.Result())
            text = str(payload.get("text", "")).strip()
            if text:
                return TranscriptUpdate(
                    segment_id="live-final",
                    text=text,
                    is_final=True,
                )
            return None

        payload = json.loads(self._recognizer.PartialResult())
        text = str(payload.get("partial", "")).strip()
        if not text:
            return None
        return TranscriptUpdate(
            segment_id="live-partial",
            text=text,
            is_final=False,
        )
