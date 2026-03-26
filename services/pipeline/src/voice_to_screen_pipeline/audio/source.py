from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
from time import sleep
from time import monotonic
from typing import Iterator

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

try:
    import sounddevice as sd
except Exception:  # pragma: no cover
    sd = None


@dataclass(slots=True)
class AudioSourceConfig:
    device_id: str
    sample_rate: int = 16000
    channels: int = 1


class AudioSource:
    """Minimal live audio monitor for input verification."""

    def __init__(self, config: AudioSourceConfig) -> None:
        self.config = config
        self._levels: Queue[float] = Queue()
        self._stream = None

    def start(self) -> None:
        """Start ingesting audio from the selected device."""
        if sd is None or np is None:
            self._stream = None
            return

        if self.config.device_id.startswith("fallback-"):
            self._stream = None
            return

        try:
            self._stream = sd.InputStream(
                device=int(self.config.device_id),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                callback=self._on_audio,
                dtype="float32",
                blocksize=2048,
            )
            self._stream.start()
        except Exception:
            self._stream = None

    def stop(self) -> None:
        """Stop ingesting audio."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def iter_levels(self) -> Iterator[float]:
        """Yield normalized audio levels for the active stream."""
        if self._stream is None:
            yield from self._fallback_levels()
            return

        while True:
            try:
                yield self._levels.get(timeout=0.25)
            except Empty:
                yield 0.0

    def _on_audio(self, indata, frames, time_info, status) -> None:  # type: ignore[no-untyped-def]
        _ = frames, time_info, status
        if np is None:
            return

        level = float(np.sqrt(np.mean(np.square(indata))))
        self._levels.put(min(max(level * 8.0, 0.0), 1.0))

    def _fallback_levels(self) -> Iterator[float]:
        start = monotonic()
        while True:
            phase = (monotonic() - start) * 2.4
            level = 0.18 + 0.12 * ((phase % 1.0) * 0.5)
            sleep(0.08)
            yield level
