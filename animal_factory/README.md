# 🐾 Animal Factory AI 2D — v1.0

Escribes una idea y el sistema crea un **dibujo animado vertical (1080×1920, ~60 s)** con animales que caminan, corren, saltan, hablan (voz en español latino), ríen y reaccionan, con efectos, música y subtítulos. Se maneja desde una página web pensada para iPhone y exporta un **MP4 descargable**.

```
IDEA → GUION → PERSONAJES → ESCENAS → ANIMACIÓN → VOCES → MÚSICA → SUBTÍTULOS → MONTAJE → MP4
```

Todo es gratuito y de código abierto, sin claves ni tarjeta (ver `docs/COSTOS.md`).

## Uso rápido

```bash
pip install -r requirements.txt
python scripts/descargar_voces.py
python -m uvicorn web.app:app --host 0.0.0.0 --port 8000
```
Abre `http://localhost:8000`. Guía completa (incluye iPhone, Codespaces y Hugging Face): `docs/INSTALACION.md`.

También sin interfaz:
```python
from pathlib import Path
from factory.pipeline import generate_and_render
generate_and_render("Un gato pobre quiere hacerse millonario", Path("salida"), quality="borrador")
```

## Qué está verificado

| Comprobación | Resultado |
|---|---|
| Render final real de la idea de ejemplo | MP4 H.264+AAC, **1080×1920, 24 fps, 62,5 s, 15,5 MB**, 171 s con 4 núcleos |
| Voces | Piper genera audio real con las 3 voces (prueba automática: duración, nivel, actividad de la boca) |
| FFmpeg | `/api/status` y el pipeline lo verifican antes de empezar |
| Pruebas automáticas | 117 rápidas + 1 de extremo a extremo con voces reales (`pytest -m slow`) |
| Interfaz | Flujo completo en Chromium con tamaño de iPhone 13: guion → generar → video → descarga |
| Instalación limpia | `requirements.txt` en un entorno virgen: 117 pruebas pasan |

No probado: Safari en un iPhone físico, el `Dockerfile`, Codespaces y Hugging Face (detalle en `docs/INSTALACION.md`).

## Cómo está hecho

| Carpeta | Qué hace |
|---|---|
| `factory/story` | Generador de historias por plantillas (5 tramas: dinero, amor, fama, valentía, superación; 7 escenas cada una) |
| `factory/characters` | 10 personajes fijos (gato, perro, zorro, conejo ×2, oso, cerdo, rana, ratón, tortuga) con rig SVG |
| `factory/animation` | Poses por tiempo, 13 fondos, cámara, subtítulos y render de fotogramas |
| `factory/audio` | Voces (Piper), efectos y música sintetizados, mezcla con *ducking* |
| `factory/video` | Montaje y exportación con FFmpeg |
| `factory/pipeline.py`, `factory/jobs.py` | Orquestación y cola de trabajos con historial |
| `web/` | API FastAPI e interfaz móvil (HTML/CSS/JS sin librerías externas) |
| `tests/` | Pruebas |

Detalles de diseño y versiones: `docs/PLAN_TECNICO.md`.

## Limitaciones honestas

- **El guion no lo escribe una IA generativa.** Es un motor de plantillas: detecta animal y tema por palabras clave (9 animales entendidos, 5 temas) y rellena una trama escrita a mano. Una idea sin palabras reconocidas usa la trama de superación. El protagonista conserva su género fijo aunque la idea diga otro.
- **Solo hay 3 voces de Piper.** Los 10 personajes + narrador se diferencian cambiando tono y velocidad; algunas voces se parecen.
- **Animación tipo "recortable"** (muñecos articulados vistos de frente), no dibujo cuadro a cuadro.
- **Duración:** cada escena dura entre 8 y 10 s; el video total queda entre ~60 y ~63 s. Si una escena tiene poca voz, se completa con acción y música.
- La cola admite 3 trabajos a la vez y los procesa uno por uno.

## Cambiar de proveedor de voz

Las voces pasan por la interfaz `TTSProvider` (`factory/audio/tts.py`): un método `synthesize(text, voice, out_wav, length_scale)` y `available_voices()`. Para usar otro servicio, crea una clase con esos dos métodos y pásala: `Pipeline(tts=MiProveedor())`. Hoy **solo existe el proveedor Piper**; no hay ningún otro integrado.

## Cambiar el generador de historias

`factory/story/generator.py` define el protocolo `StoryProvider`. El generador actual por plantillas es el único implementado.

## Guion hecho a mano: "El zorro que vendió la Luna"

`examples/zorro_luna.py` arma un guion de 6 escenas de 10 s sin pasar por el generador y lo renderiza:

```bash
python examples/zorro_luna.py salida final      # o "borrador" para probar rápido
```
