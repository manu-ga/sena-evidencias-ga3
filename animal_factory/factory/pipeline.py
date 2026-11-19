"""Pipeline completo: IDEA -> GUION -> VOCES -> ESCENAS -> MÚSICA -> SUBTÍTULOS -> MONTAJE -> MP4."""
from __future__ import annotations

import io
import json
import os
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from .animation.scene_renderer import SceneRenderer, render_clip, subtitle_events
from .animation.styles import get_style
from .audio.mixer import mix_soundtrack
from .audio.tts import PiperProvider, TTSProvider, speak, write_wav
from .characters.library import NARRATOR_VOICE
from .config import AUDIO_SR, QUALITY, SCENE_MAX, SCENE_MIN, TARGET_SECONDS, TRANSITION
from .models import Story
from .story.generator import generate_story
from .video.encoder import assemble, ffmpeg_available, probe, write_srt

LEAD, GAP, TAIL = 0.4, 0.22, 0.5
BASE_SPEED = 0.95      # voz algo más ágil que la predeterminada de Piper
MIN_SPEED = 0.78
Progress = Callable[[str, float, str], None]


@dataclass
class Result:
    video: Path
    srt: Path
    story_json: Path
    duration: float
    stats: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def _noop(stage: str, pct: float, msg: str) -> None:
    pass


def synth_scene_voices(story: Story, tts: TTSProvider, workdir: Path, warnings: list[str]):
    """Genera las voces de cada escena y calcula tiempos. Si la escena no cabe en 10 s, acelera un poco."""
    results = []
    for sc in story.scenes:
        speed = BASE_SPEED
        for attempt in range(3):
            clips, envs, times = [], [], []
            t = LEAD
            for k, line in enumerate(sc.lines):
                if line.speaker == "narrador":
                    voice, pitch, rate = NARRATOR_VOICE, 1.0, 1.0
                else:
                    ch = story.characters[line.speaker]
                    voice, pitch, rate = ch.voice, ch.pitch, ch.rate
                audio, env = speak(tts, line.text, voice, pitch, rate, workdir, f"s{sc.index}_l{k}", speed)
                dur = len(audio) / AUDIO_SR
                clips.append((t, audio))
                envs.append(env)
                times.append((t, t + dur))
                t += dur + GAP
            need = t - GAP + TAIL
            if need <= SCENE_MAX or attempt == 2:
                break
            speech = sum(b - a for a, b in times)
            speed = max(MIN_SPEED, speed * (SCENE_MAX - LEAD - TAIL - GAP * (len(sc.lines) - 1)) / speech)
        if need > SCENE_MAX + 0.01:
            warnings.append(f"Escena {sc.index}: la voz necesita {need:.1f} s (máx. {SCENE_MAX:.0f} s).")
        results.append((clips, envs, times, need))
    return results


def plan_durations(needs: list[float], target: float = TARGET_SECONDS) -> list[float]:
    d = [min(max(n, SCENE_MIN), max(SCENE_MAX, n)) for n in needs]
    for _ in range(200):
        s = sum(d)
        if abs(s - target) <= 0.25:
            break
        if s < target:
            idx = [i for i, x in enumerate(d) if x < SCENE_MAX - 1e-6]
            if not idx:
                break
            step = min(0.25, (target - s) / len(idx))
            for i in idx:
                d[i] = min(SCENE_MAX, d[i] + step)
        else:
            idx = [i for i, x in enumerate(d) if x > max(SCENE_MIN, needs[i]) + 1e-6]
            if not idx:
                break
            step = min(0.25, (s - target) / len(idx))
            for i in idx:
                d[i] = max(SCENE_MIN, needs[i], d[i] - step)
    return d


def _render_job(args):
    return render_clip(*args)


class Pipeline:
    def __init__(self, tts: TTSProvider | None = None, workers: int | None = None):
        self.tts = tts or PiperProvider()
        self.workers = workers or max(1, min(os.cpu_count() or 1, 8))

    def preflight(self) -> dict:
        ver = ffmpeg_available()
        voices = self.tts.available_voices()
        if not voices:
            raise RuntimeError("No hay voces instaladas. Ejecuta: python scripts/descargar_voces.py")
        return {"ffmpeg": ver, "voces": voices, "trabajadores": self.workers}

    def run(self, story: Story, outdir: Path, style: str = "cartoon", quality: str = "final",
            progress: Progress = _noop) -> Result:
        t_start = time.time()
        q = QUALITY[quality]
        outdir.mkdir(parents=True, exist_ok=True)
        work = outdir / "work"
        work.mkdir(exist_ok=True)
        warnings: list[str] = []
        stats: dict = {"calidad": quality, "estilo": style}

        progress("voces", 0.02, "Generando voces…")
        voices = synth_scene_voices(story, self.tts, work, warnings)
        needs = [v[3] for v in voices]
        durs = plan_durations(needs)
        starts = [sum(durs[:i]) for i in range(len(durs))]
        total = sum(durs) + TRANSITION
        envelopes: list[list[list[float]]] = []
        clips_audio: list[list[tuple[float, np.ndarray]]] = []
        for sc, (clips, envs, times, _), d in zip(story.scenes, voices, durs):
            sc.duration = d
            pad = (d - (times[-1][1] + TAIL)) * 0.35 if times else 0.0   # reparte el sobrante antes y después
            sc.line_times = [(a + pad, b + pad) for a, b in times]
            clips_audio.append([(a + pad, c[1]) for (a, _), c in zip(times, clips)])
            envelopes.append(envs)
        progress("voces", 0.15, "Voces listas")

        progress("audio", 0.17, "Mezclando música y efectos…")
        mix, mstats = mix_soundtrack(story.scenes, starts, total, clips_audio)
        audio_path = outdir / "audio.wav"
        write_wav(audio_path, mix, AUDIO_SR, channels=2)
        stats["audio"] = mstats
        progress("audio", 0.22, "Audio listo")

        progress("animacion", 0.23, "Dibujando y animando escenas…")
        jobs = []
        clip_paths = []
        for sc, env in zip(story.scenes, envelopes):
            cp = work / f"clip_{sc.index}.mp4"
            clip_paths.append(cp)
            jobs.append((sc, story.characters, style, env, str(cp), q["fps"], q["width"], q["height"], q["crf"], TRANSITION))
        done = 0
        # 'spawn': seguro aunque el servidor web use hilos y onnxruntime
        with ProcessPoolExecutor(max_workers=min(self.workers, len(jobs)),
                                 mp_context=multiprocessing.get_context("spawn")) as ex:
            futs = [ex.submit(_render_job, j) for j in jobs]
            for f in as_completed(futs):
                f.result()
                done += 1
                progress("animacion", 0.23 + 0.62 * done / len(jobs), f"Escenas listas: {done}/{len(jobs)}")

        progress("montaje", 0.86, "Montando el video…")
        events = []
        for sc, s0 in zip(story.scenes, starts):
            for a, b, _spk, txt in subtitle_events(sc, story.characters):
                events.append((s0 + a, s0 + b, txt))
        srt = outdir / "subtitulos.srt"
        write_srt(events, srt)
        video = outdir / "video.mp4"
        assemble(clip_paths, starts, [s.transition for s in story.scenes], audio_path, video, total, q["fps"], q["crf"])
        info = probe(video)
        stats["probe"] = {"duracion": float(info["format"]["duration"]), "bytes": int(info["format"]["size"]),
                          "streams": [{k: s.get(k) for k in ("codec_type", "codec_name", "width", "height")} for s in info["streams"]]}
        story_json = outdir / "story.json"
        story_json.write_text(json.dumps(story.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        stats["segundos_de_render"] = round(time.time() - t_start, 1)
        for p in work.glob("*"):
            p.unlink()
        work.rmdir()
        progress("listo", 1.0, "Video listo")
        return Result(video, srt, story_json, float(info["format"]["duration"]), stats, warnings)


def make_thumbnails(story: Story, style: str = "cartoon", width: int = 270) -> list[bytes]:
    """Una miniatura PNG por escena (sin audio), para el panel de escenas."""
    out = []
    st = get_style(style)
    for sc in story.scenes:
        if sc.duration <= 0:
            sc.duration = 9.0
        if not sc.line_times:
            tt, sc.line_times = 0.5, []
            for l in sc.lines:
                dur = max(0.8, len(l.text) * 0.065)
                sc.line_times.append((tt, tt + dur))
                tt += dur + GAP
        r = SceneRenderer(sc, story.characters, st, None)
        t = sc.line_times[0][0] + 0.5 if sc.line_times else 1.0
        out.append(r.png(min(t, sc.duration - 0.1), width, int(width * 16 / 9)))
    return out


def generate_and_render(idea: str, outdir: Path, hero: str | None = None, style: str = "cartoon",
                        quality: str = "final", progress: Progress = _noop) -> Result:
    story = generate_story(idea, hero_id=hero)
    return Pipeline().run(story, outdir, style=style, quality=quality, progress=progress)
