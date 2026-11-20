"""Configuración central: rutas, calidades de render y constantes."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = Path(os.environ.get("FACTORY_MODELS_DIR", ROOT / "models"))
OUTPUT_DIR = Path(os.environ.get("FACTORY_OUTPUT_DIR", ROOT / "output"))
JOBS_DIR = OUTPUT_DIR / "jobs"

WORLD_W, WORLD_H = 1080, 1920          # lienzo vertical 9:16
GROUND_Y = 1380                        # donde pisan los personajes
TARGET_SECONDS = 60.0
SCENE_MIN, SCENE_MAX = 8.0, 10.0
TRANSITION = 0.5                       # segundos de transición entre escenas
AUDIO_SR = 44100

# Calidades: "final" cumple 1080x1920. "borrador" sirve para probar rápido.
QUALITY = {
    "final":    {"width": 1080, "height": 1920, "fps": 24, "crf": 20},
    "borrador": {"width": 540,  "height": 960,  "fps": 12, "crf": 26},
}

# Clave opcional para proteger la app cuando está en internet.
ACCESS_CODE = os.environ.get("FACTORY_ACCESS_CODE", "")
