from __future__ import annotations

import json
import sys

from .audio.devices import list_input_devices
from .contracts import SessionConfig
from .orchestrator import PipelineOrchestrator


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "list-devices":
        _print_devices()
        return

    raw_config = sys.argv[1] if len(sys.argv) > 1 else None
    config = _parse_config(raw_config)
    orchestrator = PipelineOrchestrator(config=config)

    for event in orchestrator.start():
        print(json.dumps(event.to_dict()))


def _parse_config(raw_config: str | None) -> SessionConfig:
    if not raw_config:
        return SessionConfig(source_language="ja")

    payload = json.loads(raw_config)
    return SessionConfig(
        source_language=str(payload.get("source_language", "ja")),
        input_device_id=str(payload.get("input_device_id", "")),
        target_language=str(payload.get("target_language", "en")),
        model_tier=str(payload.get("model_tier", "balanced")),
        compact_mode=bool(payload.get("compact_mode", False)),
        speaker_labels_enabled=bool(payload.get("speaker_labels_enabled", True)),
        gender_hints_enabled=bool(payload.get("gender_hints_enabled", False)),
    )


def _print_devices() -> None:
    payload = {"devices": [device.to_dict() for device in list_input_devices()]}
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
