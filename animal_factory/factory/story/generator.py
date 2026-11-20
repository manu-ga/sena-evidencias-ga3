"""Generador de historias: idea (texto libre) -> `Story` con 7 escenas.

Es un motor de plantillas: detecta animal, tema y rasgos con reglas simples y
rellena una trama escrita a mano. No usa IA generativa ni internet.
Para cambiarlo por un modelo de lenguaje, implemente `StoryProvider`.
"""
from __future__ import annotations

import hashlib
import random
import re
import unicodedata
from typing import Protocol

from ..characters.library import CHARACTERS, SPECIES_TO_CHAR
from ..models import Beat, CameraKey, Line, Prop, Scene, SfxCue, Story
from .plots import CAST_PREFS, PLOTS, THEME_LABEL, Names, SceneDef


class StoryProvider(Protocol):
    """Interfaz para sustituir el generador (p. ej. por un LLM)."""
    def generate(self, idea: str, hero_id: str | None = None) -> Story: ...


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


SPECIES_WORDS = {
    "gato": ["gato", "gata", "gatito", "gatita", "michi", "minino"],
    "perro": ["perro", "perra", "perrito", "perrita", "cachorro"],
    "zorro": ["zorro", "zorra", "zorrito"],
    "conejo": ["conejo", "coneja", "conejito", "conejita"],
    "oso": ["oso", "osa", "osito", "osezno"],
    "cerdo": ["cerdo", "cerda", "chancho", "cochino", "puerco", "cerdito", "marrano"],
    "rana": ["rana", "ranita", "sapo"],
    "raton": ["raton", "ratoncito", "rata", "ratita"],
}

THEME_WORDS = {
    "dinero": ["millonario", "rico", "rica", "dinero", "plata", "fortuna", "pobre", "riqueza", "negocio",
               "loteria", "tesoro", "monedas", "billete", "ambicion", "banco", "estafa"],
    "amor": ["amor", "enamor", "novia", "novio", "cita", "corazon", "conquistar", "romance", "besar", "pareja"],
    "fama": ["famoso", "famosa", "fama", "estrella", "cantar", "cantante", "artista", "influencer", "youtuber",
             "talento", "concurso", "escenario", "actor", "actriz", "musico", "bailar"],
    "valentia": ["miedo", "valiente", "heroe", "monstruo", "fantasma", "oscuridad", "cobarde", "terror", "susto",
                 "bruja", "valentia"],
    "superacion": ["sueno", "meta", "lograr", "superar", "esfuerzo", "rendirse", "intentar", "campeon", "estudiar"],
}

TRAITS = ["pobre", "hambriento", "tímido", "valiente", "perezoso", "soñador", "torpe", "astuto", "gordito", "flaco"]


def detect_species(idea: str) -> str | None:
    words = re.findall(r"[a-zñ]+", _norm(idea))
    for sp, ws in SPECIES_WORDS.items():
        if any(w in words for w in ws):
            return sp
    return None


def detect_theme(idea: str) -> str:
    n = _norm(idea)
    scores = {t: sum(1 for k in ks if k in n) for t, ks in THEME_WORDS.items()}
    best = max(scores, key=lambda t: scores[t])
    return best if scores[best] > 0 else "superacion"


def detect_goal(idea: str) -> str:
    m = re.search(r"(?:quiere|desea|sueña con|sueña|intenta|busca|anhela)\s+(.+?)(?:,|\.|;|\bpero\b|$)", idea, re.I)
    if m:
        g = m.group(1).strip().rstrip("!?")
        g = re.sub(r"\bhacerse\b", "convertirse en", g)
        if 2 <= len(g) <= 60:
            return g
    return "cumplir su sueño"


def _suffix(gender: str) -> str:
    return "a" if gender == "f" else "o"


def _pick(prefs: list[str], used: set[str]) -> str:
    for c in prefs:
        if c not in used:
            return c
    for c in CHARACTERS:
        if c not in used:
            return c
    return prefs[0]


def cast_roles(theme: str, hero: str, extras: dict[str, str] | None = None) -> dict[str, str]:
    f_pref, r_pref, p_pref = CAST_PREFS[theme]
    used = {hero}
    roles = {"H": hero}
    for role, prefs in (("F", f_pref), ("R", r_pref), ("P", p_pref)):
        if extras and extras.get(role) in CHARACTERS and extras[role] not in used:
            roles[role] = extras[role]
        else:
            roles[role] = _pick(prefs, used)
        used.add(roles[role])
    return roles


def _auto_camera(sd: SceneDef) -> list[CameraKey]:
    if sd.cam:
        return [CameraKey(t, shot, focus, cut) for t, shot, focus, cut in sd.cam]
    return [CameraKey(0.0, "wide"), CameraKey(0.45, "medium")]


def generate_story(idea: str, hero_id: str | None = None, extras: dict[str, str] | None = None,
                   seed: int | None = None, style: str | None = None) -> Story:
    idea = (idea or "").strip()
    if len(idea) < 4:
        raise ValueError("Escribe una idea de al menos 4 caracteres.")
    if len(idea) > 400:
        raise ValueError("La idea es muy larga (máximo 400 caracteres).")
    theme = detect_theme(idea)
    species = detect_species(idea)
    if hero_id and hero_id not in CHARACTERS:
        raise ValueError(f"Personaje desconocido: {hero_id}")
    hero = hero_id or (SPECIES_TO_CHAR.get(species) if species else None) or "michi"
    roles = cast_roles(theme, hero, extras)
    ch = {r: CHARACTERS[c] for r, c in roles.items()}

    seed = seed if seed is not None else int(hashlib.sha256(idea.encode()).hexdigest()[:8], 16)
    rnd = random.Random(seed)
    names = Names(
        H=ch["H"].name, F=ch["F"].name, R=ch["R"].name, P=ch["P"].name,
        Ho=_suffix(ch["H"].gender), Fo=_suffix(ch["F"].gender), Ro=_suffix(ch["R"].gender), Po=_suffix(ch["P"].gender),
        goal=detect_goal(idea),
    )
    titles, message, defs = PLOTS[theme](names)
    title = rnd.choice(titles)

    scenes: list[Scene] = []
    used_ids: set[str] = set()
    for i, sd in enumerate(defs, start=1):
        lines = []
        for role, text, emo in sd.lines:
            speaker = "narrador" if role == "N" else roles[role]
            lines.append(Line(speaker, text, emo))
        beats = [Beat(roles[r], a, t0, t1, x0, x1, emo, face) for r, a, t0, t1, x0, x1, emo, face in sd.beats]
        cast = []
        for l in lines:
            if l.speaker != "narrador" and l.speaker not in cast:
                cast.append(l.speaker)
        for b in beats:
            if b.actor not in cast:
                cast.append(b.actor)
        cam = []
        for t, shot, focus, cut in (sd.cam or [(0.0, "wide", None, False), (0.45, "medium", None, False)]):
            cam.append(CameraKey(t, shot, roles.get(focus) if focus else None, cut))
        scenes.append(Scene(
            index=i, title=sd.title, location=sd.location, mood=sd.mood, lines=lines, beats=beats, cast=cast,
            camera=cam, sfx=[SfxCue(t, n) for t, n in sd.sfx],
            props=[Prop(n, x, y, s, a) for n, x, y, s, a in sd.props], transition=sd.tr))
        used_ids.update(cast)

    trait = next((t for t in TRAITS if _norm(t) in _norm(idea)), None)
    understood = {
        "protagonista": f"{ch['H'].name} ({ch['H'].species})",
        "tema": THEME_LABEL[theme],
        "reparto": ", ".join(f"{CHARACTERS[c].name}" for c in roles.values() if c != hero),
    }
    if trait:
        understood["rasgo"] = trait
    if species and species != ch["H"].species:
        understood["aviso"] = f"Elegiste otro protagonista: se usó {ch['H'].name}."
    elif not species and not hero_id:
        understood["aviso"] = "No encontré un animal en la idea; usé a Michi (gato)."
    return Story(idea=idea, title=title, theme=theme, message=message,
                 characters={cid: CHARACTERS[cid] for cid in used_ids}, scenes=scenes, understood=understood)


def scene_word_count(scene: Scene) -> int:
    return sum(len(l.text.split()) for l in scene.lines)
