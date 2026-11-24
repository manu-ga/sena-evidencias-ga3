"""Modelos de datos compartidos por todas las etapas del pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class CharacterSpec:
    id: str
    name: str
    species: str            # gato, perro, zorro, conejo, oso, cerdo, rana, raton
    gender: str             # "m" | "f" (solo para concordancia en el guion)
    personality: str
    fur: str                # color principal
    fur_dark: str           # sombras, orejas, patas
    belly: str              # hocico / panza
    outfit: str             # camiseta | traje | vestido | sudadera | overol | chaleco
    outfit_color: str
    accent: str             # color de detalles (corbata, moño, etc.)
    accessory: str | None   # sombrero | gorra | gafas | moño | bufanda | None
    eye_color: str
    voice: str              # id de voz del proveedor TTS
    pitch: float = 1.0      # 1.0 = sin cambio
    rate: float = 1.0       # >1 más lento
    scale: float = 1.0      # tamaño relativo
    color: str = "#ffffff"  # color del subtítulo

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Line:
    speaker: str            # "narrador" o id de personaje
    text: str
    emotion: str = "neutral"


@dataclass
class Beat:
    actor: str              # id de personaje
    action: str             # idle walk run jump laugh cry angry surprise dance fall think celebrate shiver
    t0: float               # fracción de la escena (0..1)
    t1: float
    x0: float = 540
    x1: float | None = None
    emo: str | None = None  # happy sad angry surprised scared greedy
    face: int | None = None # 1 mira a la derecha, -1 a la izquierda


@dataclass
class Prop:
    name: str
    x: float
    y: float
    scale: float = 1.0
    anim: str | None = None


@dataclass
class SfxCue:
    t: float                # fracción de la escena
    name: str
    gain: float = 1.0


@dataclass
class CameraKey:
    t: float                # fracción de la escena
    shot: str               # wide | medium | close | follow
    focus: str | None = None
    cut: bool = False       # True = corte seco, False = movimiento suave


@dataclass
class Scene:
    index: int
    title: str
    location: str
    mood: str               # alegre misterioso tenso triste triunfal
    lines: list[Line]
    beats: list[Beat]
    cast: list[str]
    camera: list[CameraKey] = field(default_factory=list)
    sfx: list[SfxCue] = field(default_factory=list)
    props: list[Prop] = field(default_factory=list)
    transition: str = "fade"
    # Se rellenan en el pipeline de audio:
    duration: float = 0.0
    line_times: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class Story:
    idea: str
    title: str
    theme: str
    message: str
    characters: dict[str, CharacterSpec]
    scenes: list[Scene]
    understood: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "idea": self.idea,
            "title": self.title,
            "theme": self.theme,
            "message": self.message,
            "understood": self.understood,
            "characters": {k: v.to_dict() for k, v in self.characters.items()},
            "scenes": [
                {
                    "index": s.index, "title": s.title, "location": s.location,
                    "mood": s.mood, "duration": round(s.duration, 2),
                    "lines": [asdict(l) for l in s.lines],
                    "cast": s.cast,
                }
                for s in self.scenes
            ],
        }
