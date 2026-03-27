from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .control_window import ControlWindow
from .overlay_window import OverlayWindow
from .session_controller import SessionController


def main() -> int:
    app = QApplication(sys.argv)
    controller = SessionController()

    control_window = ControlWindow(controller)
    overlay_window = OverlayWindow(controller)
    controller.initialize()
    app.aboutToQuit.connect(controller.shutdown)

    control_window.show()
    overlay_window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
