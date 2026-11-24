#!/usr/bin/env python3
"""Audio + línea de tiempo del Reel de NAWHI Ashwagandha (composición `NawhiReel`).

Uso (desde remotion_studio/):
    python scripts/build_nawhi.py --voces /ruta/voces --whisper /ruta/faster-whisper-small

Reutiliza voz, alineación por palabra y subtítulos de build_audio.py. Texto: solo lo que dice el afiche
(sin inventar resultados, precios ni dónde comprar). `tts` es la ortografía que se le da a la voz sintética.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_audio as B  # noqa: E402

ROOT = B.ROOT
SR, FPS = B.SR, B.FPS

# Cámara sobre el afiche (coordenadas de la imagen original 1086x1448): (cx, cy, zoom).
WIDE = (543, 724, 1.0)
SEGMENTS = [
    dict(id="gancho", text="¿Sientes que el día te gana?", tts="¿Sientes que el día te gana?", shots=[
        dict(kind="cam", anchor=None, props=dict(a=[540, 560, 1.0], b=[520, 470, 1.3], target=[540, 860]))]),
    dict(id="marca", text="Conoce NAWHI Ashwagandha, con Withania somnifera.",
         tts="Conoce NAWHI Ashwagandha, con Withania somnifera.", shots=[
        dict(kind="cam", anchor=None, props=dict(a=[560, 930, 1.25], b=[560, 880, 1.45], target=[540, 940], chip="NAWHI")),
        dict(kind="cam", anchor="con", props=dict(a=[520, 1130, 1.5], b=[520, 1130, 1.8], target=[540, 900], chip="ASHWAGANDHA · Withania somnifera"))]),
    dict(id="estres", text="Está pensado para acompañarte en el manejo del estrés,",
         tts="Está pensado para acompañarte en el manejo del estrés,", shots=[
        dict(kind="cam", anchor=None, props=dict(a=[560, 900, 1.15], b=[560, 860, 1.3], target=[540, 900])),
        dict(kind="cam", anchor="manejo", props=dict(a=[230, 690, 1.45], b=[200, 690, 1.75], target=[540, 860], chip="Manejo del estrés"))]),
    dict(id="sueno", text="la calidad del sueño,", tts="la calidad del sueño,", shots=[
        dict(kind="cam", anchor=None, props=dict(a=[870, 740, 1.45], b=[900, 720, 1.75], target=[540, 860], chip="Calidad del sueño"))]),
    dict(id="calma", text="la sensación de calma", tts="la sensación de calma", shots=[
        dict(kind="cam", anchor=None, props=dict(a=[230, 1170, 1.45], b=[200, 1190, 1.75], target=[540, 900], chip="Sensación de calma"))]),
    dict(id="fatiga", text="y para sentir menos fatiga.", tts="y para sentir menos fatiga.", shots=[
        dict(kind="cam", anchor=None, props=dict(a=[930, 1190, 1.45], b=[960, 1200, 1.75], target=[540, 900], chip="Menos fatiga"))]),
    dict(id="datos", text="Son sesenta unidades masticables, de venta libre.",
         tts="Son sesenta unidades masticables, de venta libre.", shots=[
        dict(kind="cam", anchor=None, props=dict(a=[500, 1190, 1.5], b=[500, 1200, 1.9], target=[540, 880], chip="60 unidades masticables")),
        dict(kind="cam", anchor="venta", props=dict(a=[600, 1000, 1.25], b=[600, 960, 1.4], target=[540, 940], chip="VENTA LIBRE"))]),
    dict(id="cierre", text="NAWHI Ashwagandha. Cuida tu bienestar.",
         tts="NAWHI Ashwagandha. Cuida tu bienestar.", shots=[
        dict(kind="end", anchor=None, props=dict(a=[543, 700, 1.05], b=[543, 640, 1.18], target=[540, 780]))]),
]

TAIL = 1.1


def build_music(total: float, rng) -> np.ndarray:
    """Música tranquila (76 BPM): colchón de acordes, arpegio suave y un shaker casi inaudible."""
    beat = 60 / 76
    bar = 4 * beat
    prog = [([57, 60, 64], 45), ([53, 57, 60], 41), ([60, 64, 67], 48), ([55, 59, 62], 43)]
    buf = np.zeros(int((total + 1) * SR))
    th = np.arange(int(0.06 * SR)) / SR
    nz = rng.uniform(-1, 1, len(th))
    shaker = (nz - B.lp(nz, 5)) * np.exp(-60 * th)
    for b in range(int(total / bar) + 2):
        t0 = b * bar
        notes, root = prog[b % 4]
        for m in notes:
            B.put(buf, B.tone(B.f(m), bar + 0.4, "tri", a=0.5, r=0.8, k=1), t0, 0.09)
            B.put(buf, B.tone(B.f(m + 12), bar + 0.4, "sine", a=0.6, r=0.8), t0, 0.05)
        B.put(buf, B.tone(B.f(root - 12), bar, "sine", a=0.1, r=0.5), t0, 0.35)
        for s in range(8):
            m = notes[[0, 1, 2, 1, 2, 1, 0, 2][s]] + 12
            B.put(buf, B.tone(B.f(m), 0.5, "sine", a=0.006, r=0.3, decay=5), t0 + s * beat / 2, 0.11)
        for q in range(8):
            B.put(buf, shaker, t0 + q * beat / 2 + beat / 4, 0.18)
    buf = buf[: int(total * SR)]
    tt = np.arange(len(buf)) / SR
    buf *= np.clip(tt / 0.8, 0, 1) * np.clip((total - tt) / 1.6, 0, 1)
    return buf * (0.5 / (np.abs(buf).max() + 1e-9))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voces", type=Path, required=True)
    ap.add_argument("--whisper", type=Path, required=True)
    ap.add_argument("--voz", default="es_MX-claude-high")
    ap.add_argument("--escala", type=float, default=0.95, help="length_scale de Piper (mayor = más pausado)")
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    model = WhisperModel(str(a.whisper), device="cpu", compute_type="int8", cpu_threads=4)
    rng = np.random.default_rng(5)
    work = Path(tempfile.mkdtemp())

    t, clips, segs, words_all, shots_all = 0.0, [], [], [], []
    GAP = 0.12
    for si, seg in enumerate(SEGMENTS):
        audio = B.synth_voice(a.voces, a.voz, seg["tts"], a.escala, work, f"n{si}")
        wt, n_heard, n_match = B.word_times(model, audio, seg["text"])
        dur = len(audio) / SR
        words = [dict(w=w, start=round(t + s, 3), end=round(t + e, 3), segstart=(k == 0)) for k, (w, s, e) in enumerate(wt)]
        words_all += words
        clips.append((t, audio))
        segs.append(dict(id=seg["id"], text=seg["text"], start=round(t, 3), end=round(t + dur, 3)))
        cursor, starts = 0, []
        for sh in seg["shots"]:
            if sh["anchor"] is None:
                starts.append(t)
                continue
            for k in range(cursor, len(words)):
                if B.norm(words[k]["w"]) == sh["anchor"]:
                    starts.append(max(t, words[k]["start"] - 0.05))
                    cursor = k + 1
                    break
            else:
                raise SystemExit(f"No encontré la palabra ancla '{sh['anchor']}' en: {seg['text']}")
        for sh, st in zip(seg["shots"], starts):
            shots_all.append(dict(kind=sh["kind"], start=round(st, 3), props=sh["props"], seg=seg["id"]))
        t += dur + GAP
    total = t - GAP + TAIL
    for i, sh in enumerate(shots_all):
        sh["end"] = round(shots_all[i + 1]["start"] if i + 1 < len(shots_all) else total, 3)
    subs = B.make_subs(words_all)

    voice = np.zeros(int(total * SR) + SR)
    for t0, x in clips:
        B.put(voice, x, t0)
    voice = voice[: int(total * SR)]
    music = build_music(total, rng)
    env = B.lp(np.abs(voice), int(0.08 * SR))
    duck = B.lp(1.0 - 0.55 * np.clip(env / 0.05, 0, 1), int(0.3 * SR))
    music_m = music * (10 ** (-24 / 20) / (np.sqrt((music ** 2).mean()) + 1e-9)) * duck
    fx = np.zeros_like(voice)
    for sh in shots_all:
        pairs = [("whoosh", -0.2, 0.3), ("pop", 0.0, 0.4)] if sh["kind"] == "cam" else [("sparkle", 0.0, 0.5), ("whoosh", -0.2, 0.3)]
        if sh["props"].get("chip", "").startswith("60") or sh["props"].get("chip") == "VENTA LIBRE":
            pairs.append(("ding", 0.05, 0.4))
        for name, off, g in pairs:
            B.put(fx, B.get(name), sh["start"] + off, 0.5 * g)
    for s in subs:
        B.put(fx, B.get("click"), s["start"], 0.12)
    mix = voice + music_m + fx
    pk = np.abs(mix).max()
    mix = mix / pk * 0.95 if pk > 0.95 else mix
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    raw = work / "mix.wav"
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
    out = ROOT / "public" / "nawhi_audio.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-ar", str(SR), str(out)], check=True)

    tl = ROOT / "src" / "nawhi" / "timeline.json"
    tl.parent.mkdir(parents=True, exist_ok=True)
    tl.write_text(json.dumps(dict(fps=FPS, duration=round(total, 3), segments=segs, shots=shots_all, subs=subs), ensure_ascii=False, indent=1), encoding="utf-8")
    rms = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
    print(f"duración {total:.2f} s | voz {rms(voice):.1f} dBFS | música (tras ducking) {rms(music_m):.1f} | efectos {rms(fx):.1f}")
    for s in segs:
        print(f"  {s['id']:8s} {s['start']:5.2f}-{s['end']:5.2f}  {s['text']}")
    for sh in shots_all:
        print(f"    {sh['start']:5.2f}-{sh['end']:5.2f} ({sh['end'] - sh['start']:.2f}s) {sh['props'].get('chip', sh['kind'])}")
    print("subtítulos:", [(x['text']) for x in subs])


if __name__ == "__main__":
    main()
