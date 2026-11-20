#!/usr/bin/env python3
"""Genera el audio (voz Piper + música sintética + micro-SFX) y la línea de tiempo (timeline.json)
del video "Ads de dropshipping vs Trading".

Uso (desde remotion_studio/):
    python scripts/build_audio.py --voces /ruta/a/voces --whisper /ruta/a/faster-whisper-small

Requiere: piper-tts, faster-whisper, numpy y ffmpeg. Los tiempos por palabra salen de Whisper
(Piper no los entrega con estas voces); el texto es el del guion, no el que "escucha" Whisper.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / "animal_factory"))
from factory.audio import sfx as SFX  # noqa: E402  (efectos sintetizados, 44,1 kHz)

SR = 48000
FPS = 30
GAP = 0.08          # pausa entre frases (< 0.12 s, regla "cero aire muerto")
TAIL = 0.7          # cola final con música para sostener el CTA

# ------------------------------------------------------------------ guion + planos
# anchor = palabra (sin tildes) donde empieza el plano; None = inicio de la frase.
SEGMENTS = [
    dict(id="gancho", text="¿Meter plata en anuncios de dropshipping o arriesgarla en trading? ¡No elijas a ciegas!", shots=[
        dict(kind="slam", anchor=None, props=dict(title="¿DÓNDE VA TU PLATA?", left="ADS", leftSub="DROPSHIPPING", right="TRADING")),
        dict(kind="zoomside", anchor="arriesgarla", props=dict(side="trading", label="TRADING", sub="RIESGO REAL")),
        dict(kind="keyword", anchor="no", props=dict(text="NO ELIJAS A CIEGAS", side="red", tag="¡ATENCIÓN!"))]),
    dict(id="filtro", text="En treinta segundos te muestro qué exige cada uno para no quemar tu capital.", shots=[
        dict(kind="clockcols", anchor=None, props=dict(seconds=30)),
        dict(kind="keyword", anchor="quemar", props=dict(text="QUEMAR TU CAPITAL", side="red", tag="EVÍTALO"))]),
    dict(id="primero", text="Primero: en anuncios de dropshipping ganas o pierdes según el creativo, el ángulo y la conversión; si el anuncio no conecta, el tráfico se va en seco.", shots=[
        dict(kind="funnel", anchor=None, props=dict(label="01 · ADS", tags=["CREATIVO", "CONVERSIÓN"])),
        dict(kind="duo", anchor="ganas", props=dict(a="GANAS", b="PIERDES", side="ads")),
        dict(kind="triple", anchor="creativo", props=dict(words=["CREATIVO", "ÁNGULO", "CONVERSIÓN"], side="ads", tag="ADS")),
        dict(kind="noconnect", anchor="si", props=dict(text="NO CONECTA")),
        dict(kind="leak", anchor="trafico", props=dict(text="EL TRÁFICO SE VA EN SECO"))]),
    dict(id="segundo", text="Segundo: en trading ganas o pierdes según lectura de mercado, gestión de riesgo y disciplina; un mal lote o una emoción te borra la cuenta.", shots=[
        dict(kind="candles", anchor=None, props=dict(label="02 · TRADING", tags=["RIESGO", "CONTROL EMOCIONAL"])),
        dict(kind="keyword", anchor="lectura", props=dict(text="LECTURA DE MERCADO", side="trading", tag="TRADING")),
        dict(kind="triple", anchor="gestion", props=dict(words=["GESTIÓN DE RIESGO", "DISCIPLINA"], side="trading", tag="TRADING")),
        dict(kind="crash", anchor="un", props=dict(text="UN MAL LOTE", text2="UNA EMOCIÓN", sub="TE BORRA LA CUENTA"))]),
    dict(id="tercero", text="Tercero: en ads necesitas validar producto y oferta; en trading necesitas reglas estrictas y paciencia en pantalla.", shots=[
        dict(kind="check", anchor=None, props=dict(stage=0, label="03 · COMPARA", left="PRUEBA DE OFERTA", right="EJECUCIÓN Y RIESGO")),
        dict(kind="check", anchor="validar", props=dict(stage=1, label="03 · COMPARA", left="PRUEBA DE OFERTA", right="EJECUCIÓN Y RIESGO")),
        dict(kind="check", anchor="trading", props=dict(stage=2, label="03 · COMPARA", left="PRUEBA DE OFERTA", right="EJECUCIÓN Y RIESGO")),
        dict(kind="keyword", anchor="paciencia", props=dict(text="PACIENCIA EN PANTALLA", side="trading", tag="TRADING"))]),
    dict(id="error", text="El error de casi todos es saltar al que ve más fácil y meter dinero sin medir cuánto puede perder.", shots=[
        dict(kind="alert", anchor=None, props=dict(text="EL ERROR MÁS CARO")),
        dict(kind="keyword", anchor="saltar", props=dict(text="SALTAR AL MÁS FÁCIL", side="red", tag="ERROR #1")),
        dict(kind="strike", anchor="meter", props=dict(text="Entrar sin plan de pérdida"))]),
    dict(id="cierre", text="Guarda este video si estás decidiendo tu próximo paso y comenta DIFERENCIA para desglosar cuál encaja mejor contigo.", shots=[
        dict(kind="cta", anchor=None, props=dict(stage="guardar")),
        dict(kind="cta", anchor="comenta", props=dict(stage="comenta")),
        dict(kind="cta", anchor="cual", props=dict(stage="final"))]),
]

ADS_WORDS = {"anuncios", "anuncio", "ads", "dropshipping", "creativo", "angulo", "conversion", "trafico", "producto", "oferta", "validar"}
TRADING_WORDS = {"arriesgarla", "trading", "lectura", "mercado", "gestion", "riesgo", "disciplina", "lote", "emocion", "cuenta", "reglas", "estrictas", "paciencia", "pantalla"}
EMPHASIS = {"diferencia"}


def norm(w: str) -> str:
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


# ------------------------------------------------------------------ voz
def synth_voice(voz_dir: Path, voice: str, text: str, scale: float, workdir: Path, tag: str) -> np.ndarray:
    from piper import PiperVoice, SynthesisConfig
    if not hasattr(synth_voice, "cache"):
        synth_voice.cache = {}
    if voice not in synth_voice.cache:
        synth_voice.cache[voice] = PiperVoice.load(str(voz_dir / f"{voice}.onnx"))
    raw, fin = workdir / f"{tag}_raw.wav", workdir / f"{tag}.wav"
    with wave.open(str(raw), "wb") as w:
        synth_voice.cache[voice].synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=scale))
    # 48 kHz, filtro de graves y compresión suave para que suene "de creador"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    "highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=4:release=80,aresample=48000",
                    "-ac", "1", "-ar", str(SR), str(fin)], check=True)
    with wave.open(str(fin)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    # recorta silencios de los extremos (deja 25 ms)
    hop = int(SR * 0.01)
    n = len(x) // hop
    e = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    idx = np.where(e > e.max() * 0.03)[0]
    a, b = max(0, idx[0] * hop - int(0.025 * SR)), min(len(x), (idx[-1] + 1) * hop + int(0.025 * SR))
    x = x[a:b]
    return x * (0.16 / (np.sqrt((x ** 2).mean()) + 1e-9))      # nivel parejo entre frases


def word_times(model, audio48: np.ndarray, text: str) -> list[tuple[str, float, float]]:
    """Tiempos por palabra: Whisper mide, el guion manda (alineación por secuencia)."""
    n = int(len(audio48) * 16000 / SR)
    a16 = np.interp(np.linspace(0, len(audio48) - 1, n), np.arange(len(audio48)), audio48).astype(np.float32)
    segs, _ = model.transcribe(a16, language="es", word_timestamps=True, vad_filter=False, beam_size=5,
                               condition_on_previous_text=False)
    heard = [(norm(w.word), w.start, w.end) for s in segs for w in (s.words or []) if norm(w.word)]
    known = text.split()
    kn = [norm(w) for w in known]
    dur = len(audio48) / SR
    # alineación por letras: cada letra "oída" recibe un instante (reparto lineal dentro de su palabra);
    # así sirve aunque Whisper parta, una o cambie palabras.
    H, ht0, ht1 = "", [], []
    for w, s0, e0 in heard:
        for k, ch in enumerate(w):
            H += ch
            ht0.append(s0 + (e0 - s0) * k / len(w))
            ht1.append(s0 + (e0 - s0) * (k + 1) / len(w))
    K = "".join(kn)
    kt0 = np.full(len(K), np.nan)
    kt1 = np.full(len(K), np.nan)
    sm = difflib.SequenceMatcher(None, K, H, autojunk=False)
    n_match = 0
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            kt0[blk.a + k], kt1[blk.a + k] = ht0[blk.b + k], ht1[blk.b + k]
            n_match += 1
    idx = np.where(~np.isnan(kt0))[0]
    if len(idx) == 0:
        raise SystemExit("Whisper no reconoció nada de la frase")
    allx = np.arange(len(K))
    kt0 = np.interp(allx, idx, kt0[idx])
    kt1 = np.interp(allx, idx, kt1[idx])
    out, pos, prev = [], 0, 0.0
    for w, wn in zip(known, kn):
        s_, e_ = float(kt0[pos]), float(kt1[pos + len(wn) - 1]) if wn else float(kt1[min(pos, len(K) - 1)])
        pos += len(wn)
        s_ = max(s_, prev)
        e_ = max(e_, s_ + 0.06)
        out.append((w, s_, e_))
        prev = s_
    return out, len(K), n_match


# ------------------------------------------------------------------ subtítulos
def make_subs(words: list[dict]) -> list[dict]:
    """2 a 4 palabras por golpe; corta en puntuación. El color sigue al lado del que se habla
    (naranja = ads, cian = trading) y vuelve a blanco al terminar cada oración."""
    subs, cur, state = [], [], "white"

    def flush(side):
        nonlocal cur
        if cur:
            subs.append(dict(text=" ".join(w["w"] for w in cur).strip(), start=cur[0]["start"], end=cur[-1]["end"],
                             side=side, emph=any(norm(w["w"]) in EMPHASIS for w in cur)))
            cur = []

    for w in words:
        n = norm(w["w"])
        if w.get("segstart"):
            flush(state)
            state = "white"
        new = "ads" if n in ADS_WORDS else "trading" if n in TRADING_WORDS else None
        if new and new != state:
            if len(cur) >= 2:
                flush(state)                  # el color cambia al llegar la palabra del otro lado
            state = new                       # con 0-1 palabras previas, ese trozo adopta el color nuevo
        cur.append(w)
        sentence_end = bool(re.search(r"[.?!]$", w["w"]))
        if len(cur) >= 4 or (re.search(r"[.,?!;:]$", w["w"]) and len(cur) >= 2) or sentence_end:
            flush(state)
            if sentence_end:
                state = "white"
    flush(state)

    def dur(x): return x["end"] - x["start"]
    changed = True
    while changed:                            # nada de parpadeos: trozos < 0.38 s o de 1 palabra se funden con un vecino
        changed = False
        for i, x in enumerate(subs):
            short = dur(x) < 0.38 or len(x["text"].split()) == 1
            if not short:
                continue
            prev_ok = (i > 0 and not re.search(r"[.?!]$", subs[i - 1]["text"]) and len(subs[i - 1]["text"].split()) + len(x["text"].split()) <= 4
                       and x["start"] - subs[i - 1]["end"] < 0.4)
            next_ok = (i + 1 < len(subs) and not re.search(r"[.?!]$", x["text"]) and len(subs[i + 1]["text"].split()) + len(x["text"].split()) <= 4
                       and subs[i + 1]["start"] - x["end"] < 0.4)
            if next_ok:
                y = subs[i + 1]
                y["text"] = x["text"] + " " + y["text"]; y["start"] = x["start"]; y["emph"] = y["emph"] or x["emph"]
                subs.pop(i); changed = True; break
            if prev_ok:
                y = subs[i - 1]
                y["text"] += " " + x["text"]; y["end"] = x["end"]; y["emph"] = y["emph"] or x["emph"]
                subs.pop(i); changed = True; break
    for x, y in zip(subs, subs[1:]):          # continuidad: aguanta hasta el siguiente (máx. 0.25 s), sin solaparse
        x["end"] = min(y["start"], x["end"] + 0.25) if y["start"] > x["end"] else y["start"]
    return subs


# ------------------------------------------------------------------ audio: música + efectos
def lp(x, k): return x if k <= 1 else np.convolve(x, np.ones(k) / k, mode="same")
def f(m): return 440.0 * 2 ** ((m - 69) / 12)


def tone(freq, d, kind="tri", a=0.005, r=0.08, decay=0.0, k=1):
    n = int(d * SR)
    t = np.arange(n) / SR
    ph = (freq * t) % 1.0
    w = {"sine": np.sin(2 * np.pi * ph), "tri": 2 * np.abs(2 * ph - 1) - 1, "saw": 2 * ph - 1,
         "sq": np.sign(np.sin(2 * np.pi * ph)) * 0.7}[kind]
    env = np.ones(n)
    na, nr = max(1, min(n, int(a * SR))), max(1, min(n, int(r * SR)))
    env[:na] = np.linspace(0, 1, na)
    env[-nr:] *= np.linspace(1, 0, nr)
    if decay:
        env *= np.exp(-decay * t)
    return lp(w, k) * env


def put(buf, x, t, g=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i + len(x) <= 0:
        return
    j0 = max(0, -i)
    i = max(0, i)
    j = min(len(buf), i + len(x) - j0)
    buf[i:j] += x[j0:j0 + (j - i)] * g


def rs(x, sr_in=44100):
    n = int(len(x) * SR / sr_in)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def build_music(total: float, rng) -> np.ndarray:
    BPM = 108
    beat = 60 / BPM
    bar = 4 * beat
    prog = [([57, 60, 64], 45), ([53, 57, 60], 41), ([55, 60, 64], 48), ([55, 59, 62], 43)]   # Am F C G
    buf = np.zeros(int((total + 1) * SR))
    t_ = np.arange(int(0.22 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(120 - 80 * np.minimum(t_ / 0.2, 1)) / SR) * np.exp(-13 * t_)
    tc = np.arange(int(0.16 * SR)) / SR
    clap = (rng.uniform(-1, 1, len(tc)) * np.exp(-26 * tc)) * 0.7
    th = np.arange(int(0.045 * SR)) / SR
    nz = rng.uniform(-1, 1, len(th))
    hat = (nz - lp(nz, 6)) * np.exp(-85 * th)
    for b in range(int(total / bar) + 2):
        t0 = b * bar
        notes, root = prog[b % 4]
        full = b >= 1                                   # arranque inmediato; capas completas desde el 2.º compás
        for m in notes:
            put(buf, tone(f(m), bar + 0.15, "saw", a=0.12, r=0.3, k=18), t0, 0.035)          # pad
        for s in range(8):                                                                   # bajo en corcheas
            put(buf, tone(f(root - 12 if s % 2 == 0 else root - 5), beat * 0.42, "tri", a=0.004, r=0.05), t0 + s * beat / 2, 0.30)
        for s in range(16):                                                                  # arpegio pluck
            m = notes[[0, 1, 2, 1][s % 4]] + 12 + (12 if s % 8 >= 6 else 0)
            put(buf, tone(f(m), 0.22, "sq", a=0.003, r=0.12, decay=10, k=6), t0 + s * beat / 4, 0.045 if full else 0.03)
        for q in range(4):
            tb = t0 + q * beat
            put(buf, kick, tb, 0.85)
            if q in (1, 3):
                put(buf, clap, tb, 0.55)
            put(buf, hat, tb + beat / 2, 0.32)
            if full:
                put(buf, hat, tb + beat / 4, 0.14)
                put(buf, hat, tb + 3 * beat / 4, 0.14)
    buf = buf[: int(total * SR)]
    tt = np.arange(len(buf)) / SR
    buf *= np.clip((total - tt) / 0.8, 0, 1)             # cierre corto
    return buf * (0.5 / (np.abs(buf).max() + 1e-9))


def click_sfx():
    n = int(0.012 * SR)
    r = np.random.default_rng(3).uniform(-1, 1, n)
    return (r - lp(r, 5)) * np.exp(-np.arange(n) / (SR * 0.003))


def tick_sfx():
    return tone(2600, 0.02, "sine", a=0.001, r=0.012) * 0.8


def get(name):
    return {"click": click_sfx(), "tick": tick_sfx()}.get(name) if name in ("click", "tick") else rs(SFX.get_sfx(name))


# (efectos por tipo de plano: (nombre, desfase_s, ganancia))
SHOT_SFX = {
    "slam": [("whoosh", -0.22, 0.9), ("boom", 0.0, 1.0), ("crash", 0.02, 0.35)],
    "zoomside": [("whoosh", -0.2, 0.8), ("pop", 0.1, 0.6)],
    "keyword": [("whoosh", -0.2, 0.5), ("pop", 0.0, 0.75)],
    "clockcols": [("whoosh", -0.2, 0.8), ("pop", 0.0, 0.6)],
    "duo": [("whoosh", -0.2, 0.5), ("pop", 0.0, 0.7)],
    "triple": [("whoosh", -0.2, 0.6), ("pop", 0.0, 0.75)],
    "noconnect": [("thud", 0.0, 0.6), ("gasp", -0.05, 0.5)],
    "funnel": [("whoosh", -0.2, 0.8), ("pop", 0.1, 0.6)],
    "leak": [("thud", 0.0, 0.6), ("whoosh", -0.15, 0.5)],
    "candles": [("whoosh", -0.2, 0.8), ("pop", 0.1, 0.6)],
    "crash": [("crash", 0.0, 0.6), ("boom", 0.0, 0.8)],
    "check": [("ding", 0.0, 0.55), ("pop", 0.0, 0.6)],
    "alert": [("siren", 0.0, 0.45), ("boom", 0.0, 0.8)],
    "strike": [("click", 0.0, 1.0), ("boom", 0.05, 0.6), ("whoosh", -0.15, 0.6)],
    "cta": [("pop", 0.0, 0.8), ("sparkle", 0.05, 0.5)],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voces", type=Path, required=True)
    ap.add_argument("--whisper", type=Path, required=True)
    ap.add_argument("--voz", default="es_MX-claude-high")
    ap.add_argument("--escala", type=float, default=0.66, help="length_scale de Piper (menor = más rápido)")
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    model = WhisperModel(str(a.whisper), device="cpu", compute_type="int8", cpu_threads=4)
    rng = np.random.default_rng(7)
    work = Path(tempfile.mkdtemp())

    t = 0.0
    clips, segs, words_all, shots_all = [], [], [], []
    for si, seg in enumerate(SEGMENTS):
        audio = synth_voice(a.voces, a.voz, seg["text"], a.escala, work, f"s{si}")
        wt, n_heard, n_match = word_times(model, audio, seg["text"])
        dur = len(audio) / SR
        words = [dict(w=w, start=round(t + s, 3), end=round(t + e, 3), segstart=(k == 0)) for k, (w, s, e) in enumerate(wt)]
        words_all += words
        clips.append((t, audio))
        segs.append(dict(id=seg["id"], text=seg["text"], start=round(t, 3), end=round(t + dur, 3), words=len(words),
                         reconocidas=f"{100 * n_match // max(1, n_heard)} % de letras"))
        # planos: cada uno empieza en su palabra ancla
        cursor = 0
        starts = []
        for sh in seg["shots"]:
            if sh["anchor"] is None:
                starts.append(t)
                continue
            for k in range(cursor, len(words)):
                if norm(words[k]["w"]) == sh["anchor"]:
                    starts.append(max(t, words[k]["start"] - 0.04))
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
    subs = make_subs(words_all)
    for s in subs:
        s["start"], s["end"] = round(s["start"], 3), round(s["end"], 3)

    # ---------------------------------------------------------- mezcla
    voice = np.zeros(int(total * SR) + SR)
    for t0, x in clips:
        put(voice, x, t0)
    voice = voice[: int(total * SR)]
    music = build_music(total, rng)
    env = lp(np.abs(voice), int(0.06 * SR))
    duck = 1.0 - 0.62 * np.clip(env / 0.05, 0, 1)
    duck = lp(duck, int(0.22 * SR))
    music_m = music * (10 ** (-23 / 20) / (np.sqrt((music ** 2).mean()) + 1e-9)) * duck   # -23 dBFS antes del ducking; nunca en silencio
    fx = np.zeros_like(voice)
    sfx_log = []
    for sh in shots_all:
        for name, off, g in SHOT_SFX[sh["kind"]]:
            x = get(name)
            if name == "siren":
                x = x[: int(0.7 * SR)].copy()
                x[-int(0.1 * SR):] *= np.linspace(1, 0, int(0.1 * SR))
            put(fx, x, sh["start"] + off, 0.55 * g)
            sfx_log.append((round(sh["start"] + off, 2), name))
        if sh["kind"] == "clockcols":                      # tictac del contador 0:30 y filas de las columnas
            for k in range(9):
                put(fx, get("tick"), sh["start"] + 0.12 + k * 0.09, 0.35)
            for k in range(6):
                put(fx, get("pop"), sh["start"] + 1.0 + k * 0.14, 0.25)
        if sh["kind"] in ("triple", "duo"):                # un golpe por palabra
            n_w = len(sh["props"].get("words", [0, 0])) if sh["kind"] == "triple" else 2
            for k in range(1, n_w):
                put(fx, get("pop"), sh["start"] + (sh["end"] - sh["start"]) * k / n_w, 0.5)
        if sh["kind"] == "candles":
            for k in range(8):
                put(fx, get("tick"), sh["start"] + 0.2 + k * 0.12, 0.3)
    for s in subs:                                         # micro-click al aparecer cada texto
        put(fx, get("click"), s["start"], 0.22)
    mix = voice + music_m + fx
    pk = np.abs(mix).max()
    mix = mix / pk * 0.95 if pk > 0.95 else mix
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    raw = work / "mix.wav"
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
    out_wav = ROOT / "public" / "ads_trading_audio.wav"
    out_wav.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", str(SR), str(out_wav)], check=True)

    rms = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
    timeline = dict(fps=FPS, duration=round(total, 3), voice=a.voz, escala=a.escala, segments=segs, shots=shots_all, subs=subs)
    tl = ROOT / "src" / "ads_trading" / "timeline.json"
    tl.parent.mkdir(parents=True, exist_ok=True)
    tl.write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"duración total {total:.2f} s | voz hablada {sum(len(x) for _, x in clips) / SR:.1f} s")
    print(f"niveles dBFS: voz {rms(voice):.1f} | música (tras ducking) {rms(music_m):.1f} | efectos {rms(fx):.1f}")
    for s in segs:
        print(f"  {s['id']:8s} {s['start']:6.2f}-{s['end']:6.2f}  {s['reconocidas']}")
    d = [b["end"] - b["start"] for b in shots_all]
    print(f"planos: {len(shots_all)} | duración mín {min(d):.2f} máx {max(d):.2f} media {sum(d) / len(d):.2f} s | subtítulos: {len(subs)}")
    for sh in shots_all:
        print(f"    {sh['start']:6.2f}-{sh['end']:6.2f} ({sh['end'] - sh['start']:.2f}s) {sh['kind']:9s} {sh['props'].get('text', '')}")
    print(f"huecos de voz > 0.12 s entre frases: {sum(1 for x, y in zip(segs, segs[1:]) if y['start'] - x['end'] > 0.12)}")


if __name__ == "__main__":
    main()
