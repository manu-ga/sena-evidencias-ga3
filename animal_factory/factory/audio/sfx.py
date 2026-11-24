"""Efectos de sonido sintetizados con NumPy (sin archivos externos, sin derechos de autor)."""
from __future__ import annotations

import numpy as np

from ..config import AUDIO_SR as SR

_rng = np.random.default_rng(1234)


def _t(d: float) -> np.ndarray:
    return np.arange(int(d * SR)) / SR


def _sine(f, d, decay=0.0, phase=0.0):
    t = _t(d)
    return np.sin(2 * np.pi * f * t + phase) * (np.exp(-decay * t) if decay else 1.0)


def _glide(f0, f1, d, decay=0.0):
    t = _t(d)
    f = f0 + (f1 - f0) * (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (np.exp(-decay * t) if decay else 1.0)


def _noise(d):
    return _rng.uniform(-1, 1, int(d * SR))


def _lp(x, n):
    return np.convolve(x, np.ones(n) / n, mode="same")


def _fade(x, a=0.005, b=0.02):
    x = x.copy()
    na, nb = int(a * SR), int(b * SR)
    if na and len(x) > na:
        x[:na] *= np.linspace(0, 1, na)
    if nb and len(x) > nb:
        x[-nb:] *= np.linspace(1, 0, nb)
    return x


def _saw(f, d, decay=0.0):
    t = _t(d)
    return (2 * ((f * t) % 1.0) - 1) * (np.exp(-decay * t) if decay else 1.0)


def _cat(*parts):
    return np.concatenate(parts)


def coin():
    return _fade(_cat(_sine(988, 0.07, 6) * 0.8, _sine(1319, 0.45, 7)), 0.002) * 0.7


def ding():
    t = _t(0.8)
    return (np.sin(2 * np.pi * 1568 * t) + 0.4 * np.sin(2 * np.pi * 3136 * t)) * np.exp(-5 * t) * 0.5


def sparkle():
    notes = [1175, 1568, 1976, 2349, 2794, 3136]
    return _cat(*[_fade(_sine(f, 0.07, 18), 0.002, 0.01) for f in notes], _sine(3136, 0.3, 9)) * 0.5


def whoosh():
    d = 0.55
    t = _t(d)
    env = np.sin(np.pi * t / d) ** 2
    n = _lp(_noise(d), 30) * 5
    return _fade(n * env * 0.8 + _glide(250, 900, d) * env * 0.15)


def boing():
    d = 0.6
    t = _t(d)
    f = 160 + 380 * np.exp(-t * 9) * (1 + 0.5 * np.cos(2 * np.pi * 16 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-4 * t) * 0.7


def jump():
    return _fade(_glide(220, 700, 0.22, 4) * 0.6)


def pop():
    return _fade(_glide(700, 180, 0.09, 22) * 0.8, 0.001, 0.01)


def thud():
    d = 0.3
    t = _t(d)
    return (np.sin(2 * np.pi * np.cumsum(90 - 50 * t / d) / SR) * 0.9 + _lp(_noise(d), 40) * 2.0) * np.exp(-14 * t)


def step():
    d = 0.07
    return _fade(_lp(_noise(d), 25) * 3.2 * np.exp(-60 * _t(d)), 0.001, 0.01) * 0.5


def crash():
    d = 1.0
    t = _t(d)
    metal = sum(np.sin(2 * np.pi * f * t) for f in (610, 940, 1330, 2010, 2870, 3920)) * 0.12
    return _fade((_noise(d) * 0.7 + metal) * np.exp(-6 * t) + thud()[: len(t)].mean() * 0, 0.001, 0.05) * 0.85


def boom():
    d = 0.9
    t = _t(d)
    return (np.sin(2 * np.pi * 55 * t) * 0.9 + _lp(_noise(d), 60) * 3) * np.exp(-4.5 * t)


def gasp():
    d = 0.4
    t = _t(d)
    n = _noise(d)
    hp = n - _lp(n, 12)
    return _fade(hp * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 * 0.8)


def knock():
    one = _fade((_sine(190, 0.1, 30) + _lp(_noise(0.1), 20) * 1.5 * np.exp(-40 * _t(0.1))), 0.001, 0.01)
    gap = np.zeros(int(0.13 * SR))
    return _cat(one, gap, one, gap, one) * 0.8


def cash():
    t = _t(0.7)
    click = _fade(_noise(0.03) * 0.8, 0.001, 0.01)
    bell = (np.sin(2 * np.pi * 2093 * t) + np.sin(2 * np.pi * 2637 * t)) * np.exp(-6 * t) * 0.45
    return _cat(click, np.zeros(int(0.05 * SR)), bell)


def siren():
    d = 1.6
    t = _t(d)
    f = 850 + 250 * np.sign(np.sin(2 * np.pi * 1.2 * t)) * 0 + 250 * np.sin(2 * np.pi * 1.2 * t)
    return _fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35, 0.05, 0.1)


def applause():
    d = 2.2
    t = _t(d)
    clicks = _noise(d) * (_rng.random(len(t)) < 0.12)
    env = np.clip(t / 0.3, 0, 1) * np.clip((d - t) / 0.8, 0, 1)
    return _lp(clicks, 6) * 6 * env * 0.7


def fanfare():
    notes = [(523, 0.14), (659, 0.14), (784, 0.14), (1047, 0.6)]
    out = []
    for f, d in notes:
        s = (_saw(f, d) * 0.5 + _sine(f, d) * 0.5) * 0.45
        out.append(_fade(_lp(s, 4), 0.01, 0.05))
    return _cat(*out)


def sad():
    notes = [(196, 0.4), (185, 0.4), (175, 0.4), (165, 0.9)]
    out = []
    for i, (f, d) in enumerate(notes):
        t = _t(d)
        vib = 1 + (0.02 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0)
        s = _lp(2 * ((np.cumsum(f * vib) / SR) % 1.0) - 1, 6) * 0.5
        out.append(_fade(s, 0.03, 0.08))
    return _cat(*out)


def heart():
    return _cat(_fade(_sine(523, 0.14, 10), 0.005), _fade(_sine(659, 0.3, 8), 0.005)) * 0.6


SFX = {
    "coin": coin, "ding": ding, "sparkle": sparkle, "whoosh": whoosh, "boing": boing, "jump": jump,
    "pop": pop, "thud": thud, "step": step, "crash": crash, "boom": boom, "gasp": gasp, "knock": knock,
    "cash": cash, "siren": siren, "applause": applause, "fanfare": fanfare, "sad": sad, "heart": heart,
}
_cache: dict[str, np.ndarray] = {}


def get_sfx(name: str) -> np.ndarray:
    if name not in SFX:
        raise KeyError(f"Efecto desconocido: {name}")
    if name not in _cache:
        x = SFX[name]().astype(np.float32)
        peak = float(np.abs(x).max()) or 1.0
        _cache[name] = x / peak * 0.8
    return _cache[name]
