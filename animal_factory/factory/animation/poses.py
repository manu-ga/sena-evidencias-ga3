"""Animación por poses: convierte (acciones del guion, tiempo) en un `Pose`.

Todo se calcula con funciones del tiempo, sin fotogramas dibujados a mano.
"""
from __future__ import annotations

import math

from ..characters.rig import Pose
from ..config import GROUND_Y
from ..models import Beat, CharacterSpec

MOVING = {"walk", "run", "jump", "celebrate"}


def smooth(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def _lerp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


def _emotion(p: Pose, emo: str | None) -> None:
    if emo == "happy":
        p.mouth_shape, p.blush = "smile", True
    elif emo == "sad":
        p.eyes, p.mouth_shape, p.head_tilt = "sad", "frown", p.head_tilt + 6
    elif emo == "angry":
        p.eyes, p.mouth_shape = "angry", "flat"
    elif emo == "surprised":
        p.eyes, p.mouth_shape, p.emote = "wide", "o", "!"
    elif emo == "scared":
        p.eyes, p.mouth_shape, p.sweat = "wide", "frown", True
    elif emo == "greedy":
        p.eyes, p.mouth_shape, p.emote = "greedy", "laugh", "$"
    elif emo == "love":
        p.eyes, p.blush, p.emote = "happy", True, "heart"
    elif emo == "thinking":
        p.emote = "?"


def _active(beats: list[Beat], tf: float) -> tuple[Beat | None, float, bool]:
    """Devuelve (beat, u, activo). Si no hay beat activo devuelve el último pasado."""
    last_past = None
    for b in beats:
        if b.t0 <= tf < b.t1:
            return b, (tf - b.t0) / max(1e-6, b.t1 - b.t0), True
        if b.t1 <= tf:
            last_past = b
    if last_past is not None:
        return last_past, 1.0, False
    return (beats[0] if beats else None), 0.0, False


def position_and_facing(beats: list[Beat], tf: float) -> tuple[float, int, float]:
    """Posición x, orientación y avance 0..1 dentro del beat actual."""
    if not beats:
        return 540.0, 1, 0.0
    facing = 1 if beats[0].x0 < 540 else -1
    x = beats[0].x0
    for b in beats:
        end = b.x1 if b.x1 is not None else b.x0
        if b.face:
            facing = b.face
        elif end != b.x0:
            facing = 1 if end > b.x0 else -1
        if tf < b.t0:
            break
        if tf < b.t1:
            u = (tf - b.t0) / max(1e-6, b.t1 - b.t0)
            e = smooth(u) if b.action in ("walk", "run", "dance") else u
            x = _lerp(b.x0, end, e) if b.action in MOVING | {"dance"} else (b.x0 if b.x1 is None else _lerp(b.x0, end, smooth(u)))
            return x, facing, u
        x = end
    return x, facing, 1.0


def actor_pose(spec: CharacterSpec, beats: list[Beat], tf: float, t: float,
               mouth: float | None, seed: float = 0.0) -> Pose:
    """Pose del personaje en el instante `t` (segundos) = `tf` (fracción de la escena)."""
    p = Pose()
    x, facing, _ = position_and_facing(beats, tf)
    p.x, p.facing = x, facing
    beat, u, active = _active(beats, tf)
    action = beat.action if (beat and active) else "idle"
    emo = beat.emo if beat else None
    tt = t + seed

    # respiración y parpadeo comunes
    p.bob = math.sin(2 * math.pi * 0.7 * tt) * 3
    p.tail = math.sin(2 * math.pi * 0.9 * tt) * 10
    p.arm_l = p.arm_r = 8 + math.sin(2 * math.pi * 0.7 * tt) * 2
    p.ear = math.sin(2 * math.pi * 0.5 * tt) * 3
    if (tt * 0.8) % 3.1 < 0.11:
        p.eyes = "closed"

    if action == "walk":
        ph = 2 * math.pi * 1.7 * tt
        p.leg_l, p.leg_r = 28 * math.sin(ph), -28 * math.sin(ph)
        p.arm_l, p.arm_r = 18 + 14 * math.sin(ph), 18 - 14 * math.sin(ph)
        p.bob, p.lean = -abs(math.sin(ph)) * 9, 4
        p.tail = 14 * math.sin(ph * 0.5)
        p.head_tilt = 2 * math.sin(ph)
    elif action == "run":
        ph = 2 * math.pi * 2.8 * tt
        p.leg_l, p.leg_r = 55 * math.sin(ph), -55 * math.sin(ph)
        p.arm_l, p.arm_r = 45 + 45 * math.sin(ph), 45 - 45 * math.sin(ph)
        p.bob, p.lean = -abs(math.sin(ph)) * 20, 13
        p.tail, p.ear = 22, 24 + 6 * math.sin(ph)
        p.eyes = "wide" if p.eyes != "closed" else "open"
        p.sx = 1.03
    elif action == "jump":
        if u < 0.2:
            k = smooth(u / 0.2)
            p.sy, p.sx, p.bob = 1 - 0.16 * k, 1 + 0.1 * k, 12 * k
            p.arm_l = p.arm_r = 20
        elif u < 0.82:
            v = (u - 0.2) / 0.62
            h = 300 * 4 * v * (1 - v)
            p.y = GROUND_Y - h
            p.sy, p.sx = 1.08, 0.96
            p.arm_l = p.arm_r = 150
            p.leg_l, p.leg_r = 35, -20
            p.eyes, p.mouth_shape = "happy", "laugh"
        else:
            k = smooth((u - 0.82) / 0.18)
            p.sy, p.sx, p.bob = 0.86 + 0.14 * k, 1.12 - 0.12 * k, 10 * (1 - k)
    elif action == "laugh":
        p.bob = -abs(math.sin(2 * math.pi * 4 * tt)) * 10
        p.head_tilt = 7 * math.sin(2 * math.pi * 3 * tt)
        p.eyes, p.mouth_shape, p.mouth, p.blush = "happy", "laugh", 0.6 + 0.3 * math.sin(2 * math.pi * 6 * tt), True
        p.arm_l, p.arm_r = 25, 25
        p.tail = 25 * math.sin(2 * math.pi * 3 * tt)
    elif action == "cry":
        p.eyes, p.mouth_shape, p.tear = "sad", "frown", True
        p.bob = math.sin(2 * math.pi * 5 * tt) * 3
        p.head_tilt, p.sy = 7, 0.97
        p.arm_l = p.arm_r = 18
        p.tail = -10
        p.mouth = 0.35 + 0.2 * math.sin(2 * math.pi * 5 * tt)
    elif action == "angry":
        p.eyes, p.mouth_shape = "angry", "flat"
        p.arm_l = p.arm_r = 38
        p.head_tilt = 4 * math.sin(2 * math.pi * 7 * tt)
        p.x += 3 * math.sin(2 * math.pi * 12 * tt)
        p.mouth = 0.35 + 0.25 * abs(math.sin(2 * math.pi * 6 * tt))
        p.tail = 35
    elif action == "surprise":
        k = smooth(u / 0.25) if active else 1.0
        p.lean, p.sy = -12 * k, 1 + 0.06 * k
        p.eyes, p.mouth_shape, p.emote = "wide", "o", "!"
        p.arm_l = p.arm_r = 60 * k
        p.ear = 18 * k
        p.x -= facing * 14 * k
    elif action == "dance":
        ph = 2 * math.pi * 2.2 * tt
        p.arm_l, p.arm_r = 90 + 70 * math.sin(ph), 90 - 70 * math.sin(ph)
        p.leg_l, p.leg_r = 22 * math.sin(ph), -22 * math.sin(ph)
        p.bob = -abs(math.sin(ph)) * 14
        p.head_tilt = 8 * math.sin(ph)
        p.eyes, p.mouth_shape, p.tail = "happy", "laugh", 30 * math.sin(ph * 2)
        p.mouth = 0.5
    elif action == "fall":
        k = smooth(u / 0.35)
        p.rot = 88 * facing * k
        p.y = GROUND_Y - 58 * k
        p.eyes, p.mouth_shape = ("dizzy", "o") if k > 0.9 else ("wide", "o")
        p.arm_l = p.arm_r = 120 * (1 - k)
    elif action == "think":
        p.arm_r = 150
        p.head_tilt = 6 + 3 * math.sin(2 * math.pi * 0.6 * tt)
        p.look = -0.6
        p.emote, p.mouth_shape = "?", "flat"
    elif action == "celebrate":
        cyc = (u * 3) % 1.0
        h = 140 * 4 * cyc * (1 - cyc)
        p.y = GROUND_Y - h
        p.arm_l = p.arm_r = 160
        p.eyes, p.mouth_shape, p.mouth = "happy", "laugh", 0.7
        p.tail = 35 * math.sin(2 * math.pi * 4 * tt)
        p.sy = 1.05
    elif action == "shiver":
        p.x += 3.5 * math.sin(2 * math.pi * 14 * tt)
        p.eyes, p.mouth_shape, p.sweat = "wide", "frown", True
        p.arm_l = p.arm_r = 30
        p.tail = -15
    elif action == "shrug":
        p.arm_l = p.arm_r = 62
        p.head_tilt, p.emote, p.mouth_shape = 9, "?", "flat"

    if emo and action in ("idle", "think", "shrug", "walk", "run"):
        _emotion(p, emo)
    elif emo and action in ("cry", "laugh", "surprise", "angry", "shiver"):
        pass

    # hablando: la boca sigue la envolvente real del audio + gesto de manos
    if mouth is not None:
        p.mouth = max(p.mouth, min(1.0, mouth))
        if p.mouth_shape in ("flat", "o") and action not in ("angry", "surprise"):
            p.mouth_shape = "smile"
        if action in ("idle", "think", "shrug"):
            g = math.sin(2 * math.pi * 1.4 * tt)
            p.arm_r = 30 + 28 * max(0.0, g)
            p.arm_l = 12 + 8 * max(0.0, -g)
            p.head_tilt += 3 * g
            p.bob += -abs(g) * 3
    return p
