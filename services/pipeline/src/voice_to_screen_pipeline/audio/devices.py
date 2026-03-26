from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - dependency may not be installed yet
    sd = None


@dataclass(slots=True)
class AudioDevice:
    device_id: str
    name: str
    max_input_channels: int
    default_samplerate: int
    is_default: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "max_input_channels": self.max_input_channels,
            "default_samplerate": self.default_samplerate,
            "is_default": self.is_default,
        }


def list_input_devices() -> list[AudioDevice]:
    if sd is None:
        return _fallback_devices("sounddevice is unavailable")

    try:
        raw_devices = sd.query_devices()
        default_input_id = _default_input_device_id()
    except Exception:
        return _fallback_devices("query failed")

    devices: list[AudioDevice] = []
    for index, raw_device in enumerate(raw_devices):
        max_input_channels = int(raw_device.get("max_input_channels", 0))
        if max_input_channels <= 0:
            continue

        devices.append(
            AudioDevice(
                device_id=str(index),
                name=str(raw_device.get("name", f"Input {index}")),
                max_input_channels=max_input_channels,
                default_samplerate=int(float(raw_device.get("default_samplerate", 16000))),
                is_default=index == default_input_id,
            )
        )

    return devices or _fallback_devices("no input devices found")


def _default_input_device_id() -> int | None:
    if sd is None:
        return None

    default_device = sd.default.device
    if isinstance(default_device, (tuple, list)) and default_device:
        raw_input_id = default_device[0]
        return int(raw_input_id) if raw_input_id is not None and int(raw_input_id) >= 0 else None

    if isinstance(default_device, int) and default_device >= 0:
        return default_device

    return None


def _fallback_devices(reason: str) -> list[AudioDevice]:
    label = f"Mock BlackHole (fallback: {reason})"
    return [
        AudioDevice(
            device_id="fallback-blackhole",
            name=label,
            max_input_channels=2,
            default_samplerate=48000,
            is_default=True,
        )
    ]
