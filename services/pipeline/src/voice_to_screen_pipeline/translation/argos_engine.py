from __future__ import annotations

import sys

try:
    from argostranslate import translate
except Exception:  # pragma: no cover
    translate = None


LANGUAGE_CODES = {
    "english": "en",
    "italian": "it",
    "chinese": "zh",
    "japanese": "ja",
}


class ArgosTranslationEngine:
    def __init__(self, source_language: str, target_language: str = "en") -> None:
        self.source_language = source_language
        self.target_language = target_language
        self._translation = None
        self.last_error: str | None = None

    def start(self) -> None:
        self.last_error = None

        source_code = LANGUAGE_CODES.get(self.source_language)
        if source_code is None:
            self.last_error = f"No translation language code configured for '{self.source_language}'"
            return

        if source_code == self.target_language:
            self._translation = "passthrough"
            return

        if translate is None:
            self.last_error = "Argos Translate is not installed"
            return

        installed_languages = translate.get_installed_languages()
        from_lang = next((lang for lang in installed_languages if lang.code == source_code), None)
        to_lang = next((lang for lang in installed_languages if lang.code == self.target_language), None)

        if from_lang is None or to_lang is None:
            self.last_error = (
                f"Missing Argos language package for {source_code}->{self.target_language}. "
                "Translation will stay disabled until the package is installed."
            )
            return

        try:
            self._translation = from_lang.get_translation(to_lang)
        except Exception as exc:
            self.last_error = f"Unable to initialize translation: {exc}"

    def translate_text(self, text: str) -> str:
        if not text:
            return ""

        if self._translation == "passthrough":
            return text

        if self._translation is None:
            return ""

        try:
            return str(self._translation.translate(text)).strip()
        except Exception as exc:
            print(f"Translation warning: {exc}", file=sys.stderr)
            return ""
