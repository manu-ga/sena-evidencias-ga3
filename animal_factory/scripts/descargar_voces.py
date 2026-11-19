#!/usr/bin/env python3
"""Descarga las voces de Piper en español latino (gratis, ~240 MB en total).

Uso:  python scripts/descargar_voces.py            # las tres voces
      python scripts/descargar_voces.py --lista    # ver voces disponibles
Las voces vienen de https://huggingface.co/rhasspy/piper-voices (licencias en cada ficha).
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
VOCES = {
    "es_MX-ald-medium": "es/es_MX/ald/medium",
    "es_MX-claude-high": "es/es_MX/claude/high",
    "es_AR-daniela-high": "es/es_AR/daniela/high",
}
DEST = Path(__file__).resolve().parent.parent / "models"
MIN_BYTES = {"onnx": 10_000_000, "json": 1_000}


def bajar(url: str, destino: Path, minimo: int) -> None:
    if destino.exists() and destino.stat().st_size >= minimo:
        print(f"  ya existe: {destino.name}")
        return
    tmp = destino.with_suffix(destino.suffix + ".part")
    print(f"  descargando {destino.name} …", flush=True)
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    if tmp.stat().st_size < minimo:
        tmp.unlink()
        raise RuntimeError(f"Descarga incompleta de {url}")
    tmp.replace(destino)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lista", action="store_true")
    ap.add_argument("--destino", type=Path, default=DEST)
    a = ap.parse_args()
    if a.lista:
        print("\n".join(VOCES))
        return 0
    a.destino.mkdir(parents=True, exist_ok=True)
    for nombre, ruta in VOCES.items():
        print(nombre)
        try:
            bajar(f"{BASE}/{ruta}/{nombre}.onnx", a.destino / f"{nombre}.onnx", MIN_BYTES["onnx"])
            bajar(f"{BASE}/{ruta}/{nombre}.onnx.json", a.destino / f"{nombre}.onnx.json", MIN_BYTES["json"])
        except Exception as e:
            print(f"  ERROR: {e}\n  ¿Tu red permite huggingface.co y us.aws.cdn.hf.co?", file=sys.stderr)
            return 1
    print("Listo. Voces en", a.destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
