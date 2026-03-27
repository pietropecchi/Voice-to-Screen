from __future__ import annotations

import sys

from PySide6.QtCore import QObject, Signal

from .models import CaptionSegment, InputDevice, ModelOption, SessionConfig
from .pipeline_client import PipelineClient


class SessionController(QObject):
    captions_changed = Signal(list)
    audio_level_changed = Signal(float)
    status_changed = Signal(str)
    running_changed = Signal(bool)
    devices_changed = Signal(list)
    models_changed = Signal(list)
    config_changed = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.config = SessionConfig()
        self.pipeline = PipelineClient(self)
        self.devices: list[InputDevice] = []
        self.models: list[ModelOption] = []
        self.captions: list[CaptionSegment] = []
        self.audio_level = 0.0
        self.is_running = False
        self.status_text = "Idle"

        self.pipeline.session_started.connect(self._handle_session_started)
        self.pipeline.session_stopped.connect(self._handle_session_stopped)
        self.pipeline.captions_updated.connect(self._handle_captions_updated)
        self.pipeline.audio_level_updated.connect(self._handle_audio_level)
        self.pipeline.process_error.connect(self._handle_process_error)

    def initialize(self) -> None:
        self.load_devices()
        self.load_models()

    def toggle_session(self) -> None:
        if self.is_running:
            self.pipeline.stop_session()
            return

        self.pipeline.start_session(self.config)

    def shutdown(self) -> None:
        if self.pipeline.is_running():
            self.pipeline.stop_session()

    def load_devices(self) -> None:
        try:
            self.devices = self.pipeline.list_devices()
            if self.devices and not self.config.input_device_id:
                self.config.input_device_id = self.devices[0].device_id
            self.devices_changed.emit(self.devices)
            self._set_status(f"Ready · {len(self.devices)} input device(s) detected")
            self.config_changed.emit(self.config)
        except Exception as exc:
            self._set_status(f"Device discovery failed: {exc}")

    def load_models(self) -> None:
        language = self.config.source_language
        try:
            self.models = self.pipeline.list_models(language)
            installed = [model for model in self.models if model.installed]
            if installed and self.config.model_tier not in {model.tier for model in installed}:
                self.config.model_tier = installed[0].tier
            if not installed:
                self.config.model_tier = ""
                self._set_status(f"No installed model sizes found for {language}")
            self.models_changed.emit(self.models)
            self.config_changed.emit(self.config)
        except Exception as exc:
            self._set_status(f"Model discovery failed: {exc}")

    def set_input_device(self, device_id: str) -> None:
        self.config.input_device_id = device_id
        self.config_changed.emit(self.config)

    def set_source_language(self, language: str) -> None:
        self.config.source_language = language
        self.config_changed.emit(self.config)
        self.load_models()

    def set_model_tier(self, tier: str) -> None:
        self.config.model_tier = tier
        self.config_changed.emit(self.config)

    def set_overlay_opacity(self, opacity: float) -> None:
        self.config.overlay_opacity = opacity
        self.config_changed.emit(self.config)

    def set_source_font_size(self, size: int) -> None:
        self.config.source_font_size = size
        self.config_changed.emit(self.config)
        self.captions_changed.emit(self.captions)

    def set_primary_font_size(self, size: int) -> None:
        self.config.primary_font_size = size
        self.config_changed.emit(self.config)
        self.captions_changed.emit(self.captions)

    def set_compact_mode(self, enabled: bool) -> None:
        self.config.compact_mode = enabled
        self.config_changed.emit(self.config)
        self.captions_changed.emit(self.captions)

    def set_speaker_labels_enabled(self, enabled: bool) -> None:
        self.config.speaker_labels_enabled = enabled
        self.config_changed.emit(self.config)
        self.captions_changed.emit(self.captions)

    def set_gender_hints_enabled(self, enabled: bool) -> None:
        self.config.gender_hints_enabled = enabled
        self.config_changed.emit(self.config)

    def _handle_session_started(self, payload: dict) -> None:
        self.is_running = True
        selected_device = payload.get("selected_input_device")
        if isinstance(selected_device, dict):
            device_name = selected_device.get("name", "Unknown device")
            self._set_status(f"Session running on {device_name}")
        else:
            self._set_status("Session running")
        self.running_changed.emit(True)

    def _handle_session_stopped(self) -> None:
        self.is_running = False
        self.audio_level = 0.0
        self.audio_level_changed.emit(0.0)
        self._set_status("Idle")
        self.running_changed.emit(False)

    def _handle_captions_updated(self, captions: list[CaptionSegment]) -> None:
        finalized = [caption for caption in captions if caption.status == "final"]
        self.captions = finalized
        self.captions_changed.emit(finalized)

    def _handle_audio_level(self, level: float) -> None:
        self.audio_level = level
        self.audio_level_changed.emit(level)

    def _handle_process_error(self, message: str) -> None:
        self.is_running = False
        self.running_changed.emit(False)
        self._set_status(f"Pipeline error: {message}")

    def _set_status(self, text: str) -> None:
        self.status_text = text
        print(text, file=sys.stderr)
        self.status_changed.emit(text)
