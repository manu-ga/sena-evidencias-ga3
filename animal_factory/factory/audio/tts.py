"""Voces: interfaz sustituible + proveedor Piper (offline, gratis).

Para usar otro proveedor (por ejemplo uno en la nube) basta con implementar
`TTSProvider.synthesize` y pasarlo a `Pipeline(tts=...)`. Hoy solo existe Piper.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path
from typing import Protocol

import numpy as np

from ..config import AUDIO_SR, MODELS_DIR

ENV_RATE = 100


class TTSError(RuntimeError):
    pass


class TTSProvider(Protocol):
    name: str

    def available_voices(self) -> list[str]: ...

    def synthesize(self, text: str, voice: str, out_wav: Path, length_scale: float = 1.0) -> None:
        """Escribe un WAV (cualquier frecuencia, mono, 16 bits) con `text` dicho."""


class PiperProvider:
    name = "piper"

    def __init__(self, models_dir: Path | None = None):
        self.models_dir = Path(models_dir or MODELS_DIR)
        self._cache: dict[str, object] = {}

    def available_voices(self) -> list[str]:
        return sorted(p.name[:-5] for p in self.models_dir.glob("*.onnx"))

    def _load(self, voice: str):
        if voice not in self._cache:
            path = self.models_dir / f"{voice}.onnx"
            if not path.exists():
                raise TTSError(
                    f"Falta la voz '{voice}' en {self.models_dir}. Ejecuta: python scripts/descargar_voces.py")
            from piper import PiperVoice  # import tardío: es pesado
            self._cache[voice] = PiperVoice.load(str(path))
        return self._cache[voice]

    def synthesize(self, text: str, voice: str, out_wav: Path, length_scale: float = 1.0) -> None:
        from piper import SynthesisConfig
        v = self._load(voice)
        with wave.open(str(out_wav), "wb") as w:
            v.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=length_scale))
        if out_wav.stat().st_size < 2000:
            raise TTSError(f"Piper no generó audio para: {text!r}")


def postprocess(in_wav: Path, out_wav: Path, pitch: float) -> None:
    """Pasa a 44,1 kHz y cambia el tono sin cambiar la duración (voces distintas por personaje)."""
    with wave.open(str(in_wav)) as w:
        sr = w.getframerate()
    if abs(pitch - 1.0) < 0.01:
        flt = f"aresample={AUDIO_SR}"
    else:
        flt = f"asetrate={sr * pitch:.0f},aresample={AUDIO_SR},atempo={1 / pitch:.4f}"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(in_wav), "-af", flt, "-ac", "1", "-ar", str(AUDIO_SR), str(out_wav)]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise TTSError(f"FFmpeg no pudo procesar la voz: {r.stderr.decode(errors='replace')[-300:]}")


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        raw = w.readframes(w.getnframes())
        ch = w.getnchannels()
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return x.reshape(-1, ch).mean(axis=1) if ch > 1 else x


def write_wav(path: Path, x: np.ndarray, sr: int = AUDIO_SR, channels: int = 1) -> None:
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype(np.int16)
    if channels == 2:
        pcm = np.repeat(pcm[:, None], 2, axis=1).reshape(-1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def envelope(x: np.ndarray, sr: int = AUDIO_SR) -> list[float]:
    """Intensidad 0..1 a 100 Hz, usada para mover la boca."""
    hop = sr // ENV_RATE
    n = len(x) // hop
    if n == 0:
        return []
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    rms = np.convolve(rms, np.ones(3) / 3, mode="same")
    ref = np.percentile(rms, 95) or 1.0
    e = np.clip(rms / ref, 0, 1) ** 0.8
    e[e < 0.1] = 0.0
    return [float(v) for v in e]


def speak(provider: TTSProvider, text: str, voice: str, pitch: float, rate: float, workdir: Path,
          tag: str, speed: float = 1.0) -> tuple[np.ndarray, list[float]]:
    """Genera una línea hablada. `speed`<1 acelera. Devuelve (audio 44,1 kHz, envolvente)."""
    raw = workdir / f"{tag}_raw.wav"
    fin = workdir / f"{tag}.wav"
    provider.synthesize(text, voice, raw, length_scale=rate * speed)
    postprocess(raw, fin, pitch)
    audio = read_wav(fin)
    if len(audio) < AUDIO_SR * 0.2 or float(np.abs(audio).max()) < 0.01:
        raise TTSError(f"El audio de la línea quedó vacío: {text!r}")
    return audio, envelope(audio)
