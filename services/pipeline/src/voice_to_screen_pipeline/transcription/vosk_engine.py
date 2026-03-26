from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

try:
    from vosk import KaldiRecognizer, Model
except Exception:  # pragma: no cover
    KaldiRecognizer = None
    Model = None


LANGUAGE_MODEL_DIRS = {
    "english": "vosk-model-en-us",
    "japanese": "vosk-model-ja",
}


@dataclass(slots=True)
class TranscriptUpdate:
    segment_id: str
    text: str
    is_final: bool


class VoskTranscriptionEngine:
    def __init__(self, source_language: str, sample_rate: int, models_root: Path) -> None:
        self.source_language = source_language
        self.sample_rate = sample_rate
        self.models_root = models_root
        self._recognizer: KaldiRecognizer | None = None
        self.last_error: str | None = None

    def start(self) -> None:
        self.last_error = None
        if Model is None or KaldiRecognizer is None:
            self.last_error = "Vosk is not installed"
            return

        model_name = LANGUAGE_MODEL_DIRS.get(self.source_language)
        if model_name is None:
            self.last_error = f"No local Vosk model configured for '{self.source_language}'"
            return

        model_path = self.models_root / model_name
        if not model_path.exists():
            self.last_error = f"Missing local Vosk model at {model_path}"
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
