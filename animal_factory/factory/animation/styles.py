"""Estilos visuales seleccionables: paleta de fondos y trazo de personajes."""
from __future__ import annotations

from dataclasses import dataclass


def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix(a: str, b: str, t: float) -> str:
    """Mezcla dos colores hex: t=0 -> a, t=1 -> b."""
    ra, rb = _rgb(a), _rgb(b)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def shade(h: str, f: float) -> str:
    """f<1 oscurece, f>1 aclara."""
    return mix(h, "#000000", 1 - f) if f <= 1 else mix(h, "#ffffff", f - 1)


@dataclass(frozen=True)
class Style:
    id: str
    label: str
    outline: str
    outline_w: float
    whiten: float          # 0..1 desatura/aclara los colores (pastel)
    night_boost: bool      # fondos nocturnos con luces de neón
    sky_day: tuple[str, str]
    sky_night: tuple[str, str]
    ground_day: tuple[str, str]
    ground_night: tuple[str, str]
    accent: str

    def tint(self, h: str) -> str:
        return mix(h, "#ffffff", self.whiten) if self.whiten else h


STYLES: dict[str, Style] = {s.id: s for s in [
    Style("cartoon", "Cartoon colorido", "#2b1d14", 5.0, 0.0, False,
          ("#6ec6ff", "#e8f7ff"), ("#1a1f4d", "#4a3c8c"),
          ("#7ed957", "#4fae3a"), ("#2d5a3d", "#1d3f2b"), "#ffcf33"),
    Style("pastel", "Pastel suave", "#5b4a5e", 4.0, 0.28, False,
          ("#bfe3ff", "#fff3f8"), ("#3b3f78", "#8c7bb8"),
          ("#c5eab0", "#a6d98c"), ("#51775f", "#3a5a47"), "#ffb3c7"),
    Style("neon", "Noche neón", "#0d0a1f", 5.5, 0.0, True,
          ("#2a1a5e", "#e04fd8"), ("#0b0630", "#3a1a7a"),
          ("#25244f", "#15143a"), ("#161338", "#0b0926"), "#2ff3e0"),
]}


def get_style(style_id: str | None) -> Style:
    return STYLES.get(style_id or "cartoon", STYLES["cartoon"])
