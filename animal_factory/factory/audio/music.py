"""Música de fondo original, sintetizada por código (libre de derechos)."""
from __future__ import annotations

import zlib

import numpy as np

from ..config import AUDIO_SR as SR

# nota MIDI -> frecuencia
def _f(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


MOODS = {
    #            bpm  raíz  progresión (grados en semitonos y tipo)         estilo
    "alegre":     (122, 60, [(0, "M"), (7, "M"), (9, "m"), (5, "M")], "pop"),
    "misterioso": (78, 57, [(0, "m"), (8, "M"), (3, "M"), (10, "M")], "pad"),
    "tenso":      (104, 52, [(0, "m"), (1, "M"), (0, "m"), (6, "M")], "pulse"),
    "triunfal":   (112, 60, [(0, "M"), (5, "M"), (7, "M"), (0, "M")], "pop"),
    "triste":     (66, 57, [(0, "m"), (5, "m"), (3, "M"), (7, "M")], "pad"),
}


def _tone(freq: float, d: float, kind: str, vol: float = 1.0, attack=0.01, release=0.08) -> np.ndarray:
    n = int(d * SR)
    t = np.arange(n) / SR
    ph = (freq * t) % 1.0
    if kind == "square":
        w = np.sign(np.sin(2 * np.pi * freq * t)) * 0.6
    elif kind == "saw":
        w = (2 * ph - 1) * 0.6
    elif kind == "tri":
        w = (2 * np.abs(2 * ph - 1) - 1)
    else:
        w = np.sin(2 * np.pi * freq * t)
    env = np.ones(n)
    a, r = min(n, int(attack * SR)), min(n, int(release * SR))
    if a:
        env[:a] = np.linspace(0, 1, a)
    if r:
        env[-r:] *= np.linspace(1, 0, r)
    return w * env * vol


def _add(buf: np.ndarray, x: np.ndarray, at: float) -> None:
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i]


def _drum(kind: str) -> np.ndarray:
    rng = np.random.default_rng(7)
    if kind == "kick":
        t = np.arange(int(0.18 * SR)) / SR
        return np.sin(2 * np.pi * np.cumsum(120 - 80 * t / 0.18) / SR) * np.exp(-18 * t)
    if kind == "snare":
        t = np.arange(int(0.14 * SR)) / SR
        return rng.uniform(-1, 1, len(t)) * np.exp(-28 * t) * 0.6
    t = np.arange(int(0.04 * SR)) / SR
    n = rng.uniform(-1, 1, len(t))
    return (n - np.convolve(n, np.ones(8) / 8, mode="same")) * np.exp(-90 * t) * 0.35


def render_music(mood: str, duration: float, seed: int = 0) -> np.ndarray:
    bpm, root, prog, style = MOODS.get(mood, MOODS["alegre"])
    rng = np.random.default_rng(seed + zlib.crc32(mood.encode()) % 1000)
    out = np.zeros(int(duration * SR) + SR)
    beat = 60.0 / bpm
    bar = 4 * beat
    nbars = int(duration / bar) + 2
    for b in range(nbars):
        deg, qual = prog[b % len(prog)]
        r = root + deg
        third = 4 if qual == "M" else 3
        chord = [r, r + third, r + 7]
        t0 = b * bar
        if style == "pad":
            for m in chord:
                _add(out, _tone(_f(m), bar, "tri", 0.16, 0.25, 0.4), t0)
            _add(out, _tone(_f(r - 12), bar, "sine", 0.25, 0.1, 0.3), t0)
            for k in range(2):  # notas sueltas de campanita
                m = chord[int(rng.integers(0, 3))] + 12
                _add(out, _tone(_f(m), beat * 1.2, "sine", 0.18, 0.005, 0.5), t0 + (k * 2 + int(rng.integers(0, 2))) * beat)
        elif style == "pulse":
            for k in range(8):
                _add(out, _tone(_f(r - 12), beat * 0.45, "saw", 0.22, 0.005, 0.06), t0 + k * beat / 2)
            _add(out, _tone(_f(r + 6), beat * 2, "tri", 0.1, 0.2, 0.3), t0 + 2 * beat)
            for k in range(4):
                _add(out, _drum("kick") * 0.8, t0 + k * beat)
            _add(out, _drum("hat"), t0 + beat * 0.5)
        else:  # pop alegre / triunfal
            for k in range(4):
                _add(out, _drum("kick") * 0.7, t0 + k * beat)
                _add(out, _drum("hat"), t0 + k * beat + beat / 2)
            _add(out, _drum("snare"), t0 + beat)
            _add(out, _drum("snare"), t0 + 3 * beat)
            for k in range(8):
                _add(out, _tone(_f(r - 12 if k % 2 == 0 else r - 5), beat * 0.45, "tri", 0.3, 0.005, 0.05), t0 + k * beat / 2)
            arp = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
            for k in range(8):
                _add(out, _tone(_f(arp[k % 4] + (12 if k >= 4 and style == "pop" else 0)), beat * 0.4, "square", 0.09, 0.005, 0.06),
                     t0 + k * beat / 2)
            if mood == "triunfal":
                for m in chord:
                    _add(out, _tone(_f(m), bar, "saw", 0.07, 0.04, 0.2), t0)
    out = out[: int(duration * SR)]
    peak = float(np.abs(out).max()) or 1.0
    return (out / peak * 0.55).astype(np.float32)
