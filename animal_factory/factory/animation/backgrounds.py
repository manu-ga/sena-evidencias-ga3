"""Fondos y objetos de escena en SVG, generados con código.

Cada fondo es una función del tiempo `t` (nubes, estrellas y luces se mueven) y de
la cámara (parallax: las capas lejanas se desplazan menos).
"""
from __future__ import annotations

import math
import random

from ..config import WORLD_H, WORLD_W
from .styles import Style, mix, shade

HORIZON = 1180
W, H = WORLD_W, WORLD_H


def _sky(style: Style, night: bool, sid: str, dusk: bool = False) -> str:
    top, bot = (style.sky_night if night else style.sky_day)
    if dusk:
        top, bot = "#5b3f9e", "#ffb36b"
    return (f'<defs><linearGradient id="{sid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#{sid})"/>')


def _stars(t: float, n: int = 45, seed: int = 3) -> str:
    r = random.Random(seed)
    out = []
    for i in range(n):
        x, y = r.uniform(0, W), r.uniform(40, 760)
        tw = 0.55 + 0.45 * math.sin(t * 2.2 + i)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(2, 5) * tw:.1f}" fill="#fff" opacity="{0.5 + 0.5 * tw:.2f}"/>')
    return "".join(out)


def _moon(x=840, y=330) -> str:
    return (f'<circle cx="{x}" cy="{y}" r="120" fill="#fff6c9" opacity="0.18"/><circle cx="{x}" cy="{y}" r="85" fill="#fff6c9"/>'
            f'<circle cx="{x - 25}" cy="{y - 15}" r="14" fill="#ece2a8"/><circle cx="{x + 30}" cy="{y + 25}" r="9" fill="#ece2a8"/>')


def _sun(x=820, y=330) -> str:
    return (f'<circle cx="{x}" cy="{y}" r="130" fill="#fff3a0" opacity="0.35"/><circle cx="{x}" cy="{y}" r="86" fill="#ffd93b"/>')


def _clouds(t: float, color="#ffffff", opacity=0.9, y0=230, n=4, speed=9.0) -> str:
    out = []
    for i in range(n):
        x = ((i * 330 + t * speed) % (W + 500)) - 250
        y = y0 + (i * 97) % 340
        s = 0.8 + (i % 3) * 0.3
        out.append(f'<g transform="translate({x:.0f} {y}) scale({s})" fill="{color}" opacity="{opacity}">'
                   '<ellipse cx="0" cy="0" rx="90" ry="38"/><ellipse cx="-55" cy="12" rx="60" ry="30"/>'
                   '<ellipse cx="60" cy="14" rx="66" ry="30"/><ellipse cx="15" cy="-24" rx="55" ry="34"/></g>')
    return "".join(out)


def _skyline(seed: int, base: float, color: str, lit: bool, t: float, hmin=180, hmax=520, wmin=90, wmax=190, glow="#ffe08a") -> str:
    r = random.Random(seed)
    x, out = -40.0, []
    while x < W + 40:
        w, h = r.uniform(wmin, wmax), r.uniform(hmin, hmax)
        out.append(f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{color}"/>')
        for wy in range(int(base - h + 30), int(base - 30), 52):
            for wx in range(int(x + 16), int(x + w - 26), 38):
                on = r.random() < 0.55
                if lit and on:
                    fl = 0.8 + 0.2 * math.sin(t * 1.5 + wx * 0.1 + wy * 0.07)
                    out.append(f'<rect x="{wx}" y="{wy}" width="16" height="24" fill="{glow}" opacity="{fl:.2f}"/>')
                elif not lit and on:
                    out.append(f'<rect x="{wx}" y="{wy}" width="16" height="24" fill="#ffffff" opacity="0.28"/>')
        x += w + r.uniform(0, 14)
    return "".join(out)


def _house(x, y, w, h, wall, roof, door="#7b4a2a") -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{wall}"/>'
            f'<polygon points="{x - 18},{y} {x + w / 2},{y - h * 0.5} {x + w + 18},{y}" fill="{roof}"/>'
            f'<rect x="{x + w * 0.4}" y="{y + h * 0.4}" width="{w * 0.22}" height="{h * 0.6}" fill="{door}"/>'
            f'<rect x="{x + w * 0.1}" y="{y + h * 0.2}" width="{w * 0.2}" height="{h * 0.22}" fill="#cfeaff"/>'
            f'<rect x="{x + w * 0.7}" y="{y + h * 0.2}" width="{w * 0.2}" height="{h * 0.22}" fill="#cfeaff"/>')


def _tree(x, base, s=1.0, leaf="#3f9d4a", trunk="#7a4b2a") -> str:
    return (f'<g transform="translate({x} {base}) scale({s})"><rect x="-18" y="-190" width="36" height="190" fill="{trunk}"/>'
            f'<circle cx="0" cy="-250" r="105" fill="{leaf}"/><circle cx="-70" cy="-205" r="70" fill="{shade(leaf, .92)}"/>'
            f'<circle cx="72" cy="-208" r="72" fill="{shade(leaf, 1.08)}"/></g>')


def _ground(style: Style, night: bool, gid: str, road: bool = False, y: int = HORIZON) -> str:
    a, b = (style.ground_night if night else style.ground_day)
    out = (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/>'
           f'<stop offset="1" stop-color="{b}"/></linearGradient></defs><rect x="0" y="{y}" width="{W}" height="{H - y}" fill="url(#{gid})"/>')
    if road:
        road_c = "#3b3b4a" if not night else "#1c1c2a"
        out += (f'<rect x="0" y="{y + 130}" width="{W}" height="{H - y - 130}" fill="{road_c}"/>'
                f'<rect x="0" y="{y + 120}" width="{W}" height="16" fill="#bdbdc8"/>')
        for i in range(-1, 8):
            out += f'<rect x="{i * 190 + 30}" y="{y + 330}" width="110" height="20" rx="6" fill="#f2f2f2" opacity="0.85"/>'
    return out


def _floor_wall(style: Style, wall: str, floor: str, y: int = 1130) -> str:
    out = f'<rect width="{W}" height="{y}" fill="{wall}"/><rect y="{y}" width="{W}" height="{H - y}" fill="{floor}"/>'
    out += f'<rect y="{y - 20}" width="{W}" height="26" fill="{shade(wall, .8)}"/>'
    for i in range(1, 7):
        out += f'<rect x="0" y="{y + i * 108}" width="{W}" height="4" fill="{shade(floor, .8)}" opacity="0.7"/>'
    return out


# --------------------------------------------------------------------------- escenarios

def _calle(style, t, night, p1, p2):
    out = _sky(style, night, "sk")
    out += _stars(t) + _moon() if night else _sun() + _clouds(t)
    out += f'<g transform="translate({p1} 0)">' + _skyline(7, HORIZON, "#3d4a7a" if night else "#9db5d6", night, t, 220, 560) + "</g>"
    out += _ground(style, night, "gr", road=True)
    out += f'<g transform="translate({p2} 0)">' + _skyline(11, HORIZON + 90, "#2a3158" if night else "#7d98c4", night, t, 140, 330, 120, 220) + "</g>"
    # farolas
    for x in (120, 560, 1000):
        out += (f'<rect x="{x - 7}" y="{HORIZON - 230}" width="14" height="{300}" fill="#2a2a38"/>'
                f'<circle cx="{x}" cy="{HORIZON - 245}" r="26" fill="#ffe28a"/>'
                + (f'<circle cx="{x}" cy="{HORIZON - 245}" r="85" fill="#ffe28a" opacity="0.22"/>' if night else ""))
    return out


def _parque(style, t, night, p1, p2, dusk=False):
    out = _sky(style, night, "sk", dusk)
    out += (_stars(t) + _moon() if night else _sun(780, 420 if dusk else 330) + _clouds(t))
    out += f'<g transform="translate({p1} 0)">' + "".join(_tree(x, HORIZON + 10, 0.8, "#3b8c53" if not night else "#1f4d36") for x in (90, 330, 620, 950)) + "</g>"
    out += _ground(style, night, "gr")
    out += f'<g transform="translate({p2} 0)">' + "".join(_tree(x, HORIZON + 130, 1.15, "#4aa85a" if not night else "#2a6a46") for x in (-20, 1090)) + "</g>"
    # camino y flores
    out += f'<path d="M-50,{H} Q520,{HORIZON + 300} 1130,{H} Z" fill="{"#d9c08c" if not night else "#6b6a77"}" opacity="0.8"/>'
    r = random.Random(5)
    for _ in range(26):
        x, y = r.uniform(0, W), r.uniform(HORIZON + 40, H - 80)
        c = r.choice(["#ff6b9d", "#ffd93b", "#ffffff", "#ff8c42"])
        out += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{c}"/><circle cx="{x:.0f}" cy="{y:.0f}" r="3.5" fill="#ffe97a"/>'
    return out


def _casa(style, t, night, p1, p2):
    wall = "#d8b98e" if not night else "#4a4668"
    out = _floor_wall(style, wall, "#8a6a4a" if not night else "#3a3050", 1130)
    # ventana
    sky = "#9bd3ff" if not night else "#16194a"
    out += (f'<rect x="150" y="360" width="340" height="420" rx="14" fill="{sky}" stroke="#6d4a2b" stroke-width="16"/>'
            f'<rect x="318" y="360" width="16" height="420" fill="#6d4a2b"/><rect x="150" y="562" width="340" height="16" fill="#6d4a2b"/>')
    out += (_moon(320, 480).replace("r=\"120\"", "r=\"60\"").replace("r=\"85\"", "r=\"40\"") if night else _clouds(t, n=1, y0=450, speed=4))
    # cortina rota, cuadro, mesa, lámpara, nevera vacía
    out += f'<path d="M130,340 L150,340 L180,820 L125,780 Z" fill="#b05a5a" opacity="0.85"/>'
    out += f'<rect x="640" y="400" width="250" height="180" fill="#f5e6c8" stroke="#6d4a2b" stroke-width="14"/><text x="765" y="505" font-size="40" font-family="DejaVu Sans" text-anchor="middle" fill="#6d4a2b" font-weight="bold">SOÑAR</text>'
    out += (f'<rect x="700" y="1020" width="330" height="30" fill="#6d4a2b"/><rect x="720" y="1050" width="22" height="130" fill="#6d4a2b"/>'
            f'<rect x="988" y="1050" width="22" height="130" fill="#6d4a2b"/>'
            f'<path d="M820,1020 L850,930 L920,930 L950,1020 Z" fill="#ffe28a"/><rect x="882" y="1020" width="6" height="0" fill="#555"/>')
    out += f'<circle cx="885" cy="935" r="150" fill="#ffe28a" opacity="{0.10 if not night else 0.22}"/>'
    return out


def _mercado(style, t, night, p1, p2):
    out = _sky(style, night, "sk") + (_stars(t) if night else _clouds(t, n=3))
    out += _ground(style, night, "gr", y=1150)
    cols = ["#e74c3c", "#f1c40f", "#3498db", "#2ecc71"]
    for i, x in enumerate((-30, 300, 640, 960)):
        c = cols[i % 4]
        out += f'<g transform="translate({x + p1 * 0.5} 0)"><rect x="40" y="820" width="14" height="340" fill="#6d4a2b"/><rect x="230" y="820" width="14" height="340" fill="#6d4a2b"/>'
        for k in range(6):
            out += f'<rect x="{30 + k * 36}" y="720" width="36" height="110" fill="{c if k % 2 == 0 else "#ffffff"}"/>'
        out += (f'<rect x="20" y="1020" width="250" height="140" fill="#a67845"/>'
                f'<circle cx="75" cy="1000" r="26" fill="#e84c3d"/><circle cx="135" cy="995" r="26" fill="#f4b400"/><circle cx="195" cy="1000" r="26" fill="#6cc04a"/></g>')
    return out


def _oficina(style, t, night, p1, p2):
    out = _floor_wall(style, "#e9e1d0", "#7a6a5a", 1150)
    out += (f'<rect x="120" y="260" width="840" height="150" rx="20" fill="#1d3b5c"/>'
            f'<text x="540" y="362" font-size="96" font-weight="bold" font-family="DejaVu Sans" text-anchor="middle" fill="#ffd23f">BANCO</text>')
    ang = t * 20
    out += (f'<circle cx="540" cy="560" r="100" fill="#fff" stroke="#6d4a2b" stroke-width="14"/>'
            f'<line x1="540" y1="560" x2="{540 + 60 * math.sin(math.radians(ang)):.1f}" y2="{560 - 60 * math.cos(math.radians(ang)):.1f}" stroke="#222" stroke-width="8"/>'
            f'<line x1="540" y1="560" x2="{540 + 38 * math.sin(math.radians(ang / 12)):.1f}" y2="{560 - 38 * math.cos(math.radians(ang / 12)):.1f}" stroke="#222" stroke-width="10"/>')
    out += f'<rect x="0" y="1000" width="{W}" height="150" fill="#5c4332"/><rect x="0" y="990" width="{W}" height="22" fill="#a9824e"/>'
    for x in range(40, W, 90):
        out += f'<rect x="{x}" y="800" width="10" height="190" fill="#c9a24a"/>'
    return out


def _escenario(style, t, night, p1, p2):
    out = f'<rect width="{W}" height="{H}" fill="#2a0f2e"/>'
    out += f'<rect x="0" y="0" width="{W}" height="1200" fill="#7b1731"/>'
    for i in range(9):
        out += f'<path d="M{i * 135 - 20},0 Q{i * 135 + 40},600 {i * 135 - 20},1200 L{i * 135 + 80},1200 Q{i * 135 + 60},600 {i * 135 + 80},0 Z" fill="{shade("#9b1c3f", 0.85 + (i % 2) * 0.15)}"/>'
    out += f'<rect x="0" y="1170" width="{W}" height="{H - 1170}" fill="#7a4b2a"/>'
    for i in range(10):
        out += f'<rect x="0" y="{1200 + i * 80}" width="{W}" height="3" fill="#5a361d"/>'
    for i, x in enumerate((220, 540, 860)):
        a = 0.16 + 0.1 * math.sin(t * 2 + i * 1.7)
        out += f'<polygon points="{x},0 {x - 180},1300 {x + 180},1300" fill="#fff3b0" opacity="{a:.2f}"/>'
    for i in range(20):
        on = (int(t * 3) + i) % 2 == 0
        out += f'<circle cx="{40 + i * 52}" cy="60" r="12" fill="{"#ffe066" if on else "#7a5c00"}"/>'
    return out


def _ciudad(style, t, night, p1, p2):
    out = _sky(style, night, "sk", dusk=not night)
    out += (_stars(t) if night else _sun(540, 700).replace("#ffd93b", "#ffb347") + _clouds(t, "#ffe0c0", 0.75))
    out += f'<g transform="translate({p1} 0)">' + _skyline(21, HORIZON, "#3a2f6b", True, t, 360, 900, 100, 170) + "</g>"
    out += _ground(style, night, "gr", road=True)
    out += f'<g transform="translate({p2} 0)">' + _skyline(23, HORIZON + 80, "#241b4a", True, t, 160, 360, 110, 200) + "</g>"
    return out


def _bosque(style, t, night, p1, p2):
    out = _sky(style, night, "sk") + (_stars(t, 25) + _moon(240, 300) if night else _clouds(t, n=2))
    out += f'<g transform="translate({p1} 0)">' + "".join(_tree(x, HORIZON, 0.9, "#2f7a45" if not night else "#173f2b") for x in range(20, 1100, 190)) + "</g>"
    out += _ground(style, night, "gr")
    out += f'<g transform="translate({p2} 0)">' + "".join(_tree(x, HORIZON + 140, 1.3, "#3f9d4a" if not night else "#1f5236") for x in (-40, 360, 780, 1120)) + "</g>"
    out += f'<rect y="{HORIZON - 200}" width="{W}" height="260" fill="#ffffff" opacity="{0.14 + 0.05 * math.sin(t):.2f}"/>'
    return out


LOCATIONS = {
    "calle_dia": lambda s, t, a, b: _calle(s, t, False, a, b),
    "calle_noche": lambda s, t, a, b: _calle(s, t, True, a, b),
    "parque": lambda s, t, a, b: _parque(s, t, False, a, b),
    "atardecer": lambda s, t, a, b: _parque(s, t, False, a, b, dusk=True),
    "parque_noche": lambda s, t, a, b: _parque(s, t, True, a, b),
    "casa": lambda s, t, a, b: _casa(s, t, False, a, b),
    "casa_noche": lambda s, t, a, b: _casa(s, t, True, a, b),
    "mercado": lambda s, t, a, b: _mercado(s, t, False, a, b),
    "oficina": lambda s, t, a, b: _oficina(s, t, False, a, b),
    "escenario": lambda s, t, a, b: _escenario(s, t, False, a, b),
    "ciudad": lambda s, t, a, b: _ciudad(s, t, False, a, b),
    "bosque": lambda s, t, a, b: _bosque(s, t, False, a, b),
    "bosque_noche": lambda s, t, a, b: _bosque(s, t, True, a, b),
}


def background_svg(location: str, style: Style, t: float, cam_dx: float = 0.0) -> str:
    fn = LOCATIONS.get(location, LOCATIONS["calle_dia"])
    # parallax: capa lejana se mueve menos que la cámara
    body = fn(style, t, cam_dx * 0.55, cam_dx * 0.25)
    if style.night_boost and "noche" not in location:
        body += f'<rect width="{W}" height="{H}" fill="#2a0a5e" opacity="0.28"/>'
    return body


# --------------------------------------------------------------------------- objetos

def prop_svg(name: str, x: float, y: float, scale: float, t: float, anim: str | None, style: Style) -> str:
    dy = 0.0
    sx = 1.0
    if anim == "bounce":
        dy = -abs(math.sin(t * 5)) * 34
    elif anim == "float":
        dy = math.sin(t * 2.4) * 18
    elif anim == "spin":
        sx = math.cos(t * 6)
    elif anim == "pulse":
        scale *= 1 + 0.08 * math.sin(t * 6)
    g = f'<g transform="translate({x:.0f} {y + dy:.0f}) scale({scale * sx:.3f} {scale:.3f})">'
    o = f'stroke="{style.outline}" stroke-width="5" stroke-linejoin="round"'
    shapes = {
        "moneda": f'<circle r="42" fill="#ffd23f" {o}/><circle r="28" fill="none" stroke="#e0a800" stroke-width="5"/><text y="14" font-size="40" font-weight="bold" font-family="DejaVu Sans" text-anchor="middle" fill="#b07d00">$</text>',
        "bolsa": f'<path d="M-50,40 Q-70,-30 -25,-50 L25,-50 Q70,-30 50,40 Z" fill="#7bc96f" {o}/><path d="M-26,-50 L-34,-78 L34,-78 L26,-50" fill="#5ea657" {o}/><text y="22" font-size="58" font-weight="bold" font-family="DejaVu Sans" text-anchor="middle" fill="#2c6b2f">$</text>',
        "billete": f'<rect x="-70" y="-38" width="140" height="76" rx="8" fill="#fff3c4" {o}/><circle r="20" fill="#ffd23f" {o}/><text x="-52" y="-12" font-size="22" font-family="DejaVu Sans" font-weight="bold" fill="#8a6a00">№</text>',
        "corazon": f'<path d="M0,40 C-80,-20 -40,-80 0,-34 C40,-80 80,-20 0,40 Z" fill="#ff4d6d" {o}/>',
        "estrella": f'<polygon points="0,-48 14,-16 48,-14 22,8 31,42 0,23 -31,42 -22,8 -48,-14 -14,-16" fill="#ffd93b" {o}/>',
        "trofeo": f'<path d="M-40,-50 L40,-50 Q36,10 0,20 Q-36,10 -40,-50 Z" fill="#ffd23f" {o}/><rect x="-8" y="20" width="16" height="30" fill="#e0a800" {o}/><rect x="-34" y="50" width="68" height="16" rx="4" fill="#b07d00" {o}/>',
        "regalo": f'<rect x="-48" y="-30" width="96" height="76" fill="#4aa3ff" {o}/><rect x="-10" y="-30" width="20" height="76" fill="#ffd23f"/><rect x="-48" y="-52" width="96" height="26" fill="#2e86e8" {o}/><path d="M0,-52 Q-36,-96 -14,-62 Z M0,-52 Q36,-96 14,-62 Z" fill="#ffd23f" {o}/>',
        "microfono": f'<circle cy="-34" r="28" fill="#555" {o}/><rect x="-10" y="-8" width="20" height="70" rx="8" fill="#888" {o}/>',
        "cartel": f'<rect x="-8" y="0" width="16" height="140" fill="#8a5a2c"/><rect x="-100" y="-80" width="200" height="100" rx="10" fill="#fff" {o}/>',
        "pastel": f'<rect x="-60" y="-10" width="120" height="56" rx="8" fill="#ff9ebb" {o}/><rect x="-60" y="-30" width="120" height="26" rx="8" fill="#fff0f5" {o}/><rect x="-5" y="-62" width="10" height="34" fill="#ffd23f"/><ellipse cx="0" cy="-70" rx="8" ry="12" fill="#ff8c42"/>',
        "chocolate": f'<circle r="40" fill="#6b3e26" {o}/><circle r="26" fill="none" stroke="#c9a24a" stroke-width="5"/><text y="12" font-size="34" font-weight="bold" font-family="DejaVu Sans" text-anchor="middle" fill="#c9a24a">$</text>',
        "fantasma": f'<path d="M-50,50 L-50,-10 Q-50,-70 0,-70 Q50,-70 50,-10 L50,50 L30,34 L10,50 L-10,34 L-30,50 Z" fill="#f5f5ff" opacity="0.92" {o}/><circle cx="-18" cy="-18" r="9" fill="#222"/><circle cx="18" cy="-18" r="9" fill="#222"/><ellipse cy="12" rx="12" ry="16" fill="#222"/>',
        "cohete_caja": f'<rect x="-120" y="-200" width="240" height="260" rx="10" fill="#c9a06a" {o}/><polygon points="-120,-200 0,-300 120,-200" fill="#e04a3a" {o}/><circle cx="0" cy="-90" r="42" fill="#cfeaff" {o}/><text y="40" font-size="40" font-weight="bold" font-family="DejaVu Sans" text-anchor="middle" fill="#6d4a2b">COHETE</text>',
        "carrito": f'<rect x="-150" y="-60" width="300" height="130" rx="12" fill="#c9a06a" {o}/><rect x="-170" y="-100" width="340" height="44" rx="10" fill="#ffd23f" {o}/><rect x="-130" y="-300" width="260" height="120" rx="14" fill="#fff" {o}/><text y="-262" font-size="32" font-weight="bold" font-family="DejaVu Sans" text-anchor="middle" fill="#2b1d14">LIMONADA</text><text y="-228" font-size="30" font-weight="bold" font-family="DejaVu Sans" text-anchor="middle" fill="#2b1d14">LUNA LLENA</text><text y="-196" font-size="26" font-family="DejaVu Sans" text-anchor="middle" fill="#1e9d3a">100 % VERDAD</text><circle cx="-90" cy="76" r="28" fill="#555" {o}/><circle cx="90" cy="76" r="28" fill="#555" {o}/>',
        "bicicleta": f'<circle cx="-70" cy="20" r="46" fill="none" stroke="#2b1d14" stroke-width="9"/><circle cx="70" cy="20" r="46" fill="none" stroke="#2b1d14" stroke-width="9"/><path d="M-70,20 L-10,-50 L50,-50 L70,20 M-10,-50 L10,20 L-70,20" fill="none" stroke="#e04a3a" stroke-width="9" stroke-linejoin="round"/>',
        "luna_cartel": "",
    }
    return g + shapes.get(name, shapes["estrella"]) + "</g>"
