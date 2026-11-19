"""Tramas escritas a mano. Cada trama devuelve 7 escenas con diálogos, acciones y efectos.

Roles: H = protagonista, F = amigo/a, R = rival/estafador, P = figura de autoridad/consejero.
Una escena se describe con S(...): título, lugar, ánimo, líneas, acciones, efectos, objetos y cámara.
Límite de diseño: ~20 palabras por escena para que quepan en 8-10 s de voz.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Names:
    H: str
    F: str
    R: str
    P: str
    Ho: str   # "o" o "a" para concordar adjetivos del protagonista
    Fo: str
    Ro: str
    Po: str
    goal: str = "cumplir su sueño"


@dataclass
class SceneDef:
    title: str
    location: str
    mood: str
    lines: list          # (rol | "N", texto, emoción)
    beats: list          # (rol, acción, t0, t1, x0, x1, emo, face)
    sfx: list            # (t, nombre)
    props: list          # (nombre, x, y, escala, anim)
    cam: list | None
    tr: str


def S(title, loc, mood, lines, beats, sfx=(), props=(), cam=None, tr="fade") -> SceneDef:
    return SceneDef(title, loc, mood, list(lines), list(beats), list(sfx), list(props), cam, tr)


def B(role, action, t0, t1, x0, x1=None, emo=None, face=None):
    return (role, action, t0, t1, x0, x1, emo, face)


# ---------------------------------------------------------------- DINERO / AMBICIÓN

def millonario(n: Names) -> tuple[list[str], str, list[SceneDef]]:
    titles = [f"{n.H} y el billete mágico", f"El millón de {n.H}", f"{n.H} quiere ser millonari{n.Ho}"]
    msg = "Lo que parece demasiado bueno para ser verdad, casi nunca lo es."
    scenes = [
        S("Tres monedas y un sueño", "calle_dia", "alegre",
          [("N", f"{n.H} tenía tres monedas, una deuda y un sueño: ser millonari{n.Ho}.", "neutral"),
           ("H", "¡Hoy dejo de ser pobre… después del almuerzo!", "happy")],
          [B("H", "walk", 0.0, 0.32, -150, 420), B("H", "jump", 0.36, 0.6, 420, 470),
           B("H", "idle", 0.6, 1.0, 470, 470, "greedy")],
          [(0.38, "jump"), (0.55, "coin"), (0.6, "coin")],
          [("moneda", 700, 1240, 1.0, "spin"), ("moneda", 840, 1300, 0.8, "spin")],
          [(0.0, "wide", None, False), (0.45, "medium", "H", False)], "slideleft"),
        S("La oferta imposible", "calle_noche", "misterioso",
          [("R", "Psss… billete premiado. Ganó ayer, y hoy gana otra vez.", "neutral"),
           ("H", "¿Cuánto cuesta?", "surprised"),
           ("R", "Solo todo lo que tienes.", "neutral")],
          [B("R", "walk", 0.0, 0.25, 1300, 760), B("R", "idle", 0.25, 1.0, 760, 760),
           B("H", "idle", 0.0, 0.5, 300, 300, "surprised"), B("H", "idle", 0.5, 1.0, 300, 300, "greedy")],
          [(0.02, "whoosh"), (0.3, "sparkle"), (0.92, "ding")],
          [("billete", 620, 1020, 1.1, "float")],
          [(0.0, "wide", None, False), (0.3, "medium", "R", False), (0.7, "close", "H", False)], "fadeblack"),
        S("Los amigos avisan", "parque", "alegre",
          [("F", f"¡{n.H}, eso es un billete de autobús del año ochenta!", "surprised"),
           ("H", "Es de colección. Los millonarios coleccionan cosas viejas.", "happy")],
          [B("F", "walk", 0.0, 0.25, 1300, 740), B("F", "idle", 0.25, 0.6, 740, 740, "surprised"),
           B("F", "shrug", 0.6, 1.0, 740, 740), B("H", "idle", 0.0, 1.0, 320, 320, "happy")],
          [(0.05, "whoosh"), (0.55, "boing")], [("billete", 360, 1000, 0.9, "float")],
          [(0.0, "wide", None, False), (0.3, "medium", "F", False)], "slideright"),
        S("El gran sorteo", "escenario", "tenso",
          [("N", f"Llegó el sorteo… y {n.H} no ganó.", "neutral"),
           ("P", "Billete de autobús. Y debe tres meses de renta.", "angry")],
          [B("H", "idle", 0.0, 0.7, 300, 300, "surprised"), B("H", "run", 0.78, 1.0, 300, -200),
           B("P", "idle", 0.0, 1.0, 780, 780, "angry")],
          [(0.05, "fanfare"), (0.5, "sad"), (0.78, "whoosh")], [("trofeo", 540, 1050, 0.9, "float")],
          [(0.0, "wide", None, False), (0.45, "medium", "P", False)], "wipeleft"),
        S("Un negocio muy familiar", "mercado", "tenso",
          [("H", "¡Espera! ¡Aquí hay mil billetes iguales al mío!", "surprised"),
           ("R", "Shhh. ¡Es un negocio familiar!", "scared"),
           ("N", "Había estafado a todo el pueblo.", "neutral")],
          [B("H", "run", 0.0, 0.22, -200, 380), B("H", "surprise", 0.22, 1.0, 380, 380),
           B("R", "idle", 0.0, 1.0, 780, 780, "scared")],
          [(0.0, "whoosh"), (0.22, "crash"), (0.7, "gasp")],
          [("billete", 640, 1000, 0.8, "float"), ("billete", 760, 1060, 0.8, "float"), ("billete", 900, 1010, 0.8, "float"),
           ("bolsa", 960, 1290, 1.0, None)],
          [(0.0, "wide", None, False), (0.3, "medium", "H", False)], "circleopen"),
        S("La firma delatora", "calle_noche", "triunfal",
          [("P", f"{n.R}, queda arrestad{n.Ro}. Sus billetes llevaban su firma.", "angry"),
           ("R", "¡Firmo todo por costumbre!", "scared"),
           ("P", f"Recompensa para {n.H}: ¡un millón de monedas!", "happy")],
          [B("P", "walk", 0.0, 0.25, 1300, 700), B("P", "idle", 0.25, 1.0, 700, 700),
           B("R", "shiver", 0.0, 0.7, 880, 880, "scared"), B("R", "fall", 0.7, 1.0, 880, 880),
           B("H", "celebrate", 0.65, 1.0, 330, 330)],
          [(0.05, "siren"), (0.7, "thud"), (0.85, "cash"), (0.92, "fanfare")], [("bolsa", 330, 1290, 1.2, "bounce")],
          [(0.0, "wide", None, False), (0.3, "medium", "P", False), (0.7, "medium", "H", False)], "zoomin"),
        S("Moraleja de chocolate", "atardecer", "triunfal",
          [("N", "Eran de chocolate.", "neutral"),
           ("H", f"Soy millonari{n.Ho}… y tengo dolor de muelas.", "sad"),
           ("N", "Moraleja: si parece demasiado bueno, desconfía.", "neutral")],
          [B("H", "idle", 0.0, 1.0, 400, 400, "sad"), B("F", "laugh", 0.0, 1.0, 700, 700)],
          [(0.05, "sad"), (0.95, "ding")],
          [("chocolate", 520, 1320, 1.0, "bounce"), ("chocolate", 600, 1350, 0.8, "bounce")],
          [(0.0, "medium", "H", False), (0.8, "wide", None, False)], "fade"),
    ]
    return titles, msg, scenes


# ---------------------------------------------------------------- AMOR

def amor(n: Names):
    titles = [f"{n.H} y las hojas del amor", f"La serenata de {n.H}", f"{n.H} enamorad{n.Ho}"]
    msg = "Ser tú mismo enamora más que presumir."
    scenes = [
        S("Hola… ¡hojas!", "parque", "alegre",
          [("N", f"{n.H} llevaba tres semanas intentando hablarle a {n.F}.", "neutral"),
           ("H", "Hoy se lo digo… Hola, ho… ¡hojas! ¡Qué lindas hojas!", "scared")],
          [B("H", "walk", 0.0, 0.4, -150, 400), B("H", "idle", 0.4, 1.0, 400, 400, "love"),
           B("F", "idle", 0.0, 1.0, 780, 780, "happy")],
          [(0.5, "heart")], [("corazon", 560, 900, 0.7, "float")],
          [(0.0, "wide", None, False), (0.45, "medium", "H", False)], "slideleft"),
        S("El rival presumido", "parque", "tenso",
          [("R", f"Tengo flores, guitarra y auto. ¿Y tú, {n.H}?", "happy"),
           ("H", "Una moneda… y muchas ganas.", "sad"),
           ("R", "Mañana le doy un anillo.", "greedy")],
          [B("R", "walk", 0.0, 0.25, 1300, 620), B("R", "idle", 0.25, 1.0, 620, 620, "greedy"),
           B("H", "idle", 0.0, 1.0, 280, 280, "sad"), B("F", "shrug", 0.3, 1.0, 880, 880)],
          [(0.02, "whoosh"), (0.5, "sad"), (0.85, "sparkle")], [("regalo", 640, 1300, 0.9, "bounce")],
          [(0.0, "wide", None, False), (0.3, "medium", "R", False), (0.6, "medium", "H", False)], "fadeblack"),
        S("Consejos peligrosos", "casa", "alegre",
          [("H", f"Necesito un plan para conquistar a {n.F}.", "scared"),
           ("P", "Regla uno: sé tú mismo. Regla dos: que no se note.", "happy")],
          [B("H", "idle", 0.0, 1.0, 330, 330, "thinking"), B("P", "idle", 0.0, 1.0, 760, 760, "happy")],
          [(0.5, "ding"), (0.9, "boing")], [],
          [(0.0, "wide", None, False), (0.35, "medium", "P", False)], "slideright"),
        S("La serenata", "calle_noche", "alegre",
          [("N", f"Esa noche, {n.H} cantó una serenata usando una olla como guitarra.", "neutral"),
           ("H", "¡Ay, ay, ay, mi amooor!", "happy")],
          [B("H", "dance", 0.0, 1.0, 330, 430), B("F", "idle", 0.0, 0.5, 820, 820, "surprised"),
           B("F", "laugh", 0.5, 1.0, 820, 820)],
          [(0.2, "knock"), (0.55, "crash"), (0.75, "thud")], [("corazon", 780, 900, 0.6, "float")],
          [(0.0, "wide", None, False), (0.5, "medium", "H", False)], "wipeleft"),
        S("Las flores robadas", "parque_noche", "misterioso",
          [("R", "Para ti, mis flores.", "happy"),
           ("F", "Son mis flores… ¡con mi nombre en la etiqueta!", "angry"),
           ("R", "¡Yo ya me voy!", "scared")],
          [B("R", "idle", 0.0, 0.5, 600, 600, "happy"), B("R", "run", 0.62, 1.0, 600, 1350),
           B("F", "angry", 0.15, 1.0, 860, 860), B("H", "idle", 0.0, 1.0, 280, 280, "surprised")],
          [(0.1, "sparkle"), (0.35, "gasp"), (0.62, "whoosh")], [("regalo", 620, 1300, 0.8, None)],
          [(0.0, "wide", None, False), (0.35, "medium", "F", False)], "circleopen"),
        S("El sí con tapones", "atardecer", "triunfal",
          [("F", f"{n.H}, nadie nunca cantó tan mal por mí.", "happy"),
           ("H", "¿Eso es… un sí?", "scared"),
           ("F", "Sí… pero con tapones.", "happy")],
          [B("H", "idle", 0.0, 1.0, 400, 400, "love"), B("F", "idle", 0.0, 1.0, 700, 700, "love")],
          [(0.4, "heart"), (0.9, "fanfare")], [("corazon", 560, 1000, 1.0, "pulse")],
          [(0.0, "medium", None, False), (0.7, "close", "H", False)], "zoomin"),
        S("Moraleja", "atardecer", "triunfal",
          [("N", f"{n.H} y {n.F} fueron felices. Los pájaros, en cambio, se mudaron.", "neutral"),
           ("N", "Moraleja: ser tú mismo enamora más que presumir.", "neutral")],
          [B("H", "dance", 0.0, 1.0, 400, 480), B("F", "dance", 0.0, 1.0, 700, 640)],
          [(0.1, "sparkle"), (0.9, "ding")], [("estrella", 540, 800, 0.8, "float"), ("corazon", 740, 880, 0.6, "float")],
          [(0.0, "wide", None, False), (0.6, "medium", None, False)], "fade"),
    ]
    return titles, msg, scenes


# ---------------------------------------------------------------- FAMA / TALENTO

def fama(n: Names):
    titles = [f"{n.H}, la estrella desafinada", f"El gran concurso de {n.H}", f"{n.H} quiere ser famos{n.Ho}"]
    msg = "Tu talento no siempre es el que soñaste; a veces es el que el mundo necesita."
    scenes = [
        S("Una voz de tesoro", "casa", "alegre",
          [("N", f"{n.H} soñaba con ser la estrella del mundo.", "neutral"),
           ("H", "¡Mi voz es un tesoro!", "happy"),
           ("F", "Un tesoro… que debería estar enterrado.", "sad")],
          [B("H", "dance", 0.0, 1.0, 340, 420), B("F", "shiver", 0.3, 1.0, 800, 800)],
          [(0.5, "crash"), (0.8, "knock")], [("microfono", 330, 1220, 0.9, None)],
          [(0.0, "wide", None, False), (0.4, "medium", "H", False)], "slideleft"),
        S("El anuncio", "escenario", "tenso",
          [("P", "Gran concurso de talentos. Premio: un millón de aplausos… y un sándwich.", "happy"),
           ("R", "Yo ya gané diez años seguidos.", "greedy")],
          [B("P", "idle", 0.0, 1.0, 330, 330, "happy"), B("R", "idle", 0.0, 1.0, 780, 780, "greedy")],
          [(0.05, "fanfare"), (0.7, "ding")], [("trofeo", 540, 1050, 1.0, "float")],
          [(0.0, "wide", None, False), (0.55, "medium", "R", False)], "fadeblack"),
        S("Un plan distinto", "parque", "alegre",
          [("F", f"{n.H}, cantar no es lo tuyo. ¿Y si haces reír?", "happy"),
           ("H", "¿Con mi voz? ¡Ya lo hago sin querer!", "surprised")],
          [B("F", "idle", 0.0, 1.0, 760, 760, "happy"), B("H", "think", 0.0, 0.6, 330, 330), B("H", "laugh", 0.6, 1.0, 330, 330)],
          [(0.5, "ding"), (0.8, "boing")], [],
          [(0.0, "wide", None, False), (0.4, "medium", "F", False)], "slideright"),
        S("A escena", "escenario", "tenso",
          [("N", f"Llegó la noche. {n.H} salió al escenario con el micrófono temblando.", "neutral"),
           ("H", "¡Laaa… la laaaaaa!", "happy")],
          [B("H", "walk", 0.0, 0.3, -150, 470), B("H", "dance", 0.45, 1.0, 470, 470),
           B("P", "idle", 0.0, 1.0, 880, 880, "surprised")],
          [(0.4, "gasp"), (0.7, "crash")], [("microfono", 470, 1220, 0.9, None)],
          [(0.0, "wide", None, False), (0.5, "close", "H", False)], "wipeleft"),
        S("La risa del público", "escenario", "triunfal",
          [("R", "¡No! ¡Todos se están riendo!", "scared"),
           ("N", f"El público lloraba de risa. {n.R} se resbaló.", "neutral")],
          [B("R", "idle", 0.0, 0.5, 780, 780, "scared"), B("R", "fall", 0.55, 1.0, 780, 780),
           B("H", "laugh", 0.0, 1.0, 330, 330)],
          [(0.2, "applause"), (0.62, "crash"), (0.7, "thud")], [],
          [(0.0, "wide", None, False), (0.55, "medium", "R", False)], "circleopen"),
        S("El premio", "escenario", "triunfal",
          [("P", f"¡Premio al artista más divertido: {n.H}!", "happy"),
           ("H", "¿Me aplauden… o se tapan los oídos?", "surprised")],
          [B("P", "celebrate", 0.0, 1.0, 780, 780), B("H", "celebrate", 0.0, 1.0, 330, 330)],
          [(0.05, "fanfare"), (0.3, "applause")], [("trofeo", 540, 1000, 1.2, "bounce"), ("estrella", 200, 800, 0.7, "float"), ("estrella", 880, 760, 0.7, "float")],
          [(0.0, "wide", None, False), (0.5, "medium", "H", False)], "zoomin"),
        S("Moraleja", "atardecer", "triunfal",
          [("N", f"{n.H} no fue cantante: fue el artista más divertido del país.", "neutral"),
           ("N", "Moraleja: tu talento puede ser otro.", "neutral")],
          [B("H", "dance", 0.0, 1.0, 400, 460), B("F", "laugh", 0.0, 1.0, 740, 740)],
          [(0.1, "sparkle"), (0.9, "ding")], [("estrella", 540, 800, 0.9, "float")],
          [(0.0, "wide", None, False), (0.6, "medium", "H", False)], "fade"),
    ]
    return titles, msg, scenes


# ---------------------------------------------------------------- VALENTÍA / MIEDO

def valentia(n: Names):
    titles = [f"{n.H} y el fantasma hambriento", f"La noche más larga de {n.H}", f"{n.H} no tiene miedo (mentira)"]
    msg = "El miedo se hace pequeño cuando lo miras a la cara."
    scenes = [
        S("Miedo a todo", "casa_noche", "misterioso",
          [("N", f"{n.H} tenía miedo de todo: la oscuridad, las arañas… y las ensaladas.", "neutral"),
           ("H", "¡Hay un monstruo debajo de mi cama!", "scared")],
          [B("H", "shiver", 0.0, 1.0, 420, 420)],
          [(0.4, "knock"), (0.7, "gasp")], [],
          [(0.0, "wide", None, False), (0.5, "close", "H", False)], "slideleft"),
        S("El campamento", "bosque_noche", "misterioso",
          [("F", f"{n.H}, hoy dormimos en el bosque. Dicen que aquí vive un fantasma.", "happy"),
           ("H", "¿Un… fantasma? ¡Yo me quedo lejísimos!", "scared")],
          [B("F", "walk", 0.0, 0.3, 1300, 740), B("F", "idle", 0.3, 1.0, 740, 740, "happy"),
           B("H", "shiver", 0.0, 1.0, 300, 300)],
          [(0.05, "whoosh"), (0.6, "gasp")], [("fantasma", 940, 980, 0.8, "float")],
          [(0.0, "wide", None, False), (0.35, "medium", "F", False)], "fadeblack"),
        S("Algo flota", "bosque_noche", "tenso",
          [("N", "A medianoche, algo empezó a flotar entre los árboles.", "neutral"),
           ("F", "¡Yo me escondo! ¡Tú eres el valiente!", "scared")],
          [B("H", "surprise", 0.0, 1.0, 320, 320), B("F", "run", 0.5, 0.8, 740, 1350)],
          [(0.1, "boom"), (0.5, "gasp"), (0.52, "whoosh")], [("fantasma", 700, 960, 1.2, "float")],
          [(0.0, "wide", None, False), (0.6, "medium", "H", False)], "wipeleft"),
        S("El fantasma habla", "bosque_noche", "tenso",
          [("R", "¡Buuu! ¡Denme su comida o los asusto!", "angry"),
           ("H", "¡Un fantasma… pidiendo almuerzo!", "scared")],
          [B("H", "shiver", 0.0, 1.0, 300, 300)],
          [(0.05, "boom"), (0.5, "gasp")], [("fantasma", 700, 960, 1.4, "float")],
          [(0.0, "medium", "H", False), (0.5, "close", "H", False)], "circleopen"),
        S("Sin sábana", "bosque_noche", "triunfal",
          [("H", "Un momento. Este fantasma huele a fritanga.", "thinking"),
           ("R", "¡Me descubrieron! ¡Corro!", "scared")],
          [B("H", "idle", 0.0, 0.5, 400, 400, "thinking"), B("H", "angry", 0.5, 1.0, 400, 400),
           B("R", "idle", 0.35, 0.7, 780, 780, "scared"), B("R", "run", 0.7, 1.0, 780, 1350)],
          [(0.35, "pop"), (0.7, "whoosh")], [],
          [(0.0, "medium", "H", False), (0.4, "wide", None, False)], "zoomin"),
        S("El valiente", "bosque_noche", "triunfal",
          [("F", f"¡{n.H} venció al fantasma!", "happy"),
           ("H", "Los fantasmas no existen. ¡Pero sí los ladrones de comida!", "happy")],
          [B("H", "celebrate", 0.0, 1.0, 400, 400), B("F", "celebrate", 0.0, 1.0, 700, 700)],
          [(0.1, "fanfare"), (0.5, "applause")], [("estrella", 540, 800, 0.9, "float")],
          [(0.0, "wide", None, False), (0.5, "medium", "H", False)], "slideright"),
        S("Moraleja", "atardecer", "triunfal",
          [("N", f"{n.H} durmió sin miedo. Bueno… con la luz prendida.", "neutral"),
           ("N", "Moraleja: el miedo se achica si lo miras de frente.", "neutral")],
          [B("H", "idle", 0.0, 1.0, 420, 420, "happy"), B("F", "laugh", 0.0, 1.0, 720, 720)],
          [(0.1, "sparkle"), (0.9, "ding")], [("estrella", 540, 800, 0.9, "float")],
          [(0.0, "wide", None, False), (0.6, "medium", "H", False)], "fade"),
    ]
    return titles, msg, scenes


# ---------------------------------------------------------------- SUPERACIÓN (genérica)

def sueno(n: Names):
    titles = [f"{n.H} no se rinde", f"El sueño de {n.H}", f"{n.H} y el día imposible"]
    msg = "Fracasar es solo el ensayo del éxito."
    g = n.goal
    scenes = [
        S("Un sueño enorme", "calle_dia", "alegre",
          [("N", f"{n.H} tenía un sueño: {g}.", "neutral"),
           ("H", "¡Lo voy a lograr hoy mismo!", "happy")],
          [B("H", "walk", 0.0, 0.35, -150, 420), B("H", "celebrate", 0.5, 1.0, 420, 420)],
          [(0.5, "boing"), (0.85, "sparkle")], [("estrella", 700, 900, 0.9, "float")],
          [(0.0, "wide", None, False), (0.45, "medium", "H", False)], "slideleft"),
        S("Las dudas", "parque", "tenso",
          [("R", "Jamás lo lograrás. Mejor ríndete ahora.", "angry"),
           ("H", "¿Y si te equivocas tú?", "angry")],
          [B("R", "walk", 0.0, 0.25, 1300, 740), B("R", "idle", 0.25, 1.0, 740, 740, "angry"),
           B("H", "idle", 0.0, 1.0, 320, 320, "angry")],
          [(0.05, "whoosh"), (0.5, "boom")], [],
          [(0.0, "wide", None, False), (0.3, "medium", "R", False), (0.7, "medium", "H", False)], "fadeblack"),
        S("Primer intento", "mercado", "alegre",
          [("N", f"El primer intento fue un desastre. {n.H} terminó en el suelo.", "neutral"),
           ("H", "Eso fue… un ensayo general.", "sad")],
          [B("H", "run", 0.0, 0.3, -100, 420), B("H", "fall", 0.35, 1.0, 420, 420)],
          [(0.3, "crash"), (0.4, "thud")], [],
          [(0.0, "wide", None, False), (0.4, "medium", "H", False)], "wipeleft"),
        S("Casi lo logra", "parque", "tenso",
          [("N", "El segundo intento fue peor. El tercero, todavía peor.", "neutral"),
           ("F", f"{n.H}, descansa un poco. Tu sueño sigue aquí.", "sad")],
          [B("H", "cry", 0.0, 1.0, 340, 340), B("F", "walk", 0.0, 0.3, 1300, 720), B("F", "idle", 0.3, 1.0, 720, 720, "sad")],
          [(0.1, "sad"), (0.4, "whoosh")], [],
          [(0.0, "medium", "H", False), (0.5, "medium", "F", False)], "circleopen"),
        S("El truco", "atardecer", "misterioso",
          [("F", "Los que lo logran no son los mejores. Son los que insisten una vez más.", "happy"),
           ("H", "¡Una vez más!", "happy")],
          [B("F", "idle", 0.0, 1.0, 720, 720, "happy"), B("H", "idle", 0.0, 0.5, 340, 340, "sad"), B("H", "celebrate", 0.5, 1.0, 340, 340)],
          [(0.5, "ding"), (0.6, "sparkle")], [("estrella", 540, 820, 0.8, "pulse")],
          [(0.0, "wide", None, False), (0.5, "close", "H", False)], "zoomin"),
        S("Lo logró", "ciudad", "triunfal",
          [("N", f"Esta vez, {n.H} no se detuvo. Y lo consiguió.", "neutral"),
           ("H", "¡Lo logré! ¡Lo logré de verdad!", "happy")],
          [B("H", "celebrate", 0.0, 1.0, 450, 450), B("F", "celebrate", 0.0, 1.0, 750, 750), B("R", "idle", 0.0, 1.0, 960, 960, "surprised")],
          [(0.1, "fanfare"), (0.5, "applause")], [("trofeo", 540, 1000, 1.1, "bounce")],
          [(0.0, "wide", None, False), (0.5, "medium", "H", False)], "slideright"),
        S("Moraleja", "atardecer", "triunfal",
          [("N", f"{n.R} no volvió a dudar. Aprendió algo importante.", "neutral"),
           ("N", "Moraleja: fracasar es solo el ensayo del éxito.", "neutral")],
          [B("H", "idle", 0.0, 1.0, 420, 420, "happy"), B("F", "laugh", 0.0, 1.0, 720, 720)],
          [(0.1, "sparkle"), (0.9, "ding")], [("estrella", 540, 800, 0.9, "float")],
          [(0.0, "wide", None, False), (0.6, "medium", "H", False)], "fade"),
    ]
    return titles, msg, scenes


PLOTS = {
    "dinero": millonario,
    "amor": amor,
    "fama": fama,
    "valentia": valentia,
    "superacion": sueno,
}

THEME_LABEL = {
    "dinero": "dinero y ambición",
    "amor": "amor",
    "fama": "fama y talento",
    "valentia": "miedo y valentía",
    "superacion": "superación",
}

# Preferencias de reparto por tema: (amigo, rival, autoridad)
CAST_PREFS = {
    "dinero": (["lola", "rocco", "pepe"], ["fausto", "pancho"], ["bruno", "pancho"]),
    "amor": (["lola", "rita"], ["fausto", "pancho"], ["pepe", "bruno", "rocco"]),
    "fama": (["pepe", "rocco", "lola"], ["fausto", "pancho"], ["bruno", "pancho", "rita"]),
    "valentia": (["pepe", "rocco", "lola"], ["fausto", "pancho"], ["bruno"]),
    "superacion": (["lola", "rocco", "pepe"], ["pancho", "fausto"], ["bruno"]),
}
