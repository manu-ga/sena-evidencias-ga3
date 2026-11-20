"""Rig SVG de personajes animales 2D.

Un personaje se dibuja en coordenadas locales: los pies en (0, 0) y la cabeza
hacia y negativa. `Pose` contiene todo lo que cambia entre fotogramas; el dibujo
de la especie, la ropa y los colores sale de `CharacterSpec`, así el diseño
no cambia en todo el video.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..animation.styles import Style, shade, mix
from ..config import GROUND_Y
from ..models import CharacterSpec

DARK = "#3a1e1e"


@dataclass
class Pose:
    x: float = 540.0
    y: float = float(GROUND_Y)       # posición de los pies
    facing: int = 1                  # 1 derecha, -1 izquierda
    bob: float = 0.0                 # sube/baja el cuerpo (px)
    lean: float = 0.0                # inclinación del cuerpo (grados)
    leg_l: float = 0.0               # + = adelante
    leg_r: float = 0.0
    arm_l: float = 0.0               # 0 cuelga, + = separa/levanta
    arm_r: float = 0.0
    head_tilt: float = 0.0
    mouth: float = 0.0               # apertura 0..1
    mouth_shape: str = "smile"       # smile flat frown o laugh
    eyes: str = "open"               # open closed happy angry sad wide greedy dizzy
    look: float = 0.0                # -1..1 mirada
    brow: float = 0.0                # -1 triste .. +1 enojado
    tail: float = 0.0                # grados de la cola
    ear: float = 0.0                 # grados de las orejas
    sx: float = 1.0
    sy: float = 1.0
    rot: float = 0.0                 # giro total (caídas)
    blush: bool = False
    sweat: bool = False
    tear: bool = False
    emote: str | None = None         # "!" "?" "$" "heart"


# --------------------------------------------------------------------------- helpers

def _o(style: Style, w: float = 1.0) -> str:
    return f'stroke="{style.outline}" stroke-width="{style.outline_w * w:.1f}" stroke-linejoin="round" stroke-linecap="round"'


def _ell(cx, cy, rx, ry, fill, style, w=1.0, extra=""):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {_o(style, w)} {extra}/>'


def _path(d, fill, style, w=1.0, extra=""):
    return f'<path d="{d}" fill="{fill}" {_o(style, w)} {extra}/>'


def _line(d, color, width, extra=""):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def _mirror(fn):
    """Dibuja algo en el lado izquierdo y su espejo en el derecho."""
    return fn(-1) + fn(1)


# --------------------------------------------------------------------------- tails

def _tail(spec: CharacterSpec, pose: Pose, st: Style, fur, fur_dark, belly) -> str:
    sp = spec.species
    ang = pose.tail
    if sp == "rana":
        return ""
    if sp == "gato":
        body = ("M0,0 Q-75,-25 -85,-110 Q-90,-155 -52,-165")
        inner = (_line(body, st.outline, 30) + _line(body, fur, 22))
    elif sp == "perro":
        body = "M0,0 Q-55,-15 -62,-75"
        inner = _line(body, st.outline, 26) + _line(body, fur, 18)
    elif sp == "raton":
        body = "M0,0 Q-95,-5 -125,-85 Q-135,-130 -102,-165"
        inner = _line(body, st.outline, 15) + _line(body, "#f2b6c0", 8)
    elif sp == "cerdo":
        body = "M0,0 q-30,-5 -22,-32 q8,-20 -16,-28 q-14,-8 0,-22"
        inner = _line(body, st.outline, 17) + _line(body, fur_dark, 9)
    elif sp == "zorro":
        inner = (_ell(-55, -35, 72, 34, fur, st, extra='transform="rotate(-25 -55 -35)"')
                 + _ell(-105, -62, 34, 22, belly, st, 0.8, extra='transform="rotate(-25 -105 -62)"'))
    elif sp == "conejo":
        inner = _ell(-48, -18, 30, 30, "#ffffff", st)
    elif sp == "tortuga":
        inner = _path("M0,-14 L-52,0 L0,14 Z", fur, st)
    else:  # oso
        inner = _ell(-40, -12, 26, 26, fur, st)
    return f'<g transform="translate(-55 -215) rotate({ang:.1f})">{inner}</g>'


# --------------------------------------------------------------------------- ears

def _ears(spec: CharacterSpec, pose: Pose, st: Style, fur, fur_dark, belly) -> str:
    sp = spec.species
    e = pose.ear

    def side(s: int) -> str:
        t = lambda base: f'transform="translate({s * base[0]} {base[1]}) rotate({s * (e + base[2])}) scale({s} 1)"'
        if sp == "gato":
            return (f'<g transform="translate({s * 62} -520) rotate({s * (e + 8)}) scale({s} 1)">'
                    + _path("M-40,25 L-22,-75 L38,10 Z", fur, st)
                    + _path("M-24,10 L-18,-48 L18,6 Z", "#f4a6b8", st, 0.0) + "</g>")
        if sp == "zorro":
            return (f'<g transform="translate({s * 66} -525) rotate({s * (e + 10)}) scale({s} 1)">'
                    + _path("M-42,25 L-25,-100 L42,12 Z", fur, st)
                    + _path("M-25,-100 L-33,-55 L-10,-62 Z", "#2b1d14", st, 0.0)
                    + _path("M-26,5 L-20,-52 L16,4 Z", belly, st, 0.0) + "</g>")
        if sp == "perro":
            return (f'<g transform="translate({s * 98} -500) rotate({s * (-12 + e)}) scale({s} 1)">'
                    + _ell(0, 50, 36, 74, fur_dark, st) + "</g>")
        if sp == "conejo":
            return (f'<g transform="translate({s * 48} -530) rotate({s * (e + 6)}) scale({s} 1)">'
                    + _ell(0, -78, 30, 96, fur, st) + _ell(0, -78, 15, 74, belly, st, 0.0) + "</g>")
        if sp == "oso":
            return (f'<g transform="translate({s * 80} -522)">'
                    + _ell(0, 0, 40, 40, fur, st) + _ell(0, 4, 21, 21, belly, st, 0.0) + "</g>")
        if sp == "cerdo":
            return (f'<g transform="translate({s * 76} -525) rotate({s * (e + 25)}) scale({s} 1)">'
                    + _path("M-38,10 L-12,-62 L40,6 Q4,22 -38,10 Z", fur_dark, st) + "</g>")
        if sp == "raton":
            return (f'<g transform="translate({s * 92} -512) rotate({s * e})">'
                    + _ell(0, 0, 58, 58, fur, st) + _ell(0, 2, 38, 38, "#f2b6c0", st, 0.0) + "</g>")
        return ""
    return _mirror(side)


# --------------------------------------------------------------------------- face

def _eyes(spec: CharacterSpec, pose: Pose, st: Style) -> str:
    sp = spec.species
    ey = -462 if sp != "rana" else -528
    ex = 42 if sp != "rana" else 56
    big = 1.0 if sp != "rana" else 1.25
    look = pose.look * 8
    out = []
    state = pose.eyes

    def pupil(cx):
        if state == "wide":
            return (f'<circle cx="{cx + look * 0.5:.1f}" cy="{ey + 2}" r="7" fill="{DARK}"/>')
        if state == "greedy":
            return (f'<text x="{cx}" y="{ey + 12}" font-family="DejaVu Sans, Inter, sans-serif" font-size="34" '
                    f'font-weight="bold" text-anchor="middle" fill="#1e9d3a">$</text>')
        if state == "dizzy":
            return (_line(f"M{cx - 11},{ey - 11} L{cx + 11},{ey + 11} M{cx + 11},{ey - 11} L{cx - 11},{ey + 11}", DARK, 5))
        return (f'<circle cx="{cx + look:.1f}" cy="{ey + 3}" r="{12 * big:.1f}" fill="{spec.eye_color}"/>'
                f'<circle cx="{cx + look:.1f}" cy="{ey + 3}" r="{6.5 * big:.1f}" fill="{DARK}"/>'
                f'<circle cx="{cx + look - 4:.1f}" cy="{ey - 3}" r="3.5" fill="#fff"/>')

    for s in (-1, 1):
        cx = s * ex
        if state in ("closed",):
            out.append(_line(f"M{cx - 20},{ey + 4} Q{cx},{ey + 14} {cx + 20},{ey + 4}", st.outline, 6))
        elif state == "happy":
            out.append(_line(f"M{cx - 22},{ey + 8} Q{cx},{ey - 24} {cx + 22},{ey + 8}", st.outline, 7))
        else:
            rx = (26 if state != "wide" else 31) * big
            ry = (30 if state != "wide" else 36) * big
            out.append(_ell(cx, ey, rx, ry, "#ffffff", st, 0.8))
            out.append(pupil(cx))
            if state == "angry":
                # párpado superior inclinado hacia el centro
                out.append(f'<path d="M{cx + s * 30},{ey - 34 * big:.0f} L{cx - s * 30},{ey - 6:.0f} L{cx - s * 30},{ey - 40 * big:.0f} Z" '
                           f'fill="{spec.fur}" stroke="none"/>'
                           + _line(f"M{cx + s * 30},{ey - 34 * big:.0f} L{cx - s * 30},{ey - 6:.0f}", st.outline, 6))
            elif state == "sad":
                out.append(f'<path d="M{cx - s * 30},{ey - 34 * big:.0f} L{cx + s * 30},{ey - 8:.0f} L{cx + s * 30},{ey - 40 * big:.0f} Z" '
                           f'fill="{spec.fur}" stroke="none"/>'
                           + _line(f"M{cx - s * 30},{ey - 34 * big:.0f} L{cx + s * 30},{ey - 8:.0f}", st.outline, 6))
    return "".join(out)


def _mouth(spec: CharacterSpec, pose: Pose, st: Style, y: float) -> str:
    m = max(0.0, min(1.0, pose.mouth))
    shape = pose.mouth_shape
    w = 30 if spec.species != "rana" else 70
    teeth = ""
    if spec.species == "conejo":
        teeth = (f'<rect x="-13" y="{y + 1}" width="12" height="17" rx="3" fill="#fff" {_o(st, 0.7)}/>'
                 f'<rect x="1" y="{y + 1}" width="12" height="17" rx="3" fill="#fff" {_o(st, 0.7)}/>')
    if shape == "laugh":
        m = max(m, 0.85)
    if m > 0.06 or shape == "laugh":
        h = 8 + 46 * m
        return (f'<clipPath id="mc{spec.id}"><path d="M{-w},{y} Q0,{y + 2 * h:.1f} {w},{y} Z"/></clipPath>'
                f'<path d="M{-w},{y} Q0,{y + 2 * h:.1f} {w},{y} Z" fill="#6b1d1d" {_o(st, 0.9)}/>'
                f'<g clip-path="url(#mc{spec.id})"><ellipse cx="0" cy="{y + h * 1.25:.1f}" rx="{w * 0.55:.0f}" ry="{h * 0.45:.1f}" fill="#f06a7e"/></g>'
                + teeth)
    if shape == "o":
        return f'<ellipse cx="0" cy="{y + 8}" rx="11" ry="14" fill="#6b1d1d" {_o(st, 0.8)}/>'
    if shape == "frown":
        return _line(f"M{-w * 0.8},{y + 14} Q0,{y - 10} {w * 0.8},{y + 14}", st.outline, 6) + teeth
    if shape == "flat":
        return _line(f"M{-w * 0.7},{y + 6} L{w * 0.7},{y + 6}", st.outline, 6)
    return _line(f"M{-w},{y} Q0,{y + 24} {w},{y}", st.outline, 6) + teeth


def _head(spec: CharacterSpec, pose: Pose, st: Style, fur, fur_dark, belly) -> str:
    sp = spec.species
    parts = [_ears(spec, pose, st, fur, fur_dark, belly)]
    if sp == "tortuga":
        parts.append(_ell(0, -440, 98, 88, fur, st))
        parts.append(_ell(0, -405, 56, 40, belly, st, 0.8))
        for s_ in (-1, 1):
            parts.append(f'<circle cx="{s_ * 11}" cy="-418" r="4" fill="{st.outline}"/>')
        mouth_y = -388
    elif sp == "rana":
        parts.append(_ell(0, -440, 122, 82, fur, st))
        parts.append(_ell(-56, -528, 40, 40, fur, st))
        parts.append(_ell(56, -528, 40, 40, fur, st))
        parts.append(_ell(0, -410, 100, 40, belly, st, 0.0, 'opacity="0.55"'))
        mouth_y = -405
    else:
        rx, ry = (108, 98)
        if sp == "zorro":
            rx = 112
        if sp == "raton":
            rx, ry = 100, 96
        parts.append(_ell(0, -445, rx, ry, fur, st))
        if sp == "zorro":
            parts.append(_path("M-112,-440 Q-85,-380 -30,-368 Q0,-362 30,-368 Q85,-380 112,-440 Q60,-405 0,-402 Q-60,-405 -112,-440 Z", belly, st, 0.0))
        if sp == "gato":
            for s in (-1, 1):
                parts.append(_line(f"M{s * 30},-535 l0,26 M{s * 48},-530 l4,24 M{s * 14},-537 l-2,20", fur_dark, 7))
        if sp == "perro":
            parts.append(_ell(-52, -462, 42, 44, fur_dark, st, 0.0))
        # hocico
        if sp in ("gato", "perro", "oso", "zorro", "conejo", "raton"):
            mx, my, mrx, mry = {"gato": (0, -408, 52, 36), "perro": (0, -402, 64, 46), "oso": (0, -402, 58, 42),
                                "zorro": (0, -405, 56, 34), "conejo": (0, -408, 50, 34), "raton": (0, -408, 46, 36)}[sp]
            parts.append(_ell(mx, my, mrx, mry, belly, st, 0.8))
        mouth_y = -392
        if sp == "cerdo":
            parts.append(_ell(0, -408, 54, 38, fur_dark, st))
            parts.append(f'<ellipse cx="-17" cy="-410" rx="8" ry="13" fill="{shade(fur_dark, .55)}"/>')
            parts.append(f'<ellipse cx="17" cy="-410" rx="8" ry="13" fill="{shade(fur_dark, .55)}"/>')
            mouth_y = -380
    parts.append(_eyes(spec, pose, st))
    # nariz
    if sp == "gato":
        parts.append(_path("M-12,-430 L12,-430 L0,-416 Z", "#f4859d", st, 0.7))
    elif sp == "perro":
        parts.append(_ell(0, -425, 20, 14, "#222", st, 0.5))
    elif sp == "zorro":
        parts.append(_ell(0, -428, 13, 10, "#222", st, 0.5))
    elif sp == "conejo":
        parts.append(_path("M-9,-428 L9,-428 L0,-417 Z", "#ff6f91", st, 0.6))
    elif sp == "oso":
        parts.append(_ell(0, -424, 19, 13, "#2b1d14", st, 0.5))
    elif sp == "raton":
        parts.append(_ell(0, -430, 12, 10, "#f2788f", st, 0.6))
    if sp in ("gato", "raton"):
        for s in (-1, 1):
            parts.append(_line(f"M{s * 40},-415 L{s * 110},-430 M{s * 40},-405 L{s * 112},-402 M{s * 40},-395 L{s * 106},-376", st.outline, 3))
    parts.append(_mouth(spec, pose, st, mouth_y))
    if pose.blush:
        for s in (-1, 1):
            parts.append(f'<ellipse cx="{s * 76}" cy="-410" rx="20" ry="12" fill="#ff6f91" opacity="0.5"/>')
    if pose.tear:
        for s in (-1, 1):
            parts.append(f'<path d="M{s * 52},-428 q-9,22 0,26 q9,-4 0,-26 Z" fill="#6ec6ff" {_o(st, 0.5)}/>')
    if pose.sweat:
        parts.append(f'<path d="M96,-520 q-14,28 0,34 q14,-6 0,-34 Z" fill="#8fd3ff" {_o(st, 0.5)}/>')
    parts.append(_accessory(spec, st))
    return "".join(parts)


def _accessory(spec: CharacterSpec, st: Style) -> str:
    a = spec.accessory
    ac = spec.accent
    if a == "sombrero":
        return (_ell(0, -532, 96, 16, "#1d1d1d", st) +
                f'<rect x="-56" y="-640" width="112" height="108" rx="10" fill="#222" {_o(st)}/>'
                f'<rect x="-56" y="-566" width="112" height="22" fill="{ac}" {_o(st, 0.6)}/>')
    if a == "gorra":
        return (_path("M-100,-520 Q-95,-600 0,-604 Q95,-600 100,-520 Q0,-540 -100,-520 Z", spec.accent if spec.id != "bruno" else spec.outfit_color, st)
                + _path("M20,-526 Q95,-545 135,-515 Q90,-505 30,-512 Z", shade(spec.accent if spec.id != "bruno" else spec.outfit_color, .8), st))
    if a == "gafas":
        return ("".join(f'<circle cx="{s * 42}" cy="-462" r="35" fill="#cfe9ff" fill-opacity="0.25" stroke="#222" stroke-width="6"/>' for s in (-1, 1))
                + _line("M-7,-462 L7,-462", "#222", 6) + _line("M-77,-462 L-104,-470 M77,-462 L104,-470", "#222", 5))
    if a == "moño":
        return (f'<g transform="translate(-62 -545) rotate(-18)">'
                + _path("M0,0 L-42,-26 L-42,26 Z", ac, st, 0.8) + _path("M0,0 L42,-26 L42,26 Z", ac, st, 0.8)
                + _ell(0, 0, 12, 12, shade(ac, .8), st, 0.7) + "</g>")
    return ""


# --------------------------------------------------------------------------- body

def _outfit_extra(spec: CharacterSpec, st: Style, oc: str) -> str:
    ac = spec.accent
    o = spec.outfit
    if o == "traje":
        return (_path("M-30,-350 L0,-290 L30,-350 Z", "#fafafa", st, 0.7)
                + _path(f"M-9,-340 L9,-340 L14,-268 L0,-250 L-14,-268 Z", ac, st, 0.7))
    if o == "camiseta":
        return f'<rect x="-76" y="-285" width="152" height="22" fill="{ac}" opacity="0.85"/>'
    if o == "sudadera":
        return (f'<rect x="-40" y="-258" width="80" height="42" rx="12" fill="{shade(oc, .82)}" {_o(st, 0.6)}/>'
                + _ell(0, -352, 46, 14, shade(oc, .75), st, 0.7))
    if o == "overol":
        return (f'<rect x="-52" y="-345" width="104" height="150" rx="18" fill="{shade(oc, .94)}" {_o(st, 0.8)}/>'
                + f'<rect x="-52" y="-352" width="16" height="70" fill="{oc}" {_o(st, 0.6)}/><rect x="36" y="-352" width="16" height="70" fill="{oc}" {_o(st, 0.6)}/>'
                + f'<rect x="-22" y="-300" width="44" height="30" rx="6" fill="{ac}" {_o(st, 0.6)}/>')
    if o == "chaleco":
        return (f'<path d="M-6,-352 L-6,-195 M6,-352 L6,-195" stroke="{st.outline}" stroke-width="3"/>'
                + "".join(f'<circle cx="0" cy="{y}" r="6" fill="{ac}" {_o(st, 0.4)}/>' for y in (-300, -258, -222))
                + _path("M-76,-345 L-6,-352 L-6,-300 L-76,-300 Z", "none", st, 0.0))
    if o == "chal":
        return (_path("M-96,-340 Q0,-382 96,-340 L64,-236 L0,-198 L-64,-236 Z", shade(oc, .82), st, 0.8)
                + "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{ac}"/>' for x, y in ((-50, -318), (0, -300), (50, -318), (-26, -262), (26, -262))))
    if o == "vestido":
        return _path("M-100,-195 Q0,-170 100,-195 L112,-178 Q0,-150 -112,-178 Z", ac, st, 0.7)
    return ""


def _torso(spec: CharacterSpec, st: Style, oc: str) -> str:
    if spec.outfit == "vestido":
        body = "M-70,-350 Q-85,-270 -108,-185 Q0,-160 108,-185 Q85,-270 70,-350 Q0,-372 -70,-350 Z"
    else:
        body = "M-78,-195 Q-88,-265 -72,-348 Q0,-372 72,-348 Q88,-265 78,-195 Q0,-172 -78,-195 Z"
    return _path(body, oc, st) + _outfit_extra(spec, st, oc)


def _leg(spec: CharacterSpec, st: Style, s: int, ang: float, leg_color: str, shoe: str) -> str:
    return (f'<g transform="translate({s * 38} -195) rotate({-ang:.1f})">'
            + f'<rect x="-17" y="0" width="34" height="166" rx="17" fill="{leg_color}" {_o(st, 0.9)}/>'
            + _ell(9, 172, 38, 19, shoe, st, 0.9) + "</g>")


def _arm(spec: CharacterSpec, st: Style, s: int, ang: float, fur: str, oc: str) -> str:
    sleeve = spec.outfit in ("sudadera", "traje", "chaleco")
    sl = f'<rect x="-15" y="0" width="30" height="64" rx="15" fill="{oc}" {_o(st, 0.8)}/>' if sleeve else ""
    return (f'<g transform="translate({s * 84} -326) rotate({s * ang:.1f})">'
            + f'<rect x="-15" y="0" width="30" height="150" rx="15" fill="{fur}" {_o(st, 0.9)}/>' + sl
            + _ell(0, 154, 20, 20, fur, st, 0.9) + "</g>")


def _emote(pose: Pose, st: Style, spec: CharacterSpec) -> str:
    e = pose.emote
    if not e:
        return ""
    x, y = 120, -600
    if e in ("!", "?", "$"):
        col = {"!": "#ff3b30", "?": "#2f80ed", "$": "#1e9d3a"}[e]
        return (f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Inter, sans-serif" font-size="120" font-weight="bold" '
                f'text-anchor="middle" fill="{col}" stroke="#fff" stroke-width="8" paint-order="stroke">{e}</text>')
    if e == "heart":
        return (f'<path transform="translate({x} {y + 30}) scale(2.2)" d="M0,12 C-30,-8 -16,-32 0,-16 C16,-32 30,-8 0,12 Z" fill="#ff4d6d" {_o(st, 0.5)}/>')
    return ""


def character_svg(spec: CharacterSpec, pose: Pose, style: Style, ground_y: float = GROUND_Y) -> str:
    """Devuelve el SVG (grupo) del personaje en `pose`, sombra incluida."""
    fur = style.tint(spec.fur)
    fur_dark = style.tint(spec.fur_dark)
    belly = style.tint(spec.belly)
    oc = style.tint(spec.outfit_color)
    pants = shade(oc, 0.78) if spec.outfit in ("traje", "overol", "sudadera", "chaleco") else fur
    shoe = shade(spec.accent, 0.55) if spec.outfit != "vestido" else shade(spec.outfit_color, 0.7)
    sc = spec.scale

    height_off = max(0.0, ground_y - pose.y)
    sh = max(0.35, 1 - height_off / 700)
    shadow = (f'<ellipse cx="{pose.x:.1f}" cy="{ground_y + 10}" rx="{105 * sc * sh:.1f}" ry="{22 * sc * sh:.1f}" '
              f'fill="#000" opacity="{0.25 * sh:.2f}"/>')

    behind = ""
    if spec.species == "tortuga":
        behind = (_ell(0, -275, 128, 116, shade(fur_dark, .9), style)
                  + "".join(_line(d, spec.accent, 4, 'opacity="0.8"') for d in (
                      "M-80,-330 L-40,-290 L-40,-240 M80,-330 L40,-290 L40,-240 M-40,-290 L40,-290 M-40,-240 L40,-240",)))
    elif spec.accessory == "mochila":
        behind = f'<rect x="-112" y="-345" width="70" height="128" rx="20" fill="{spec.accent}" {_o(style)}/>'
    # cuerpo (con bob y lean alrededor de la cadera)
    body = (behind + _tail(spec, pose, style, fur, fur_dark, belly)
            + _arm(spec, style, -1, pose.arm_l, fur, oc)
            + _leg(spec, style, -1, pose.leg_l, pants, shoe)
            + _leg(spec, style, 1, pose.leg_r, pants, shoe)
            + _torso(spec, style, oc)
            + _arm(spec, style, 1, pose.arm_r, fur, oc)
            + (f'<g transform="rotate({pose.head_tilt:.1f} 0 -362)">' + _head(spec, pose, style, fur, fur_dark, belly)
               + _emote(pose, style, spec) + "</g>"))
    if spec.accessory == "bufanda":
        body = body.replace("<!--scarf-->", "")
        scarf = (f'<g transform="rotate({pose.head_tilt:.1f} 0 -362)">'
                 f'<rect x="-66" y="-372" width="132" height="34" rx="17" fill="{spec.accent}" {_o(style)}/>'
                 f'<rect x="30" y="-352" width="30" height="86" rx="12" fill="{spec.accent}" {_o(style)}/></g>')
        # la bufanda va entre torso y cabeza: se inserta antes de la cabeza
        idx = body.rfind(f'<g transform="rotate({pose.head_tilt:.1f} 0 -362)">')
        body = body[:idx] + scarf + body[idx:]

    tr = (f'translate({pose.x:.1f} {pose.y + pose.bob:.1f}) rotate({pose.rot:.1f}) '
          f'scale({pose.sx * sc * pose.facing:.3f} {pose.sy * sc:.3f}) rotate({pose.lean:.1f} 0 -195)')
    return shadow + f'<g transform="{tr}">{body}</g>'
