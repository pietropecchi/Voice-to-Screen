from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ModelOption:
    language: str
    tier: str
    label: str
    model_dir: str
    installed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "tier": self.tier,
            "label": self.label,
            "model_dir": self.model_dir,
            "installed": self.installed,
        }


CATALOG: dict[str, list[tuple[str, str, str]]] = {
    "english": [
        ("fast", "Fast", "vosk-model-en-us"),
        ("balanced", "Balanced", "vosk-model-en-us-0.22"),
        ("accurate", "Accurate", "vosk-model-en-us-0.42-gigaspeech"),
    ],
    "japanese": [
        ("fast", "Fast", "vosk-model-ja"),
        ("balanced", "Balanced", "vosk-model-ja-0.22"),
        ("accurate", "Accurate", "vosk-model-ja-0.22-lgraph"),
    ],
}


def list_model_options(models_root: Path, language: str | None = None) -> list[ModelOption]:
    languages = [language] if language else list(CATALOG.keys())
    options: list[ModelOption] = []

    for lang in languages:
        for tier, label, model_dir in CATALOG.get(lang, []):
            options.append(
                ModelOption(
                    language=lang,
                    tier=tier,
                    label=label,
                    model_dir=model_dir,
                    installed=(models_root / model_dir).exists(),
                )
            )

    return options


def resolve_model_path(models_root: Path, language: str, tier: str) -> tuple[Path | None, list[ModelOption]]:
    options = list_model_options(models_root=models_root, language=language)
    for option in options:
        if option.tier == tier and option.installed:
            return models_root / option.model_dir, options
    return None, options
