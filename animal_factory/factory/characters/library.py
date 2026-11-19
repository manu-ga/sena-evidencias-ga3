"""Biblioteca de personajes fijos. Cada uno conserva diseño, colores, ropa y voz."""
from __future__ import annotations

from ..models import CharacterSpec

V_ALD = "es_MX-ald-medium"
V_CLAUDE = "es_MX-claude-high"
V_DANIELA = "es_AR-daniela-high"

NARRATOR_VOICE = V_ALD

CHARACTERS: dict[str, CharacterSpec] = {c.id: c for c in [
    CharacterSpec(
        id="michi", name="Michi", species="gato", gender="m",
        personality="soñador y travieso",
        fur="#f0a14a", fur_dark="#c8742a", belly="#fff1d6",
        outfit="camiseta", outfit_color="#3aa76d", accent="#ffd23f",
        accessory="bufanda", eye_color="#2e7d32",
        voice=V_ALD, pitch=1.12, rate=0.97, color="#ffd27a"),
    CharacterSpec(
        id="rocco", name="Rocco", species="perro", gender="m",
        personality="leal y algo torpe",
        fur="#a9734a", fur_dark="#6d4524", belly="#f4dfc0",
        outfit="sudadera", outfit_color="#3b6fd4", accent="#e74c3c",
        accessory="gorra", eye_color="#4e342e",
        voice=V_ALD, pitch=0.92, rate=1.04, color="#9fc2ff"),
    CharacterSpec(
        id="fausto", name="Fausto", species="zorro", gender="m",
        personality="astuto y encantador",
        fur="#e8622a", fur_dark="#a8401a", belly="#fff4e6",
        outfit="traje", outfit_color="#1f8a5b", accent="#f1c40f",
        accessory="sombrero", eye_color="#f39c12",
        voice=V_CLAUDE, pitch=0.82, rate=1.02, color="#ff9d7a"),
    CharacterSpec(
        id="lola", name="Lola", species="conejo", gender="f",
        personality="lista, dulce y directa",
        fur="#f4f1ee", fur_dark="#c9c3bd", belly="#ffd9e3",
        outfit="vestido", outfit_color="#ec6fa5", accent="#ffffff",
        accessory="moño", eye_color="#c2185b",
        voice=V_DANIELA, pitch=1.1, rate=0.98, color="#ffb3d4"),
    CharacterSpec(
        id="bruno", name="Bruno", species="oso", gender="m",
        personality="serio, noble y pesado al caminar",
        fur="#8a5a3c", fur_dark="#5d3a24", belly="#d9b48a",
        outfit="chaleco", outfit_color="#2c4a8a", accent="#ffd23f",
        accessory="gorra", eye_color="#3e2723",
        voice=V_ALD, pitch=0.76, rate=1.08, scale=1.12, color="#a8c0ff"),
    CharacterSpec(
        id="pancho", name="Pancho", species="cerdo", gender="m",
        personality="pomposo y ambicioso",
        fur="#f7a8b8", fur_dark="#e07b94", belly="#fbc7d2",
        outfit="traje", outfit_color="#596275", accent="#c0392b",
        accessory="gafas", eye_color="#37474f",
        voice=V_CLAUDE, pitch=0.9, rate=1.05, scale=1.05, color="#ffc2d0"),
    CharacterSpec(
        id="rita", name="Rita", species="rana", gender="f",
        personality="dramática y artista",
        fur="#5fbf5a", fur_dark="#3c8f3a", belly="#e8f5c8",
        outfit="vestido", outfit_color="#8e5bd0", accent="#ffd23f",
        accessory="moño", eye_color="#1b5e20",
        voice=V_DANIELA, pitch=1.26, rate=0.95, color="#b8f09a"),
    CharacterSpec(
        id="perla", name="Doña Perla", species="tortuga", gender="f",
        personality="anciana serena y muy aguda",
        fur="#9ccc65", fur_dark="#2f6b3a", belly="#e6f2c8",
        outfit="chal", outfit_color="#8e5bd0", accent="#ffd23f",
        accessory="gafas", eye_color="#33691e",
        voice=V_DANIELA, pitch=0.88, rate=1.12, scale=0.82, color="#d3b3ff"),
    CharacterSpec(
        id="tomas", name="Tomás", species="conejo", gender="m",
        personality="ilusionado y confiado",
        fur="#f4f1ee", fur_dark="#b9b2ad", belly="#ffd9e3",
        outfit="overol", outfit_color="#2f6fd1", accent="#ffd23f",
        accessory="mochila", eye_color="#3e2723",
        voice=V_ALD, pitch=1.38, rate=0.95, scale=0.8, color="#a5d8ff"),
    CharacterSpec(
        id="pepe", name="Pepe", species="raton", gender="m",
        personality="nervioso y muy listo",
        fur="#b8b8c4", fur_dark="#8a8a9a", belly="#f0e6e6",
        outfit="overol", outfit_color="#f2c230", accent="#e74c3c",
        accessory="gafas", eye_color="#212121",
        voice=V_CLAUDE, pitch=1.3, rate=0.95, scale=0.86, color="#e0e0f0"),
]}

SPECIES_TO_CHAR = {c.species: c.id for c in CHARACTERS.values()}


def get(char_id: str) -> CharacterSpec:
    return CHARACTERS[char_id]
