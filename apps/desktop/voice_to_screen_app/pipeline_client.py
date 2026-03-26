from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal

from .models import CaptionSegment, InputDevice, SessionConfig


class PipelineClient(QObject):
    captions_updated = Signal(list)
    audio_level_updated = Signal(float)
    session_started = Signal(dict)
    session_stopped = Signal()
    process_error = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._consume_stdout)
        self._process.readyReadStandardError.connect(self._consume_stderr)
        self._process.finished.connect(self._handle_finished)
        self._segments_by_id: dict[str, CaptionSegment] = {}

    def start_session(self, config: SessionConfig) -> None:
        if self._process.state() != QProcess.ProcessState.NotRunning:
            return

        self._segments_by_id.clear()
        command = [sys.executable, "-m", "voice_to_screen_pipeline.main", json.dumps(config.to_pipeline_dict())]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self._pipeline_src_dir())
        self._process.setProcessEnvironment(self._build_environment(env))
        self._process.setWorkingDirectory(str(self._repo_root()))
        self._process.start(command[0], command[1:])

    def stop_session(self) -> None:
        if self._process.state() == QProcess.ProcessState.NotRunning:
            return
        self._process.kill()
        self._process.waitForFinished(1500)

    def list_devices(self) -> list[InputDevice]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self._pipeline_src_dir())
        command = [sys.executable, "-m", "voice_to_screen_pipeline.main", "list-devices"]
        result = subprocess.run(
            command,
            cwd=self._repo_root(),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            error_message = result.stderr.strip() or "Device discovery failed"
            raise RuntimeError(error_message)

        payload = json.loads(result.stdout)
        return [InputDevice.from_dict(item) for item in payload.get("devices", [])]

    def _consume_stdout(self) -> None:
        while self._process.canReadLine():
            raw_line = bytes(self._process.readLine()).decode("utf-8").strip()
            if not raw_line:
                continue
            self._handle_event(raw_line)

    def _consume_stderr(self) -> None:
        message = bytes(self._process.readAllStandardError()).decode("utf-8").strip()
        if message:
            self.process_error.emit(message)

    def _handle_finished(self) -> None:
        self.session_stopped.emit()

    def _handle_event(self, raw_line: str) -> None:
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            self.process_error.emit(f"Invalid pipeline event: {exc}")
            return

        event_type = event.get("event_type")
        payload = event.get("payload", {})

        if event_type == "session_started":
            self.session_started.emit(payload)
            return

        if event_type == "caption_segment":
            segment = CaptionSegment.from_event_payload(payload)
            self._segments_by_id[segment.segment_id] = segment
            self.captions_updated.emit(list(self._segments_by_id.values()))
            return

        if event_type == "audio_level":
            self.audio_level_updated.emit(float(payload.get("level", 0.0)))
            return

        if event_type == "error":
            self.process_error.emit(str(payload.get("message", "Unknown pipeline error")))
            return

        if event_type == "session_stopped":
            self.session_stopped.emit()

    @staticmethod
    def _build_environment(env_map: dict[str, str]):
        from PySide6.QtCore import QProcessEnvironment

        env = QProcessEnvironment()
        for key, value in env_map.items():
            env.insert(key, value)
        return env

    @staticmethod
    def _repo_root() -> Path:
        return Path(__file__).resolve().parents[3]

    @classmethod
    def _pipeline_src_dir(cls) -> Path:
        return cls._repo_root() / "services" / "pipeline" / "src"
