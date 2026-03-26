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


@dataclass(slots=True)
class AudioPacket:
    level: float
    pcm_bytes: bytes


class AudioSource:
    """Minimal live audio monitor for input verification."""

    def __init__(self, config: AudioSourceConfig) -> None:
        self.config = config
        self._packets: Queue[AudioPacket] = Queue()
        self._stream = None
        self.last_error: str | None = None
        self.active_sample_rate = config.sample_rate
        self._device_sample_rate = config.sample_rate
        self._device_channels = config.channels

    def start(self) -> None:
        """Start ingesting audio from the selected device."""
        self.last_error = None
        if sd is None or np is None:
            self._stream = None
            self.last_error = "Audio dependencies are unavailable"
            return

        if self.config.device_id.startswith("fallback-"):
            self._stream = None
            return

        try:
            device_info = sd.query_devices(int(self.config.device_id), "input")
            input_channels = int(device_info["max_input_channels"])
            channels = max(1, min(self.config.channels, input_channels))
            sample_rate = int(float(device_info.get("default_samplerate", self.config.sample_rate)))
            self._device_sample_rate = sample_rate
            self._device_channels = channels
            self.active_sample_rate = self.config.sample_rate

            sd.check_input_settings(
                device=int(self.config.device_id),
                channels=channels,
                dtype="int16",
                samplerate=sample_rate,
            )

            self._stream = sd.RawInputStream(
                device=int(self.config.device_id),
                samplerate=sample_rate,
                channels=channels,
                callback=self._on_audio,
                dtype="int16",
                blocksize=1024,
            )
            self._stream.start()
        except Exception as exc:
            self._stream = None
            self.last_error = str(exc)

    def stop(self) -> None:
        """Stop ingesting audio."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def iter_packets(self) -> Iterator[AudioPacket]:
        """Yield normalized audio levels plus raw PCM for the active stream."""
        if self._stream is None:
            yield from self._fallback_levels()
            return

        while True:
            try:
                yield self._packets.get(timeout=0.25)
            except Empty:
                yield AudioPacket(level=0.0, pcm_bytes=b"")

    def _on_audio(self, indata, frames, time_info, status) -> None:  # type: ignore[no-untyped-def]
        _ = frames, time_info, status
        if np is None:
            return

        pcm_bytes = bytes(indata)
        raw_samples = np.frombuffer(pcm_bytes, dtype=np.int16)
        if self._device_channels > 1:
            raw_samples = raw_samples.reshape(-1, self._device_channels).mean(axis=1).astype(np.int16)

        processed_samples = self._resample_to_target_rate(raw_samples)
        samples = processed_samples.astype(np.float32) / 32768.0
        if samples.size == 0:
            level = 0.0
        else:
            level = float(np.sqrt(np.mean(np.square(samples))))
        self._packets.put(
            AudioPacket(
                level=min(max(level * 8.0, 0.0), 1.0),
                pcm_bytes=processed_samples.tobytes(),
            )
        )

    def _fallback_levels(self) -> Iterator[AudioPacket]:
        start = monotonic()
        while True:
            phase = (monotonic() - start) * 2.4
            level = 0.18 + 0.12 * ((phase % 1.0) * 0.5)
            sleep(0.08)
            yield AudioPacket(level=level, pcm_bytes=b"")

    def _resample_to_target_rate(self, samples: "np.ndarray") -> "np.ndarray":
        if np is None or samples.size == 0:
            return samples

        if self._device_sample_rate == self.config.sample_rate:
            return samples.astype(np.int16, copy=False)

        ratio = self._device_sample_rate / self.config.sample_rate
        if ratio.is_integer():
            step = int(ratio)
            return samples[::step].astype(np.int16, copy=False)

        target_length = max(1, int(len(samples) * self.config.sample_rate / self._device_sample_rate))
        source_positions = np.arange(len(samples), dtype=np.float32)
        target_positions = np.linspace(0, max(len(samples) - 1, 0), num=target_length, dtype=np.float32)
        resampled = np.interp(target_positions, source_positions, samples.astype(np.float32))
        return np.clip(resampled, -32768, 32767).astype(np.int16)
