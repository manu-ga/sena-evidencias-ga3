# Remotion Studio

Edición de video con [Remotion](https://www.remotion.dev) (videos como código React). Versión instalada: **4.0.545**, con Node 22.

## Uso

```bash
cd remotion_studio
npm install                  # una sola vez
npm run studio               # abre el editor visual en http://localhost:3000
npm run render               # renderiza la composición "Demo" a out/demo.mp4
npm run still                # guarda un fotograma en out/demo.png
npm run compositions         # lista las composiciones
```

Para agregar un video nuevo: crea un componente en `src/`, registra una `<Composition>` en `src/Root.tsx` y renderízala con
`npx remotion render src/index.ts <IdDeLaComposicion> out/mi_video.mp4`.

## Navegador

Remotion renderiza con Chrome. Si ya tienes Chromium (o no hay acceso a internet para que Remotion descargue el suyo), indica su ruta:

```bash
REMOTION_BROWSER=/ruta/a/chromium npm run render
```

## Probado

- `npm install`: 245 paquetes, sin vulnerabilidades.
- `tsc --noEmit`: sin errores.
- Render real de la composición `Demo` (1080×1920, 24 fps, 3 s): MP4 H.264 en 12 s.
- `remotion studio` arranca y responde.

## Licencia

Remotion tiene una licencia propia: es gratuito para particulares y equipos pequeños, y las empresas más grandes deben comprar una licencia. Revisa las condiciones vigentes en https://www.remotion.dev/license antes de usarlo comercialmente.

## GSAP en Remotion

GSAP 3.15.1 está instalado. `src/GsapDemo.tsx` (composición `GsapDemo`, 4 s) muestra el patrón correcto: la línea de tiempo se crea **en pausa** y se coloca con `tl.seek(frame / fps)` en cada fotograma, para que el render sea exacto. No uses `tl.play()`: depende del reloj real y saldría distinto en cada render.

```bash
REMOTION_BROWSER=/opt/pw-browsers/chromium npx remotion render src/index.ts GsapDemo out/gsap.mp4
```
Licencia de GSAP: "Standard 'no charge' license" (https://gsap.com/standard-license).

## Video "Ads de dropshipping vs Trading" (composición `AdsVsTrading`)

Explicador vertical 9:16 de ~38 s: pantalla partida, 24 planos con cortes cada ~1,6 s, subtítulos de 2–4 palabras (naranja `#F97316` = ads, cian `#06B6D4` = trading), voz, música continua con ducking y un micro-efecto en cada corte.

```bash
# 1) Audio + línea de tiempo (necesita piper-tts, faster-whisper, numpy y ffmpeg; ver ../animal_factory/docs/INSTALACION.md)
python ../animal_factory/scripts/descargar_voces.py --destino voces      # ~240 MB, una vez
python scripts/build_audio.py --voces voces --whisper /ruta/a/faster-whisper-small
# 2) Vista previa y render
npm run studio
REMOTION_BROWSER=/ruta/a/chromium npx remotion render src/index.ts AdsVsTrading out/ads_vs_trading.mp4
```

- `scripts/build_audio.py` contiene el guion (editable), genera `public/ads_trading_audio.wav` y `src/ads_trading/timeline.json`. Cada plano arranca en una palabra ancla del guion, así que si cambias el texto los cortes siguen a la voz.
- Los tiempos por palabra los mide Whisper sobre la voz sintética (Piper no los entrega). El texto de los subtítulos es siempre el del guion.
- `src/ads_trading/shots.tsx` tiene los 15 tipos de plano. Para ver las zonas seguras: `--props='{"safeGuides":true}'`.
- Render (4 núcleos, software): ~3,5 min.
