#!/usr/bin/env python3
"""Audio + línea de tiempo del documental "¿Quién es el cuarto gigante de Sudamérica?" (composición `CuartoGigante`).

Uso (desde remotion_studio/):
    python scripts/build_gigante.py --voces /ruta/voces --whisper /ruta/faster-whisper-small

Narrador: voz sintética masculina (Piper es_MX-ald-medium, tono más grave). No es una voz clonada.
Las escenas siguen las ventanas del guion (0-10, 10-23, 23-38, 38-52, 52-70, 70-90 s).
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
TOTAL = 90.0

# --------------------------------------------------------------------------- datos verificados
# Fuentes (consulta 24/11/2026): FIFA/Coca-Cola Men's World Ranking del 18/11/2026 (vía Wikipedia, módulo
# SportsRankings/data/FIFA World Rankings); fichas de las selecciones en Wikipedia; 2026 FIFA World Cup knockout stage.
TEAMS = {
    "CHI": dict(copas=2, copas_anos="2015 · 2016", mejor_mundial="3.er puesto (1962)", mm_pts=5, mundiales=9, ranking=51),
    "PAR": dict(copas=2, copas_anos="1953 · 1979", mejor_mundial="Cuartos (2010)", mm_pts=3, mundiales=9, ranking=31),
    "PER": dict(copas=2, copas_anos="1939 · 1975", mejor_mundial="Cuartos (1970)", mm_pts=3, mundiales=5, ranking=52),
    "COL": dict(copas=1, copas_anos="2001", mejor_mundial="Cuartos (2014)", mm_pts=3, mundiales=7, ranking=10),
}


def ranking_pts(r: int) -> float:
    return 3 if r <= 10 else 2 if r <= 30 else 1 if r <= 50 else 0


def score_table():
    rows = []
    for code, d in TEAMS.items():
        parts = dict(p_copas=3 * d["copas"], p_mundial=d["mm_pts"], p_part=0.5 * d["mundiales"], p_rank=ranking_pts(d["ranking"]))
        rows.append(dict(team=code, **parts, total=sum(parts.values()), **{k: d[k] for k in ("copas", "mundiales", "ranking")}))
    rows.sort(key=lambda r: -r["total"])
    return rows


# --------------------------------------------------------------------------- guion
SCENES = [
    dict(id="gancho", window=(0.0, 10.0),
         text="Argentina, Brasil y Uruguay son los tres gigantes históricos de Sudamérica. Pero hay una pregunta que divide a todo el continente: ¿quién merece ser el cuarto grande?",
         shots=[dict(kind="giants", anchor=None, hit=True),
                dict(kind="question", anchor="pero"),
                dict(kind="four", anchor="quien", hit=True)]),
    dict(id="historias", window=(10.0, 23.0),
         text="Paraguay, con dos Copas América y leyendas como Chilavert y Santa Cruz. Perú, bicampeón continental, con genios como Cubillas y Chumpitaz. Colombia, con Valderrama, Higuita, Falcao y James. Y Chile, con Elías Figueroa, Zamorano, Salas, Alexis Sánchez y Arturo Vidal.",
         shots=[dict(kind="team", anchor=None, hit=True, props=dict(team="PAR", badge="2 COPAS AMÉRICA", players=["José Luis Chilavert", "Roque Santa Cruz"])),
                dict(kind="team", anchor="peru", hit=True, props=dict(team="PER", badge="BICAMPEÓN CONTINENTAL", players=["Teófilo Cubillas", "Héctor Chumpitaz"])),
                dict(kind="team", anchor="colombia", hit=True, props=dict(team="COL", badge="CAMPEÓN COPA AMÉRICA 2001", players=["Carlos Valderrama", "René Higuita", "Radamel Falcao", "James Rodríguez"])),
                dict(kind="team", anchor="chile", hit=True, props=dict(team="CHI", badge="BICAMPEÓN 2015 · 2016", players=["Elías Figueroa", "Iván Zamorano", "Marcelo Salas", "Alexis Sánchez", "Arturo Vidal"]))]),
    dict(id="mundiales", window=(23.0, 38.0),
         text="En los Mundiales, Chile tiene una ventaja histórica: alcanzó el tercer puesto en 1962. Colombia y Paraguay llegaron a cuartos de final. Perú también alcanzó esa instancia en 1970.",
         shots=[dict(kind="chapter", anchor=None, hit=True, props=dict(kicker="CAPÍTULO 2", title="LA BATALLA MUNDIALISTA")),
                dict(kind="podium", anchor="alcanzo", hit=True, props=dict(team="CHI", place="3.er", label="PUESTO", event="MUNDIAL 1962")),
                dict(kind="quarters", anchor="colombia", hit=True, props=dict(rows=[["COL", "2014"], ["PAR", "2010"]])),
                dict(kind="quarters", anchor="peru", hit=True, props=dict(rows=[["COL", "2014"], ["PAR", "2010"], ["PER", "1970"]]))]),
    dict(id="titulos", window=(38.0, 52.0),
         text="Chile conquistó dos Copas América consecutivas. Paraguay también tiene dos títulos. Perú suma dos y Colombia uno. Pero la grandeza no se mide solamente con trofeos: también se mide con generaciones, estrellas y actuaciones inolvidables.",
         shots=[dict(kind="bars", anchor=None, hit=True),
                dict(kind="words", anchor="pero", props=dict(lines=["LA GRANDEZA", "NO SOLO SON", "TROFEOS"])),
                dict(kind="words", anchor="generaciones", hit=True, props=dict(lines=["GENERACIONES", "ESTRELLAS", "ACTUACIONES"], gold=True))]),
    dict(id="dato", window=(52.0, 70.0),
         text="Y atención: en noviembre de 2026, Colombia regresó al top 10 del ranking FIFA, ocupando el décimo puesto. Chile también alcanzó históricamente el tercer lugar mundial, igual que Colombia. ¡La batalla está más pareja de lo que parece!",
         tts="Y atención: en noviembre de dos mil veintiséis, Colombia regresó al top diez del ranking FIFA, ocupando el décimo puesto. Chile también alcanzó históricamente el tercer lugar mundial, igual que Colombia. ¡La batalla está más pareja de lo que parece!",
         shots=[dict(kind="alert", anchor=None, hit=True, props=dict(text="EL DATO QUE CAMBIA TODO")),
                dict(kind="ranking", anchor="colombia", hit=True),
                dict(kind="history", anchor="chile", hit=True),
                dict(kind="balance", anchor="la", hit=True)]),
    dict(id="veredicto", window=(70.0, 90.0),
         text="Aplicando nuestro sistema de puntuación, Chile obtiene el cuarto puesto de esta clasificación. Pero esto no significa que la discusión esté terminada. Colombia tiene argumentos, Paraguay tiene historia y Perú tiene leyendas. Ahora queremos conocer tu opinión: ¿Chile merece ser el cuarto gigante de Sudamérica? ¿O debería ser Colombia, Paraguay o Perú? ¡Te leemos en los comentarios!",
         shots=[dict(kind="score", anchor=None, hit=True, props=dict(stage=0)),
                dict(kind="score", anchor="chile", hit=True, props=dict(stage=1)),
                dict(kind="debate", anchor="pero", props=dict(stage=0)),
                dict(kind="debate", anchor="colombia", hit=True, props=dict(stage=1)),
                dict(kind="final", anchor="ahora", hit=True)]),
]


# --------------------------------------------------------------------------- voz
def synth(voces: Path, text: str, scale: float, work: Path, tag: str, voice="es_MX-ald-medium", pitch=0.9) -> np.ndarray:
    from piper import PiperVoice, SynthesisConfig
    if not hasattr(synth, "v"):
        synth.v = PiperVoice.load(str(voces / f"{voice}.onnx"))
    raw, fin = work / f"{tag}_raw.wav", work / f"{tag}.wav"
    with wave.open(str(raw), "wb") as w:
        synth.v.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=scale))
    with wave.open(str(raw)) as w:
        sr = w.getframerate()
    # tono más grave sin cambiar la duración + compresión de locutor
    af = (f"asetrate={sr * pitch:.0f},aresample=48000,atempo={1 / pitch:.4f},highpass=f=70,"
          "equalizer=f=140:t=q:w=1:g=3,acompressor=threshold=-20dB:ratio=3.5:attack=4:release=90")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ac", "1", "-ar", str(SR), str(fin)], check=True)
    with wave.open(str(fin)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(SR * 0.01)
    n = len(x) // hop
    e = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    idx = np.where(e > e.max() * 0.03)[0]
    x = x[max(0, idx[0] * hop - int(0.02 * SR)): min(len(x), (idx[-1] + 1) * hop + int(0.03 * SR))]
    return x * (0.17 / (np.sqrt((x ** 2).mean()) + 1e-9))


# --------------------------------------------------------------------------- música y estadio
def epic_music(total: float, intensity, rng) -> np.ndarray:
    """Música cinematográfica deportiva (92 BPM, Re menor): ostinato de cuerdas, timbales, metales."""
    beat = 60 / 92
    bar = 4 * beat
    prog = [([62, 65, 69], 50), ([58, 62, 65], 46), ([53, 57, 60], 41), ([60, 64, 67], 48)]   # Dm Bb F C
    buf = np.zeros(int((total + 2) * SR))
    t_ = np.arange(int(0.9 * SR)) / SR
    timp = np.sin(2 * np.pi * np.cumsum(70 - 22 * t_) / SR) * np.exp(-4.5 * t_) + B.lp(rng.uniform(-1, 1, len(t_)), 30) * 1.5 * np.exp(-25 * t_)
    tk = np.arange(int(0.35 * SR)) / SR
    taiko = np.sin(2 * np.pi * np.cumsum(110 - 60 * tk / 0.35) / SR) * np.exp(-9 * tk)
    for b in range(int(total / bar) + 2):
        t0 = b * bar
        lvl = intensity(t0)
        notes, root = prog[b % 4]
        for m in notes:                                           # colchón de cuerdas
            B.put(buf, B.tone(B.f(m - 12), bar + 0.3, "saw", a=0.3, r=0.5, k=22), t0, 0.05 + 0.03 * lvl)
        for s in range(8):                                        # ostinato
            m = notes[[0, 0, 2, 0, 1, 0, 2, 1][s]] - 12
            B.put(buf, B.tone(B.f(m), beat * 0.45, "saw", a=0.006, r=0.06, k=12), t0 + s * beat / 2, 0.07 + 0.06 * lvl)
        B.put(buf, B.tone(B.f(root - 12), bar, "sine", a=0.05, r=0.3), t0, 0.32)
        B.put(buf, timp, t0, 0.55 + 0.35 * lvl)
        B.put(buf, timp, t0 + 2 * beat, 0.35 + 0.3 * lvl)
        if lvl > 0.45:
            for q in (0, 1.5, 2.5, 3):
                B.put(buf, taiko, t0 + q * beat, 0.35 * lvl)
        if lvl > 0.7:                                             # metales
            for m in notes:
                B.put(buf, B.tone(B.f(m), beat * 1.5, "saw", a=0.04, r=0.3, k=7), t0, 0.05 * lvl)
    return buf[: int(total * SR)]


def crowd(total: float, rng) -> np.ndarray:
    n = int(total * SR)
    x = rng.uniform(-1, 1, n)
    band = B.lp(x, 6) - B.lp(x, 40)                              # banda media: murmullo de estadio
    mod = B.lp(rng.uniform(0.6, 1.0, n // 2400 + 2).repeat(2400)[:n], 4800)
    return band * mod * 2.2


def roar(d: float, rng) -> np.ndarray:
    n = int(d * SR)
    x = rng.uniform(-1, 1, n)
    t = np.arange(n) / SR
    env = np.clip(t / 0.25, 0, 1) * np.exp(-1.6 * np.clip(t - 0.25, 0, None))
    return (B.lp(x, 4) - B.lp(x, 26)) * env * 3


def whistle(rng) -> np.ndarray:
    out = []
    for d in (0.22, 0.5):
        t = np.arange(int(d * SR)) / SR
        f = 2950 + 90 * np.sign(np.sin(2 * np.pi * 34 * t))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(t / 0.01, 0, 1) * np.clip((d - t) / 0.02, 0, 1)
        out += [s * 0.5, np.zeros(int(0.08 * SR))]
    return np.concatenate(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voces", type=Path, required=True)
    ap.add_argument("--whisper", type=Path, required=True)
    ap.add_argument("--escala", type=float, default=0.86)
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    model = WhisperModel(str(a.whisper), device="cpu", compute_type="int8", cpu_threads=4)
    rng = np.random.default_rng(9)
    work = Path(tempfile.mkdtemp())

    shots, words_all, clips, segs = [], [], [], []
    LEAD, GAP, TAILS = 0.25, 0.3, 1.8
    # 1.ª pasada: duración natural; 2.ª: un solo ritmo para que toda la narración quepa en 90 s
    nat = [len(synth(a.voces, sc.get("tts", sc["text"]), a.escala, work, f"p{i}")) / SR for i, sc in enumerate(SCENES)]
    target = TOTAL - LEAD - GAP * (len(SCENES) - 1) - TAILS
    scale = min(0.95, max(0.68, a.escala * target / sum(nat)))
    for attempt in range(3):
        shots, words_all, clips, segs = [], [], [], []
        t_prev_end = 0.0
        for si, sc in enumerate(SCENES):
            audio = synth(a.voces, sc.get("tts", sc["text"]), scale, work, f"g{si}")
            dur = len(audio) / SR
            start = LEAD if si == 0 else t_prev_end + GAP
            wt, *_ = B.word_times(model, audio, sc["text"])
            words = [dict(w=w, start=round(start + s, 3), end=round(start + e, 3), segstart=(k == 0)) for k, (w, s, e) in enumerate(wt)]
            words_all += words
            clips.append((start, audio))
            t_prev_end = start + dur
            segs.append(dict(id=sc["id"], start=round(start, 3), end=round(start + dur, 3), window=list(sc["window"]), scale=round(scale, 3)))
            cursor = 0
            scene_start = 0.0 if si == 0 else start - 0.15
            for sh in sc["shots"]:
                if sh["anchor"] is None:
                    st = scene_start
                else:
                    for k in range(cursor, len(words)):
                        if B.norm(words[k]["w"]) == sh["anchor"]:
                            st = words[k]["start"] - 0.08
                            cursor = k + 1
                            break
                    else:
                        raise SystemExit(f"Ancla '{sh['anchor']}' no encontrada en: {sc['text']}")
                shots.append(dict(kind=sh["kind"], start=round(max(st, scene_start), 3), hit=sh.get("hit", False),
                                  props=sh.get("props", {}), scene=sc["id"]))
        speech = sum(len(x) for _, x in clips) / SR
        if abs(t_prev_end + TAILS - TOTAL) <= 0.25 or attempt == 2:
            break
        scale = min(0.95, max(0.66, scale * (speech - (t_prev_end + TAILS - TOTAL)) / speech))
    total = round(t_prev_end + TAILS, 3)
    for i, sh in enumerate(shots):
        sh["end"] = round(shots[i + 1]["start"] if i + 1 < len(shots) else total, 3)
    subs = B.make_subs(words_all)

    # ------------------------------------------------------------------ mezcla
    voice = np.zeros(int(total * SR) + SR)
    for t0, x in clips:
        B.put(voice, x, t0)
    voice = voice[: int(total * SR)]

    def intensity(t):                              # la música crece hacia el veredicto
        return 0.35 if t < 10 else 0.5 if t < 38 else 0.6 if t < 52 else 0.75 if t < 70 else 0.9
    music = epic_music(total, intensity, rng)
    env = B.lp(np.abs(voice), int(0.08 * SR))
    duck = B.lp(1.0 - 0.6 * np.clip(env / 0.05, 0, 1), int(0.3 * SR))
    music = music * (10 ** (-21 / 20) / (np.sqrt((music ** 2).mean()) + 1e-9)) * duck
    fx = np.zeros_like(voice)
    amb = crowd(total, rng)
    fx += amb * (10 ** (-38 / 20) / (np.sqrt((amb ** 2).mean()) + 1e-9)) * (0.6 + 0.4 * duck)
    B.put(fx, whistle(rng), 0.05, 0.35)
    for sh in shots:
        if sh["hit"]:
            B.put(fx, B.get("boom"), sh["start"], 0.42)
            B.put(fx, B.get("whoosh"), sh["start"] - 0.25, 0.25)
        else:
            B.put(fx, B.get("whoosh"), sh["start"] - 0.25, 0.22)
        if sh["kind"] in ("four", "final"):
            B.put(fx, roar(3.5, rng), sh["start"], 0.16)
    B.put(fx, roar(4.5, rng), total - 5.5, 0.14)
    mix = voice + music + fx
    tt = np.arange(len(mix)) / SR
    mix *= np.clip((total - tt) / 1.5, 0, 1)
    pk = np.abs(mix).max()
    mix = mix / pk * 0.95 if pk > 0.95 else mix
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    raw = work / "mix.wav"
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
    out = ROOT / "public" / "gigante_audio.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", str(SR), str(out)], check=True)

    data = dict(fps=FPS, duration=round(total, 3), segments=segs, shots=shots, subs=subs, score=score_table(), teams=TEAMS,
                fuentes="FIFA/Coca-Cola Men's World Ranking (18/11/2026) y Wikipedia (consulta 24/11/2026)")
    tl = ROOT / "src" / "gigante" / "timeline.json"
    tl.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    rms = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
    print(f"duración {total:.2f} s | voz {rms(voice):.1f} | música {rms(music):.1f} | efectos {rms(fx):.1f} dBFS")
    for s in segs:
        print(f"  {s['id']:10s} voz {s['start']:5.2f}-{s['end']:5.2f}  ventana {s['window']}  escala {s['scale']}")
    d = [x["end"] - x["start"] for x in shots]
    print(f"planos {len(shots)} | min {min(d):.2f} máx {max(d):.2f} s")
    for x in shots:
        print(f"    {x['start']:5.2f}-{x['end']:5.2f} {x['kind']:9s} {x['props'].get('team', '')}")
    print("puntuación:", [(r['team'], r['total']) for r in score_table()])


if __name__ == "__main__":
    main()
