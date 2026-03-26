from __future__ import annotations

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QSizeGrip,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .models import CaptionSegment, InputDevice, ModelOption, SegmentStatus, SessionConfig
from .pipeline_client import PipelineClient


class OverlayWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._drag_origin: QPoint | None = None
        self._config = SessionConfig()
        self._pipeline = PipelineClient(self)
        self._devices: list[InputDevice] = []
        self._models: list[ModelOption] = []
        self._audio_level = 0.0
        self._always_on_top_timer = QTimer(self)
        self._always_on_top_timer.setInterval(1500)
        self._always_on_top_timer.timeout.connect(self._reassert_on_top)

        self._build_window()
        self._build_ui()
        self._bind_events()
        self._load_devices()
        self._load_models()

    def _build_window(self) -> None:
        self.setWindowTitle("Voice-to-Screen")
        self.setMinimumSize(680, 380)
        self.resize(860, 520)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowOpacity(self._config.overlay_opacity)

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)

        self.panel = QFrame()
        self.panel.setObjectName("panel")
        self.panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        title_wrap = QVBoxLayout()
        title = QLabel("Voice-to-Screen")
        title.setObjectName("title")
        subtitle = QLabel("Local live translation overlay")
        subtitle.setObjectName("subtitle")
        title_wrap.addWidget(title)
        title_wrap.addWidget(subtitle)
        header_layout.addLayout(title_wrap)
        header_layout.addStretch(1)

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startButton")
        header_layout.addWidget(self.start_button)
        panel_layout.addLayout(header_layout)

        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)

        row_one = QHBoxLayout()
        self.device_combo = QComboBox()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Italian", "Chinese", "Japanese"])
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(160)
        row_one.addWidget(_labeled_widget("Audio device", self.device_combo))
        row_one.addWidget(_labeled_widget("Input", self.language_combo))
        row_one.addWidget(_labeled_widget("Model size", self.model_combo))
        controls_layout.addLayout(row_one)

        row_two = QHBoxLayout()
        self.compact_toggle = QCheckBox("Compact mode")
        self.speakers_toggle = QCheckBox("Speaker labels")
        self.speakers_toggle.setChecked(True)
        self.gender_toggle = QCheckBox("Experimental gender hints")
        row_two.addWidget(self.compact_toggle)
        row_two.addWidget(self.speakers_toggle)
        row_two.addWidget(self.gender_toggle)
        row_two.addStretch(1)
        controls_layout.addLayout(row_two)

        row_three = QHBoxLayout()
        row_three.addWidget(QLabel("Opacity"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(35, 95)
        self.opacity_slider.setValue(int(self._config.overlay_opacity * 100))
        row_three.addWidget(self.opacity_slider)
        self.refresh_devices_button = QPushButton("Refresh devices")
        self.refresh_devices_button.setObjectName("secondaryButton")
        row_three.addWidget(self.refresh_devices_button)
        controls_layout.addLayout(row_three)

        row_four = QHBoxLayout()
        row_four.addWidget(QLabel("Source text"))
        self.source_font_slider = QSlider(Qt.Orientation.Horizontal)
        self.source_font_slider.setRange(11, 28)
        self.source_font_slider.setValue(self._config.source_font_size)
        row_four.addWidget(self.source_font_slider)
        row_four.addWidget(QLabel("Primary text"))
        self.primary_font_slider = QSlider(Qt.Orientation.Horizontal)
        self.primary_font_slider.setRange(14, 40)
        self.primary_font_slider.setValue(self._config.primary_font_size)
        row_four.addWidget(self.primary_font_slider)
        controls_layout.addLayout(row_four)

        panel_layout.addLayout(controls_layout)

        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("statusLabel")
        panel_layout.addWidget(self.status_label)

        meter_row = QHBoxLayout()
        meter_label = QLabel("Input level")
        meter_label.setObjectName("fieldLabel")
        self.audio_meter = QProgressBar()
        self.audio_meter.setRange(0, 100)
        self.audio_meter.setValue(0)
        self.audio_meter.setTextVisible(False)
        self.audio_meter.setObjectName("audioMeter")
        meter_row.addWidget(meter_label)
        meter_row.addWidget(self.audio_meter, 1)
        panel_layout.addLayout(meter_row)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.feed_widget = QWidget()
        self.feed_layout = QVBoxLayout(self.feed_widget)
        self.feed_layout.setSpacing(12)
        self.feed_layout.addStretch(1)

        self.scroll_area.setWidget(self.feed_widget)
        panel_layout.addWidget(self.scroll_area, 1)

        footer_row = QHBoxLayout()
        footer_row.addStretch(1)
        self.resize_hint = QLabel("Resize")
        self.resize_hint.setObjectName("fieldLabel")
        footer_row.addWidget(self.resize_hint)
        self.size_grip = QSizeGrip(self.panel)
        self.size_grip.setFixedSize(18, 18)
        footer_row.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignBottom)
        panel_layout.addLayout(footer_row)

        root_layout.addWidget(self.panel)
        self.setStyleSheet(_stylesheet())

    def _bind_events(self) -> None:
        self.start_button.clicked.connect(self._toggle_session)
        self.opacity_slider.valueChanged.connect(self._set_opacity)
        self.source_font_slider.valueChanged.connect(self._set_source_font_size)
        self.primary_font_slider.valueChanged.connect(self._set_primary_font_size)
        self.compact_toggle.toggled.connect(self._update_config)
        self.speakers_toggle.toggled.connect(self._update_config)
        self.gender_toggle.toggled.connect(self._update_config)
        self.device_combo.currentIndexChanged.connect(self._update_config)
        self.language_combo.currentTextChanged.connect(self._update_config)
        self.language_combo.currentTextChanged.connect(self._load_models)
        self.model_combo.currentTextChanged.connect(self._update_config)
        self.refresh_devices_button.clicked.connect(self._load_devices)

        self._pipeline.session_started.connect(self._handle_session_started)
        self._pipeline.session_stopped.connect(self._handle_session_stopped)
        self._pipeline.captions_updated.connect(self._render_captions)
        self._pipeline.audio_level_updated.connect(self._handle_audio_level)
        self._pipeline.process_error.connect(self._handle_process_error)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._reassert_on_top()
        self._always_on_top_timer.start()
        super().showEvent(event)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._always_on_top_timer.stop()
        if self._pipeline.is_running():
            self._pipeline.stop_session()
        super().closeEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._drag_origin = None
        super().mouseReleaseEvent(event)

    def _toggle_session(self) -> None:
        if self.start_button.text() == "Start":
            self._update_config()
            self._pipeline.start_session(self._config)
        else:
            self._pipeline.stop_session()

    def _set_opacity(self, value: int) -> None:
        self._config.overlay_opacity = value / 100
        self.setWindowOpacity(self._config.overlay_opacity)

    def _set_source_font_size(self, value: int) -> None:
        self._config.source_font_size = value
        self._rerender_existing_cards()

    def _set_primary_font_size(self, value: int) -> None:
        self._config.primary_font_size = value
        self._rerender_existing_cards()

    def _update_config(self) -> None:
        selected_device = self.device_combo.currentData()
        self._config.input_device_id = str(selected_device) if selected_device is not None else ""
        self._config.source_language = self.language_combo.currentText().lower()
        selected_tier = self.model_combo.currentData()
        self._config.model_tier = str(selected_tier) if selected_tier is not None else ""
        self._config.compact_mode = self.compact_toggle.isChecked()
        self._config.speaker_labels_enabled = self.speakers_toggle.isChecked()
        self._config.gender_hints_enabled = self.gender_toggle.isChecked()
        self._rerender_existing_cards()

    def _handle_session_started(self, payload: dict) -> None:
        selected_device = payload.get("selected_input_device")
        if isinstance(selected_device, dict):
            device_name = selected_device.get("name", "Unknown device")
            self.status_label.setText(f"Session running on {device_name}")
        else:
            self.status_label.setText("Session running")
        self.start_button.setText("Stop")

    def _handle_session_stopped(self) -> None:
        self.status_label.setText("Idle")
        self.start_button.setText("Start")
        self.audio_meter.setValue(0)

    def _handle_process_error(self, message: str) -> None:
        self.status_label.setText(f"Pipeline error: {message}")
        self.start_button.setText("Start")
        self.audio_meter.setValue(0)

    def _handle_audio_level(self, level: float) -> None:
        self._audio_level = level
        self.audio_meter.setValue(int(level * 100))

    def _load_devices(self) -> None:
        try:
            devices = self._pipeline.list_devices()
        except Exception as exc:
            self.status_label.setText(f"Device discovery failed: {exc}")
            return

        self._devices = devices
        self.device_combo.blockSignals(True)
        self.device_combo.clear()

        for device in devices:
            label = f"{device.name} · {device.max_input_channels}ch · {device.default_samplerate}Hz"
            if device.is_default:
                label = f"{label} · default"
            self.device_combo.addItem(label, device.device_id)

        self.device_combo.blockSignals(False)
        self._update_config()
        if devices:
            self.status_label.setText(f"Ready · {len(devices)} input device(s) detected")

    def _load_models(self) -> None:
        language = self.language_combo.currentText().lower()
        try:
            models = self._pipeline.list_models(language)
        except Exception as exc:
            self.status_label.setText(f"Model discovery failed: {exc}")
            return

        self._models = models
        installed = [model for model in models if model.installed]

        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        for model in installed:
            self.model_combo.addItem(model.label, model.tier)
        self.model_combo.blockSignals(False)

        if installed:
            self._config.model_tier = installed[0].tier
            self.status_label.setText(
                f"Ready · {len(self._devices)} input device(s) · {len(installed)} model size(s)"
            )
        else:
            self._config.model_tier = ""
            self.status_label.setText(f"No installed model sizes found for {language}")

    def _render_captions(self, captions: list[CaptionSegment]) -> None:
        while self.feed_layout.count() > 1:
            item = self.feed_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for caption in captions:
            self.feed_layout.insertWidget(self.feed_layout.count() - 1, self._build_card(caption))

    def _rerender_existing_cards(self) -> None:
        cards = list(self._pipeline._segments_by_id.values())
        if cards:
            self._render_captions(cards)

    def _build_card(self, caption: CaptionSegment) -> QWidget:
        card = QFrame()
        card.setObjectName("captionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        if self._config.speaker_labels_enabled:
            speaker = QLabel(caption.speaker_label)
            speaker.setObjectName("speakerLabel")
            layout.addWidget(speaker)

        if not self._config.compact_mode:
            source = QLabel(caption.source_text)
            source.setWordWrap(True)
            source.setObjectName("sourceText")
            source.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            source.setFont(QFont("Helvetica Neue", self._config.source_font_size, QFont.Weight.Medium))
            source.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            layout.addWidget(source)

        primary_text = caption.translated_text or caption.source_text
        translation = QLabel(primary_text)
        translation.setWordWrap(True)
        translation.setObjectName("translationText")
        translation.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        translation.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        translation.setFont(QFont("Helvetica Neue", self._config.primary_font_size, QFont.Weight.Medium))
        layout.addWidget(translation)

        status = QLabel(caption.status.value.upper())
        status.setObjectName("statusText")
        status.setStyleSheet(f"color: {status_color(caption.status).name()};")
        layout.addWidget(status)
        return card

    def _reassert_on_top(self) -> None:
        self.raise_()
        self.activateWindow()


def _labeled_widget(label_text: str, widget: QWidget) -> QWidget:
    wrap = QWidget()
    layout = QVBoxLayout(wrap)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)
    label = QLabel(label_text)
    label.setObjectName("fieldLabel")
    layout.addWidget(label)
    layout.addWidget(widget)
    return wrap


def status_color(status: SegmentStatus) -> QColor:
    if status == SegmentStatus.DRAFT:
        return QColor("#f0c75e")
    if status == SegmentStatus.REVISED:
        return QColor("#ff9757")
    return QColor("#6be28c")


def _stylesheet() -> str:
    return """
    QWidget {
        color: #f5f7fb;
        font-family: "Helvetica Neue";
        font-size: 13px;
    }
    #panel {
        background: rgba(18, 22, 29, 215);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
    }
    #title {
        font-size: 26px;
        font-weight: 700;
    }
    #subtitle {
        color: rgba(245, 247, 251, 0.68);
    }
    #captionCard {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 18px;
    }
    #speakerLabel, #fieldLabel, #statusLabel {
        color: rgba(245, 247, 251, 0.7);
    }
    #sourceText {
        color: rgba(245, 247, 251, 0.85);
    }
    #translationText {
        font-weight: 600;
    }
    #statusText {
        font-family: Menlo, monospace;
        font-size: 11px;
        letter-spacing: 1px;
    }
    QProgressBar#audioMeter {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        min-height: 12px;
    }
    QProgressBar#audioMeter::chunk {
        background: #e56b3c;
        border-radius: 7px;
    }
    QPushButton#startButton {
        background: #e56b3c;
        border: none;
        border-radius: 12px;
        padding: 10px 16px;
        font-weight: 700;
    }
    QPushButton#startButton:hover {
        background: #f47a4b;
    }
    QPushButton#secondaryButton {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 8px 12px;
    }
    QPushButton#secondaryButton:hover {
        background: rgba(255, 255, 255, 0.12);
    }
    QComboBox, QSlider, QCheckBox {
        margin-top: 2px;
    }
    """
