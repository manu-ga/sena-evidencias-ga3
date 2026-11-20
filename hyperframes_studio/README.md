# HyperFrames Studio

[HyperFrames](https://hyperframes.heygen.com) (HeyGen, Apache-2.0): se escribe el video como **HTML + GSAP** y se renderiza a MP4.
Versión instalada: **hyperframes 0.9.70** (necesita Node ≥ 22). Animaciones con **GSAP 3.15.0** incluido en `demo/vendor/`.

## Uso

```bash
cd hyperframes_studio
npm install
npm run check      # valida la composición (Chrome headless)
npm run preview    # editor visual en el navegador
npm run render     # genera demo/renders/demo.mp4
npm run doctor     # revisa Node, FFmpeg y Chrome
```

La composición de ejemplo es `demo/index.html`: un título animado vertical de 1080×1920 y 3 s.
Para un video nuevo: `npx hyperframes init mi-video --example blank --resolution portrait --non-interactive --skip-skills`.

## Importante en este entorno

- **Sin CDN.** La plantilla carga GSAP desde `cdn.jsdelivr.net`, que aquí está bloqueado. Por eso GSAP va copiado en `demo/vendor/gsap.min.js`.
  Usa siempre `<script src="vendor/gsap.min.js">` en tus composiciones.
- **Telemetría desactivada** (`hyperframes telemetry disable`). Si trabajas en otro equipo, desactívala con `HYPERFRAMES_NO_TELEMETRY=1`.
- **No se usó ninguna función en la nube ni de pago** (`cloud`, `lambda`, `cloudrun`, `publish`, `share`, `billing`, `templates` Pro, `auth`). Requieren cuenta de HeyGen u otros servicios; no las uses sin decidirlo.

## Probado

- `npm install`: 78 paquetes, sin vulnerabilidades. `hyperframes doctor`: Node 22, FFmpeg 6.1 y Chrome detectados.
- `hyperframes check`: 0 errores.
- Render real: MP4 H.264, 1080×1920, 30 fps, 3 s, en unos 10 s (4 núcleos, captura por software).

No instalado (opcional): transcripción local (whisper-cpp), voz local (Kokoro) y música local (MusicGen).

## Licencia
HyperFrames: Apache-2.0. GSAP tiene su propia licencia (https://gsap.com/standard-license).
