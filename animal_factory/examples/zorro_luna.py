"""Guion "El zorro que vendió la Luna": 6 escenas de ~10 s, escrito a mano (sin el generador).

Uso:  python examples/zorro_luna.py [salida] [borrador|final]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factory.characters.library import CHARACTERS
from factory.models import Beat, CameraKey, Line, Prop, Scene, SfxCue, Story
from factory.pipeline import Pipeline

CROWD = ["michi", "rocco", "lola", "pepe"]


def scene(i, title, loc, mood, lines, beats, sfx, props, cam, tr):
    cast = []
    for l in lines:
        if l.speaker != "narrador" and l.speaker not in cast:
            cast.append(l.speaker)
    for b in beats:
        if b.actor not in cast:
            cast.append(b.actor)
    return Scene(i, title, loc, mood, lines, beats, cast, camera=cam, sfx=[SfxCue(t, n) for t, n in sfx],
                 props=[Prop(*p) for p in props], transition=tr)


def build_story() -> Story:
    S = []
    # 1 · GANCHO INICIAL ------------------------------------------------------
    S.append(scene(1, "Última llamada", "calle_noche", "alegre",
        [Line("narrador", "Fausto vendió treinta y siete terrenos en la Luna. No era suya."),
         Line("fausto", "¡El cohete sale a medianoche! Voy a revisar los motores.", "happy")],
        [Beat("fausto", "idle", 0.0, 0.72, 540, 540, "happy"), Beat("fausto", "walk", 0.72, 1.0, 540, 1250),
         Beat("michi", "idle", 0.0, 0.4, 150, 150, "happy"), Beat("michi", "celebrate", 0.45, 1.0, 150, 150),
         Beat("rocco", "idle", 0.0, 0.5, 320, 320, "happy"), Beat("rocco", "celebrate", 0.5, 1.0, 320, 320),
         Beat("lola", "idle", 0.0, 0.4, 780, 780, "happy"), Beat("lola", "celebrate", 0.45, 1.0, 780, 780),
         Beat("pepe", "idle", 0.0, 0.5, 950, 950, "happy"), Beat("pepe", "celebrate", 0.5, 1.0, 950, 950)],
        [(0.05, "fanfare"), (0.5, "applause"), (0.74, "whoosh")],
        [("cohete_caja", 540, 1400, 1.0, None)],
        [CameraKey(0.0, "wide"), CameraKey(0.4, "medium", "fausto"), CameraKey(0.75, "wide")], "slideleft"))
    # 2 · SEGUNDO GANCHO ------------------------------------------------------
    S.append(scene(2, "El teléfono de medianoche", "oficina", "tenso",
        [Line("perla", "Fausto, compré tu lote uno. Fui notaria sesenta años: firmaste la estafa. "
                       "A medianoche llegan los vecinos y la patrulla.", "angry"),
         Line("fausto", "¿Dijo… medianoche?", "scared")],
        [Beat("fausto", "idle", 0.0, 0.45, 300, 300, "greedy"), Beat("fausto", "surprise", 0.45, 0.8, 300, 300),
         Beat("fausto", "shiver", 0.8, 1.0, 300, 300),
         Beat("perla", "idle", 0.0, 1.0, 800, 800, "happy", -1)],
        [(0.02, "ding"), (0.07, "ding"), (0.72, "gasp"), (0.9, "boom")],
        [("bolsa", 120, 1300, 1.0, None), ("bolsa", 190, 1330, 0.9, None), ("bolsa", 70, 1340, 0.8, None)],
        [CameraKey(0.0, "wide"), CameraKey(0.2, "medium", "perla"), CameraKey(0.72, "close", "fausto")], "fadeblack"))
    # 3 · DESARROLLO ----------------------------------------------------------
    S.append(scene(3, "Vendí mi bicicleta", "calle_noche", "misterioso",
        [Line("tomas", "Vendí mi bicicleta por mi lote. ¿Cómo se llega?", "happy"),
         Line("fausto", "Eh… saltando. Muy, muy alto.", "scared"),
         Line("narrador", "Y Tomás empezó a saltar.")],
        [Beat("fausto", "walk", 0.0, 0.25, -150, 520), Beat("fausto", "idle", 0.25, 1.0, 520, 520, "scared"),
         Beat("tomas", "idle", 0.0, 0.6, 800, 800, "happy", -1), Beat("tomas", "celebrate", 0.7, 1.0, 800, 800)],
        [(0.62, "boing"), (0.8, "jump"), (0.95, "ding")],
        [("bolsa", 330, 1320, 1.0, None), ("bolsa", 400, 1340, 0.9, None)],
        [CameraKey(0.0, "wide"), CameraKey(0.3, "medium", "tomas"), CameraKey(0.65, "close", "fausto")], "wipeleft"))
    # 4 · COMPLICACIÓN --------------------------------------------------------
    S.append(scene(4, "Treinta y siete denuncias", "parque_noche", "tenso",
        [Line("bruno", "Fausto. Treinta y siete denuncias. ¿Dónde está la Luna que vendiste?", "angry"),
         Line("fausto", "¡Ahí arriba, oficial! ¡Siempre estuvo arriba!", "scared")],
        [Beat("fausto", "shiver", 0.0, 1.0, 430, 430),
         Beat("bruno", "walk", 0.0, 0.3, 1300, 740), Beat("bruno", "idle", 0.3, 1.0, 740, 740, "angry", -1),
         Beat("michi", "angry", 0.0, 1.0, 130, 130), Beat("rocco", "angry", 0.0, 1.0, 270, 270),
         Beat("lola", "angry", 0.0, 1.0, 900, 900, None, -1), Beat("pepe", "angry", 0.0, 1.0, 1010, 1010, None, -1)],
        [(0.02, "siren"), (0.6, "gasp"), (0.9, "boom")], [],
        [CameraKey(0.0, "wide"), CameraKey(0.3, "medium", "bruno"), CameraKey(0.62, "close", "fausto")], "circleopen"))
    # 5 · GIRO INESPERADO -----------------------------------------------------
    S.append(scene(5, "La letra pequeña", "parque_noche", "triunfal",
        [Line("perla", "Cuando me vendiste el lote uno, firmaste mi recibo. "
                       "Letra pequeña: el vendedor devuelve cada moneda.", "happy"),
         Line("fausto", "¡Nadie lee la letra pequeña!", "scared"),
         Line("perla", "Yo sí.", "happy")],
        [Beat("perla", "walk", 0.0, 0.35, -150, 360), Beat("perla", "idle", 0.35, 1.0, 360, 360, "happy"),
         Beat("fausto", "idle", 0.0, 0.7, 720, 720, "scared", -1), Beat("fausto", "fall", 0.78, 1.0, 720, 720),
         Beat("bruno", "idle", 0.0, 1.0, 960, 960, "happy", -1),
         Beat("michi", "celebrate", 0.55, 1.0, 120, 120), Beat("rocco", "celebrate", 0.55, 1.0, 230, 230),
         Beat("lola", "celebrate", 0.55, 1.0, 840, 840), Beat("pepe", "celebrate", 0.55, 1.0, 1030, 1030)],
        [(0.05, "whoosh"), (0.5, "gasp"), (0.62, "cash"), (0.78, "thud"), (0.8, "applause"), (0.92, "fanfare")],
        [("billete", 560, 1000, 1.0, "float"), ("billete", 640, 900, 0.9, "float"), ("billete", 480, 1090, 0.9, "float"),
         ("billete", 780, 1050, 0.8, "float"), ("moneda", 600, 1250, 0.9, "spin"), ("moneda", 520, 1300, 0.8, "spin")],
        [CameraKey(0.0, "wide"), CameraKey(0.3, "medium", "perla"), CameraKey(0.7, "medium", "fausto"), CameraKey(0.85, "wide")],
        "zoomin"))
    # 6 · FINAL MEMORABLE -----------------------------------------------------
    S.append(scene(6, "Limonada Luna Llena", "parque", "alegre",
        [Line("narrador", "Fausto devolvió todo. Hoy vende limonada."),
         Line("tomas", "¿Una limonada, por favor?", "happy"),
         Line("fausto", "Con hielo lunar. Es verdad.", "happy"),
         Line("perla", "Lee antes de firmar. ¿Qué firmaste tú sin leer?", "happy")],
        [Beat("fausto", "idle", 0.0, 1.0, 470, 470, "happy"),
         Beat("tomas", "walk", 0.0, 0.3, -150, 220), Beat("tomas", "idle", 0.3, 1.0, 220, 220, "happy"),
         Beat("perla", "idle", 0.0, 1.0, 960, 960, "happy", -1)],
        [(0.3, "ding"), (0.55, "sparkle"), (0.95, "ding")],
        [("carrito", 740, 1320, 0.95, None), ("bicicleta", 90, 1380, 1.0, None)],
        [CameraKey(0.0, "wide"), CameraKey(0.3, "medium", "tomas"), CameraKey(0.55, "medium", "fausto"), CameraKey(0.78, "close", "perla")],
        "fade"))

    ids = {"fausto", "perla", "tomas", "bruno", *CROWD}
    return Story(idea="El zorro que vendió la Luna", title="El zorro que vendió la Luna", theme="mentiras",
                 message="Lee antes de firmar.", characters={c: CHARACTERS[c] for c in ids}, scenes=S)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "salida_zorro_luna")
    quality = sys.argv[2] if len(sys.argv) > 2 else "final"
    story = build_story()

    def prog(stage, pct, msg):
        print(f"[{pct * 100:3.0f}%] {stage}: {msg}", flush=True)
    res = Pipeline().run(story, out, style="cartoon", quality=quality, progress=prog)
    print("VIDEO", res.video, f"{res.duration:.1f}s", res.warnings)
    print([round(s.duration, 1) for s in story.scenes])
