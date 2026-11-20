"""Mezcla final: voces + efectos (del guion y automáticos) + música con ducking."""
from __future__ import annotations

import numpy as np

from ..animation.poses import position_and_facing
from ..config import AUDIO_SR as SR, TRANSITION
from ..models import Scene
from .music import render_music
from .sfx import get_sfx

WALK_HZ, RUN_HZ = 1.7, 2.8   # deben coincidir con poses.py


def _place(buf: np.ndarray, x: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    if i < 0 or i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


def auto_sfx(scene: Scene) -> list[tuple[float, str, float]]:
    """Pasos al caminar/correr y salto/aterrizaje, sincronizados con las poses."""
    d = scene.duration
    cues: list[tuple[float, str, float]] = []
    seeds = {cid: k * 0.77 for k, cid in enumerate(scene.cast)}
    by_actor: dict[str, list] = {}
    for b in scene.beats:
        by_actor.setdefault(b.actor, []).append(b)
    for b in scene.beats:
        seed = seeds.get(b.actor, 0.0)
        a, z = b.t0 * d, b.t1 * d
        if b.action in ("walk", "run"):
            hz = WALK_HZ if b.action == "walk" else RUN_HZ
            j = int(np.ceil((a + seed) * 2 * hz))
            while True:
                t = j / (2 * hz) - seed
                if t >= z:
                    break
                x = position_and_facing(sorted(by_actor[b.actor], key=lambda q: q.t0), t / d)[0]
                if -40 < x < 1120:
                    cues.append((t, "step", 0.5 if b.action == "walk" else 0.7))
                j += 1
        elif b.action == "jump":
            cues.append((a + 0.2 * (z - a), "jump", 0.5))
            cues.append((a + 0.82 * (z - a), "thud", 0.45))
        elif b.action == "fall":
            cues.append((a + 0.3 * (z - a), "thud", 0.7))
    return cues


def mix_soundtrack(scenes: list[Scene], starts: list[float], total: float,
                   voice_clips: list[list[tuple[float, np.ndarray]]]) -> tuple[np.ndarray, dict]:
    n = int(total * SR)
    voice = np.zeros(n, np.float32)
    sfx = np.zeros(n, np.float32)
    music = np.zeros(n, np.float32)

    for sc, s0, clips in zip(scenes, starts, voice_clips):
        for t, a in clips:
            rms = float(np.sqrt((a ** 2).mean())) or 1.0
            _place(voice, a * min(3.0, 0.13 / rms), s0 + t)
        for c in sc.sfx:
            _place(sfx, get_sfx(c.name), s0 + c.t * sc.duration, 0.65 * c.gain)
        for t, name, g in auto_sfx(sc):
            _place(sfx, get_sfx(name), s0 + t, 0.5 * g)
        seg_len = sc.duration + TRANSITION
        m = render_music(sc.mood, seg_len, seed=sc.index)
        fi, fo = int(0.4 * SR), int(min(TRANSITION + 0.2, 0.9) * SR)
        if sc.index > 1:
            m[:fi] *= np.linspace(0, 1, min(fi, len(m)))
        m[-fo:] *= np.linspace(1, 0, min(fo, len(m)))
        _place(music, m, s0, 1.0)

    # ducking: la música baja cuando alguien habla
    win = int(0.05 * SR)
    env = np.convolve(np.abs(voice), np.ones(win) / win, mode="same")
    duck = 1.0 - 0.65 * np.clip(env / 0.06, 0, 1)
    rel = int(0.3 * SR)
    duck = np.convolve(duck, np.ones(rel) / rel, mode="same")
    mix = voice * 1.0 + sfx * 0.6 + music * 0.5 * duck
    peak = float(np.abs(mix).max()) or 1.0
    if peak > 0.92:
        mix = mix / peak * 0.92
    stats = {
        "pico": round(peak, 3),
        "rms_voz": round(float(np.sqrt((voice ** 2).mean())), 4),
        "rms_musica": round(float(np.sqrt(((music * 0.5 * duck) ** 2).mean())), 4),
        "rms_efectos": round(float(np.sqrt((sfx ** 2).mean())), 4),
    }
    return mix.astype(np.float32), stats
