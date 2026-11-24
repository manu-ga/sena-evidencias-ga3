"""Montaje final con FFmpeg: transiciones entre escenas, audio y exportación H.264/AAC."""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..config import TRANSITION

XFADE_OK = {"fade", "fadeblack", "slideleft", "slideright", "wipeleft", "circleopen", "zoomin"}


class EncodeError(RuntimeError):
    pass


def ffmpeg_available() -> str:
    """Devuelve la versión de FFmpeg o lanza error si no está instalado."""
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=20)
    except FileNotFoundError as e:
        raise EncodeError("FFmpeg no está instalado. Instálalo con: apt-get install ffmpeg") from e
    if r.returncode != 0:
        raise EncodeError("FFmpeg no responde correctamente.")
    return r.stdout.splitlines()[0]


def assemble(clips: list[Path], starts: list[float], transitions: list[str], audio: Path,
             out_mp4: Path, total: float, fps: int, crf: int) -> None:
    n = len(clips)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for c in clips:
        cmd += ["-i", str(c)]
    cmd += ["-i", str(audio)]
    if n == 1:
        vmap = "0:v"
        graph = None
    else:
        parts, prev = [], "[0:v]"
        for i in range(1, n):
            tr = transitions[i] if transitions[i] in XFADE_OK else "fade"
            lab = f"[v{i}]"
            parts.append(f"{prev}[{i}:v]xfade=transition={tr}:duration={TRANSITION}:offset={starts[i]:.3f}{lab}")
            prev = lab
        graph, vmap = ";".join(parts), prev
    if graph:
        cmd += ["-filter_complex", graph]
    cmd += ["-map", vmap, "-map", f"{n}:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
            "-t", f"{total:.3f}", "-movflags", "+faststart", str(out_mp4)]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise EncodeError(f"FFmpeg falló en el montaje: {r.stderr.decode(errors='replace')[-500:]}")


def probe(path: Path) -> dict:
    import json
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,duration",
                        "-show_entries", "format=duration,size", "-of", "json", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        raise EncodeError(f"ffprobe no pudo leer {path}: {r.stderr[-200:]}")
    return json.loads(r.stdout)


def _ts(t: float) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}".replace(",1000", ",999")


def write_srt(events: list[tuple[float, float, str]], path: Path) -> None:
    lines = []
    for i, (a, b, txt) in enumerate(events, start=1):
        lines += [str(i), f"{_ts(a)} --> {_ts(b)}", txt, ""]
    path.write_text("\n".join(lines), encoding="utf-8")
