"""Renderizador de escenas: línea de tiempo -> fotogramas SVG -> PNG -> clip MP4."""
from __future__ import annotations

import math
import os
import random
import subprocess
from pathlib import Path

import resvg_py

from ..characters.rig import Pose, character_svg
from ..config import GROUND_Y, WORLD_H, WORLD_W
from ..models import CameraKey, CharacterSpec, Scene
from .backgrounds import background_svg, prop_svg
from .poses import actor_pose, position_and_facing, smooth
from .styles import Style, get_style

ENV_RATE = 100  # muestras por segundo de la envolvente de audio
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
SUB_SIZE = 54
SUB_MAX_W = 900

try:  # medición real del texto para ajustar líneas
    from PIL import ImageFont
    _FONT = ImageFont.truetype(FONT_PATH, SUB_SIZE) if FONT_PATH else None
except Exception:  # pragma: no cover
    _FONT = None


def text_width(s: str) -> float:
    if _FONT is not None:
        return _FONT.getlength(s)
    return len(s) * SUB_SIZE * 0.64


def wrap(text: str, max_w: float = SUB_MAX_W) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if text_width(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def subtitle_chunks(text: str, t0: float, t1: float) -> list[tuple[float, float, str]]:
    """Parte una frase en trozos de máx. 2 líneas y reparte el tiempo según su longitud."""
    words, chunks, cur = text.split(), [], []
    for w in words:
        trial = " ".join(cur + [w])
        if len(wrap(trial)) <= 2 or not cur:
            cur.append(w)
        else:
            chunks.append(" ".join(cur))
            cur = [w]
    if cur:
        chunks.append(" ".join(cur))
    total = sum(len(c) for c in chunks) or 1
    out, t = [], t0
    for c in chunks:
        d = (t1 - t0) * len(c) / total
        out.append((t, t + d, c))
        t += d
    return out


def subtitle_events(scene: Scene, characters: dict[str, CharacterSpec]) -> list[tuple[float, float, str, str]]:
    ev = []
    for line, (a, b) in zip(scene.lines, scene.line_times):
        for c0, c1, txt in subtitle_chunks(line.text, a, b + 0.12):
            ev.append((c0, c1, line.speaker, txt))
    return ev


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SceneRenderer:
    def __init__(self, scene: Scene, characters: dict[str, CharacterSpec], style: Style,
                 envelopes: list[list[float]] | None = None):
        self.scene = scene
        self.chars = characters
        self.style = style
        self.env = envelopes or [[] for _ in scene.lines]
        self.beats: dict[str, list] = {}
        for b in scene.beats:
            self.beats.setdefault(b.actor, []).append(b)
        for v in self.beats.values():
            v.sort(key=lambda b: b.t0)
        self.sub_events = subtitle_events(scene, characters)
        self.cam_keys = sorted(scene.camera or [CameraKey(0.0, "wide")], key=lambda k: k.t)
        self.crash_times = [c.t * scene.duration for c in scene.sfx if c.name in ("crash", "boom", "thud")]

    # ------------------------------------------------------------------ audio -> boca
    def _speaking(self, t: float) -> tuple[str | None, float]:
        for i, (a, b) in enumerate(self.scene.line_times):
            if a <= t < b:
                env = self.env[i] if i < len(self.env) else []
                k = int((t - a) * ENV_RATE)
                v = env[k] if 0 <= k < len(env) else 0.55
                return self.scene.lines[i].speaker, v
        return None, 0.0

    # ------------------------------------------------------------------ cámara
    def _shot_target(self, key: CameraKey, t: float, xs: dict[str, float]) -> tuple[float, float, float]:
        focus_x = xs.get(key.focus) if key.focus else None
        if focus_x is None:
            vals = [x for x in xs.values() if 0 < x < WORLD_W]
            focus_x = sum(vals) / len(vals) if vals else WORLD_W / 2
        shot = key.shot
        if shot == "wide":
            return WORLD_W / 2, WORLD_H / 2, 1.0
        if shot == "medium":
            return focus_x, 1060, 1.35
        if shot == "close":
            return focus_x, 1010, 1.8
        if shot == "follow":
            return focus_x, 1080, 1.3
        return WORLD_W / 2, WORLD_H / 2, 1.0

    def camera_at(self, t: float, xs: dict[str, float]) -> tuple[float, float, float]:
        dur = max(self.scene.duration, 1e-6)
        tf = t / dur
        idx = 0
        for i, k in enumerate(self.cam_keys):
            if k.t <= tf:
                idx = i
        key = self.cam_keys[idx]
        cx, cy, z = self._shot_target(key, t, xs)
        if idx > 0 and not key.cut:
            since = t - key.t * dur
            u = smooth(since / 0.7)
            if u < 1:
                px, py, pz = self._shot_target(self.cam_keys[idx - 1], t, xs)
                cx, cy, z = px + (cx - px) * u, py + (cy - py) * u, pz + (z - pz) * u
        # empuje suave continuo para que la cámara nunca esté estática
        z *= 1 + 0.04 * (tf)
        for ct in self.crash_times:
            if 0 <= t - ct < 0.4:
                a = (1 - (t - ct) / 0.4) * 22
                cx += a * math.sin(t * 90)
                cy += a * math.cos(t * 77)
        z = max(1.0, z)
        hw, hh = WORLD_W / (2 * z), WORLD_H / (2 * z)
        cx = min(max(cx, hw), WORLD_W - hw)
        cy = min(max(cy, hh), WORLD_H - hh)
        return cx, cy, z

    # ------------------------------------------------------------------ subtítulos
    def _subtitle_svg(self, t: float) -> str:
        cur = None
        for a, b, spk, txt in self.sub_events:
            if a <= t < b:
                cur = (spk, txt)
        if not cur:
            return ""
        spk, txt = cur
        lines = wrap(txt)[:3]
        lh = SUB_SIZE * 1.22
        bw = min(SUB_MAX_W + 70, max(text_width(l) for l in lines) + 70)
        bh = lh * len(lines) + 36
        cy = 1650
        x0 = (WORLD_W - bw) / 2
        out = [f'<rect x="{x0:.0f}" y="{cy - bh / 2:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="30" fill="#000" opacity="0.62"/>']
        color = "#ffffff"
        if spk in self.chars:
            color = self.chars[spk].color
            name = self.chars[spk].name.upper()
            nw = text_width(name) * 0.55 + 40
            out.append(f'<rect x="{x0 + 24:.0f}" y="{cy - bh / 2 - 30:.0f}" width="{nw:.0f}" height="44" rx="22" fill="{color}"/>'
                       f'<text x="{x0 + 24 + nw / 2:.0f}" y="{cy - bh / 2 + 2:.0f}" font-family="DejaVu Sans" font-weight="bold" '
                       f'font-size="28" text-anchor="middle" fill="#1b1b1b">{_esc(name)}</text>')
        for i, l in enumerate(lines):
            y = cy - bh / 2 + 18 + lh * (i + 0.8)
            out.append(f'<text x="{WORLD_W / 2:.0f}" y="{y:.0f}" font-family="DejaVu Sans" font-weight="bold" font-size="{SUB_SIZE}" '
                       f'text-anchor="middle" fill="{color}" stroke="#000" stroke-width="7" paint-order="stroke" '
                       f'stroke-linejoin="round">{_esc(l)}</text>')
        return "".join(out)

    # ------------------------------------------------------------------ fotograma
    def frame_svg(self, t: float, out_w: int = WORLD_W, out_h: int = WORLD_H) -> str:
        sc = self.scene
        dur = max(sc.duration, 1e-6)
        tf = t / dur
        speaker, env_v = self._speaking(t)

        xs: dict[str, float] = {}
        for cid, beats in self.beats.items():
            xs[cid] = position_and_facing(beats, tf)[0]

        poses: list[tuple[str, Pose]] = []
        for k, cid in enumerate(sc.cast):
            if cid not in self.beats or cid not in self.chars:
                continue
            beats = self.beats[cid]
            mouth = env_v if speaker == cid else None
            p = actor_pose(self.chars[cid], beats, tf, t, mouth, seed=k * 0.77)
            # los oyentes miran a quien habla
            if speaker and speaker != cid and speaker in xs:
                beat_now = next((b for b in beats if b.t0 <= tf < b.t1), None)
                if beat_now is None or beat_now.action in ("idle", "think", "shrug", "laugh"):
                    d = 1 if xs[speaker] >= p.x else -1
                    if beat_now is None or beat_now.face is None:
                        p.facing = d
            poses.append((cid, p))
        # el que habla se dibuja al frente
        poses.sort(key=lambda cp: 1 if cp[0] == speaker else 0)

        cx, cy, z = self.camera_at(t, xs)
        vw, vh = WORLD_W / z, WORLD_H / z
        vx, vy = cx - vw / 2, cy - vh / 2

        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" width="{out_w}" height="{out_h}">']
        parts.append(background_svg(sc.location, self.style, t, cx - WORLD_W / 2))
        for pr in sc.props:
            parts.append(prop_svg(pr.name, pr.x, pr.y, pr.scale, t, pr.anim, self.style))
        for cid, p in poses:
            parts.append(character_svg(self.chars[cid], p, self.style, GROUND_Y))
        sub = self._subtitle_svg(t)
        if sub:
            parts.append(f'<g transform="translate({vx:.1f} {vy:.1f}) scale({1 / z:.4f})">{sub}</g>')
        parts.append("</svg>")
        return "".join(parts)

    def png(self, t: float, w: int, h: int) -> bytes:
        svg = self.frame_svg(t, w, h)
        kw = {"font_files": [FONT_PATH]} if FONT_PATH else {}
        return bytes(resvg_py.svg_to_bytes(svg_string=svg, width=w, height=h, **kw))


# --------------------------------------------------------------------------- clip

def render_clip(scene: Scene, characters: dict[str, CharacterSpec], style_id: str,
                envelopes: list[list[float]], out_path: str, fps: int, width: int, height: int,
                crf: int, tail: float) -> str:
    """Renderiza una escena a MP4 (sin audio). `tail` = segundos extra para la transición."""
    r = SceneRenderer(scene, characters, get_style(style_id), envelopes)
    n = int(round((scene.duration + tail) * fps))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p", "-r", str(fps),
           "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(n):
            proc.stdin.write(r.png(i / fps, width, height))
        proc.stdin.close()
        err = proc.stderr.read().decode(errors="replace")
        if proc.wait() != 0:
            raise RuntimeError(f"FFmpeg falló en la escena {scene.index}: {err[-400:]}")
    except BrokenPipeError:
        err = proc.stderr.read().decode(errors="replace")
        raise RuntimeError(f"FFmpeg cerró la entrada en la escena {scene.index}: {err[-400:]}")
    return out_path
