from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .session_controller import SessionController


class ControlWindow(QWidget):
    def __init__(self, controller: SessionController) -> None:
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Voice-to-Screen Settings")
        self.resize(720, 360)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        title = QLabel("Voice-to-Screen")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QLabel("Session setup and live subtitle controls")
        subtitle.setStyleSheet("color: rgba(20,20,20,0.6);")
        root.addWidget(title)
        root.addWidget(subtitle)

        row_one = QHBoxLayout()
        self.device_combo = QComboBox()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Italian", "Chinese", "Japanese"])
        self.model_combo = QComboBox()
        row_one.addWidget(_labeled_widget("Audio device", self.device_combo))
        row_one.addWidget(_labeled_widget("Input", self.language_combo))
        row_one.addWidget(_labeled_widget("Model size", self.model_combo))
        root.addLayout(row_one)

        row_two = QHBoxLayout()
        self.compact_toggle = QCheckBox("Compact overlay")
        self.speakers_toggle = QCheckBox("Speaker labels")
        self.speakers_toggle.setChecked(True)
        self.gender_toggle = QCheckBox("Experimental gender hints")
        row_two.addWidget(self.compact_toggle)
        row_two.addWidget(self.speakers_toggle)
        row_two.addWidget(self.gender_toggle)
        row_two.addStretch(1)
        root.addLayout(row_two)

        row_three = QHBoxLayout()
        row_three.addWidget(QLabel("Overlay opacity"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(35, 95)
        self.opacity_slider.setValue(int(self.controller.config.overlay_opacity * 100))
        row_three.addWidget(self.opacity_slider)
        self.refresh_devices_button = QPushButton("Refresh devices")
        row_three.addWidget(self.refresh_devices_button)
        root.addLayout(row_three)

        row_four = QHBoxLayout()
        row_four.addWidget(QLabel("Source text"))
        self.source_font_slider = QSlider(Qt.Orientation.Horizontal)
        self.source_font_slider.setRange(11, 28)
        self.source_font_slider.setValue(self.controller.config.source_font_size)
        row_four.addWidget(self.source_font_slider)
        row_four.addWidget(QLabel("Primary text"))
        self.primary_font_slider = QSlider(Qt.Orientation.Horizontal)
        self.primary_font_slider.setRange(14, 40)
        self.primary_font_slider.setValue(self.controller.config.primary_font_size)
        row_four.addWidget(self.primary_font_slider)
        root.addLayout(row_four)

        meter_row = QHBoxLayout()
        meter_row.addWidget(QLabel("Input level"))
        self.audio_meter = QProgressBar()
        self.audio_meter.setRange(0, 100)
        self.audio_meter.setValue(0)
        self.audio_meter.setTextVisible(False)
        meter_row.addWidget(self.audio_meter, 1)
        root.addLayout(meter_row)

        action_row = QHBoxLayout()
        self.toggle_button = QPushButton("Start")
        self.toggle_button.setStyleSheet(
            "background: #e56b3c; color: white; border: none; border-radius: 10px; padding: 10px 16px; font-weight: 700;"
        )
        action_row.addStretch(1)
        action_row.addWidget(self.toggle_button)
        root.addLayout(action_row)

        self._bind()
        self._sync_from_controller()
        self._update_devices(self.controller.devices)
        self._update_models(self.controller.models)
        self.audio_meter.setValue(int(self.controller.audio_level * 100))
        self._update_running_state(self.controller.is_running)

    def _bind(self) -> None:
        self.toggle_button.clicked.connect(self.controller.toggle_session)
        self.refresh_devices_button.clicked.connect(self.controller.load_devices)
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        self.language_combo.currentTextChanged.connect(lambda text: self.controller.set_source_language(text.lower()))
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.compact_toggle.toggled.connect(self.controller.set_compact_mode)
        self.speakers_toggle.toggled.connect(self.controller.set_speaker_labels_enabled)
        self.gender_toggle.toggled.connect(self.controller.set_gender_hints_enabled)
        self.opacity_slider.valueChanged.connect(lambda value: self.controller.set_overlay_opacity(value / 100))
        self.source_font_slider.valueChanged.connect(self.controller.set_source_font_size)
        self.primary_font_slider.valueChanged.connect(self.controller.set_primary_font_size)

        self.controller.devices_changed.connect(self._update_devices)
        self.controller.models_changed.connect(self._update_models)
        self.controller.audio_level_changed.connect(lambda level: self.audio_meter.setValue(int(level * 100)))
        self.controller.running_changed.connect(self._update_running_state)
        self.controller.config_changed.connect(lambda _: self._sync_from_controller())

    def _sync_from_controller(self) -> None:
        config = self.controller.config
        self.device_combo.blockSignals(True)
        if self.device_combo.count():
            index = self.device_combo.findData(config.input_device_id)
            if index >= 0:
                self.device_combo.setCurrentIndex(index)
        self.device_combo.blockSignals(False)

        self.language_combo.blockSignals(True)
        self.language_combo.setCurrentText(config.source_language.capitalize())
        self.language_combo.blockSignals(False)

        self.model_combo.blockSignals(True)
        if self.model_combo.count():
            index = self.model_combo.findData(config.model_tier)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
        self.model_combo.blockSignals(False)

        self.compact_toggle.blockSignals(True)
        self.compact_toggle.setChecked(config.compact_mode)
        self.compact_toggle.blockSignals(False)

        self.speakers_toggle.blockSignals(True)
        self.speakers_toggle.setChecked(config.speaker_labels_enabled)
        self.speakers_toggle.blockSignals(False)

        self.gender_toggle.blockSignals(True)
        self.gender_toggle.setChecked(config.gender_hints_enabled)
        self.gender_toggle.blockSignals(False)

        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(int(config.overlay_opacity * 100))
        self.opacity_slider.blockSignals(False)

        self.source_font_slider.blockSignals(True)
        self.source_font_slider.setValue(config.source_font_size)
        self.source_font_slider.blockSignals(False)

        self.primary_font_slider.blockSignals(True)
        self.primary_font_slider.setValue(config.primary_font_size)
        self.primary_font_slider.blockSignals(False)

    def _update_devices(self, devices: list) -> None:
        self.device_combo.blockSignals(True)
        self.device_combo.clear()
        for device in devices:
            label = f"{device.name} · {device.max_input_channels}ch · {device.default_samplerate}Hz"
            self.device_combo.addItem(label, device.device_id)
        current_id = self.controller.config.input_device_id
        index = max(0, self.device_combo.findData(current_id))
        self.device_combo.setCurrentIndex(index)
        self.device_combo.blockSignals(False)

    def _update_models(self, models: list) -> None:
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        for model in [model for model in models if model.installed]:
            self.model_combo.addItem(model.label, model.tier)
        current_tier = self.controller.config.model_tier
        index = max(0, self.model_combo.findData(current_tier))
        if self.model_combo.count():
            self.model_combo.setCurrentIndex(index)
        self.model_combo.blockSignals(False)

    def _update_running_state(self, running: bool) -> None:
        self.toggle_button.setText("Stop" if running else "Start")

    def _on_device_changed(self) -> None:
        device_id = self.device_combo.currentData()
        if device_id is not None:
            self.controller.set_input_device(str(device_id))

    def _on_model_changed(self) -> None:
        tier = self.model_combo.currentData()
        if tier is not None:
            self.controller.set_model_tier(str(tier))


def _labeled_widget(label_text: str, widget: QWidget) -> QWidget:
    wrap = QWidget()
    layout = QVBoxLayout(wrap)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    label = QLabel(label_text)
    layout.addWidget(label)
    layout.addWidget(widget)
    return wrap
