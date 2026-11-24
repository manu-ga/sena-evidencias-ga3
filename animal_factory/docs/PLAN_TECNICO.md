# Plan técnico — Animal Factory AI 2D v1.0

Fábrica automática de dibujos animados 2D: escribes una idea y obtienes un MP4 vertical (1080×1920) de ~60 s con personajes animales que se mueven, hablan en español latino, con efectos, música y subtítulos.

## Flujo

```
IDEA → GUION → PERSONAJES → ESCENAS → ANIMACIÓN → VOCES → MÚSICA → SUBTÍTULOS → MONTAJE → MP4
```

| Paso | Módulo | Cómo funciona |
|---|---|---|
| Guion | `factory/story` | Plantillas de trama escritas a mano (dinero, amor, fama, valentía, superación). Detecta animal, tema y rasgos en la idea y rellena 7 escenas. **No es una IA generativa**: es un motor de plantillas que funciona sin internet ni costo. |
| Personajes | `factory/characters` | 8 especies dibujadas con SVG y un "rig" (cuerpo, brazos, piernas, cabeza, orejas, cola) controlado por parámetros. Cada personaje fija sus colores, ropa y voz. |
| Animación | `factory/animation` | Cada fotograma se calcula: pose del personaje (caminar, correr, saltar, hablar, reír, reaccionar), fondo con parallax, cámara y subtítulo. Se convierte a PNG con `resvg`. |
| Voces | `factory/audio/tts.py` | Piper (offline, gratis). La boca se mueve con la envolvente real del audio generado. Interfaz `TTSProvider` para cambiar de proveedor. |
| Efectos y música | `factory/audio/sfx.py`, `music.py` | Sintetizados con NumPy desde cero, así que no hay derechos de autor. |
| Montaje | `factory/video` | FFmpeg: una clip por escena, transiciones `xfade`, mezcla de audio y exportación H.264 + AAC. |
| App | `web/` | FastAPI + HTML/JS adaptado a iPhone. Cola de trabajos, historial, vista previa y descarga. |

## Decisiones y versiones

Probadas juntas en Python 3.13 y FFmpeg 6.1 (ver `requirements.txt`).

| Pieza | Elección | Por qué |
|---|---|---|
| SVG → PNG | `resvg-py 0.5.0` | Es un binario Rust autocontenido; cairosvg exige librerías del sistema. ~0,4 s por frame a 1080×1920. |
| Voz | `piper-tts 1.8.0` + voces `es_MX-ald-medium`, `es_MX-claude-high`, `es_AR-daniela-high` | Gratis, offline, sin tarjeta. Las voces vienen de Hugging Face. |
| Servidor | `fastapi 0.165.0` + `uvicorn 0.54.0` | Sirve vídeo con soporte `Range`, necesario para reproducir en Safari. |
| Video | FFmpeg `libx264` + `aac` | H.264/AAC se reproduce en cualquier iPhone. |

## Limitaciones honestas del MVP

- El guion sale de plantillas, no de un modelo de lenguaje. Entiende ocho animales (más la tortuga, que solo se usa en guiones a mano) y cinco temas. Una idea fuera de eso usa la trama de superación.
- Las tres voces de Piper se diferencian con cambios de tono y velocidad. No hay un reparto de voces distintas para cada personaje.
- La animación es de estilo "recortable" frontal, no de dibujo cuadro a cuadro.
- Un video final de 60 s tarda minutos en un servidor gratuito de 2 núcleos. El modo "borrador" es unas 8 veces más rápido.

## Etapas

1. Arquitectura y estructura (este documento).
2. Generador de historias.
3. Personajes SVG reutilizables.
4. Motor de animación 2D.
5. Voces, efectos y música.
6. Montaje y exportación MP4.
7. Interfaz móvil.
8. Pruebas completas.
9. Despliegue accesible desde iPhone.
