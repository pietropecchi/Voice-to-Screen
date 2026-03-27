from __future__ import annotations

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizeGrip,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .models import CaptionSegment, SegmentStatus
from .session_controller import SessionController


class OverlayWindow(QWidget):
    def __init__(self, controller: SessionController) -> None:
        super().__init__()
        self.controller = controller
        self._drag_origin: QPoint | None = None
        self._always_on_top_timer = QTimer(self)
        self._always_on_top_timer.setInterval(1500)
        self._always_on_top_timer.timeout.connect(self._reassert_on_top)

        self._build_window()
        self._build_ui()
        self._bind()
        self.status_label.setText(self.controller.status_text)
        self._render_captions(self.controller.captions)

    def _build_window(self) -> None:
        self.setWindowTitle("Voice-to-Screen Overlay")
        self.setMinimumSize(540, 220)
        self.resize(900, 320)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setWindowOpacity(self.controller.config.overlay_opacity)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        self.panel = QFrame()
        self.panel.setObjectName("overlayPanel")
        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.feed_widget = QWidget()
        self.feed_layout = QVBoxLayout(self.feed_widget)
        self.feed_layout.setSpacing(12)
        self.feed_layout.addStretch(1)
        self.scroll_area.setWidget(self.feed_widget)
        layout.addWidget(self.scroll_area, 1)

        footer = QVBoxLayout()
        self.status_label = QLabel("Overlay ready")
        self.status_label.setObjectName("overlayStatus")
        footer.addWidget(self.status_label)
        self.size_grip = QSizeGrip(self.panel)
        footer.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(footer)

        root.addWidget(self.panel)
        self.setStyleSheet(_overlay_stylesheet())

    def _bind(self) -> None:
        self.controller.captions_changed.connect(self._render_captions)
        self.controller.status_changed.connect(self.status_label.setText)
        self.controller.config_changed.connect(self._apply_config)

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._reassert_on_top()
        self._always_on_top_timer.start()
        super().showEvent(event)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._always_on_top_timer.stop()
        super().closeEvent(event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._drag_origin = None
        super().mouseReleaseEvent(event)

    def _render_captions(self, captions: list[CaptionSegment]) -> None:
        while self.feed_layout.count() > 1:
            item = self.feed_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for caption in captions:
            self.feed_layout.insertWidget(self.feed_layout.count() - 1, self._build_card(caption))

    def _build_card(self, caption: CaptionSegment) -> QWidget:
        config = self.controller.config
        card = QFrame()
        card.setObjectName("captionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        primary_text = caption.translated_text or caption.source_text
        primary = QLabel(primary_text)
        primary.setWordWrap(True)
        primary.setObjectName("primaryText")
        primary.setFont(QFont("Helvetica Neue", config.primary_font_size, QFont.Weight.DemiBold))
        primary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        primary.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addWidget(primary)

        if not config.compact_mode and caption.source_text:
            source = QLabel(caption.source_text)
            source.setWordWrap(True)
            source.setObjectName("secondaryText")
            source.setFont(QFont("Helvetica Neue", config.source_font_size, QFont.Weight.Medium))
            source.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            source.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            layout.addWidget(source)

        if config.speaker_labels_enabled:
            speaker = QLabel(f"{caption.speaker_label} · {caption.status.value.upper()}")
            speaker.setObjectName("metaText")
            speaker.setStyleSheet(f"color: {status_color(caption.status).name()};")
            layout.addWidget(speaker)
        return card

    def _apply_config(self, config) -> None:
        self.setWindowOpacity(config.overlay_opacity)
        self._render_captions(self.controller.captions)

    def _reassert_on_top(self) -> None:
        self.raise_()


def status_color(status: SegmentStatus) -> QColor:
    if status == SegmentStatus.DRAFT:
        return QColor("#f0c75e")
    if status == SegmentStatus.REVISED:
        return QColor("#ff9757")
    return QColor("#6be28c")


def _overlay_stylesheet() -> str:
    return """
    QWidget {
        color: #f5f7fb;
        font-family: "Helvetica Neue";
        font-size: 13px;
    }
    #overlayPanel {
        background: rgba(18, 22, 29, 215);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
    }
    #captionCard {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 18px;
    }
    #primaryText {
        font-weight: 700;
    }
    #secondaryText {
        color: rgba(245, 247, 251, 0.72);
    }
    #metaText, #overlayStatus {
        color: rgba(245, 247, 251, 0.62);
    }
    """
