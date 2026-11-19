# Costos y licencias

**Costo de uso del MVP: $0.** No hay claves de API, tarjeta de crédito ni servicios de pago.

| Pieza | Costo | Licencia |
|---|---|---|
| Código de Animal Factory | gratis | el de este repositorio |
| Piper (`piper-tts` 1.8.0) | gratis | GPL-3.0-or-later |
| Voz `es_MX-ald-medium` | gratis | Unlicense (dominio público) |
| Voz `es_MX-claude-high` | gratis | Apache-2.0 |
| Voz `es_AR-daniela-high` | gratis | **CC BY-SA 4.0: si publicas un video con esta voz, cita la fuente** (Lola y Rita la usan) |
| FFmpeg | gratis | LGPL/GPL según la compilación |
| resvg, NumPy, Pillow, FastAPI, Uvicorn | gratis | código abierto |
| Música y efectos | gratis | se generan con código: sin derechos de terceros |
| Personajes y fondos | gratis | dibujados con código: sin derechos de terceros |

Fuente de las licencias de voz: la ficha (`MODEL_CARD`) de cada voz en https://huggingface.co/rhasspy/piper-voices.

## Dónde ejecutarlo (todas son opciones gratuitas, ver `INSTALACION.md`)

| Opción | Costo | Límites a tener en cuenta |
|---|---|---|
| GitHub Codespaces | Cuota gratuita mensual de GitHub para cuentas personales | Se apaga solo por inactividad. Se consumen horas de la cuota mientras está encendido. |
| Hugging Face Spaces (CPU básico) | Gratis | Disco temporal: los videos se pierden al reiniciar. Pausa por inactividad. |

Las condiciones de los planes gratuitos las fijan GitHub y Hugging Face y pueden cambiar: revísalas antes de depender de ellas.
**No se compra ni se consume ningún crédito sin tu autorización.** Si algún día cambias la voz por un servicio de pago, será una decisión tuya (ver "Cambiar de proveedor de voz" en el README).

## Tiempo de render (medido)

| Calidad | Equipo | Tiempo |
|---|---|---|
| Final 1080×1920, 24 fps, 62 s | 4 núcleos | 171 s |
| Borrador 540×960, 12 fps, 62 s | 4 núcleos | ~40 s |

En un servidor gratuito de 2 núcleos espera aproximadamente el doble.
