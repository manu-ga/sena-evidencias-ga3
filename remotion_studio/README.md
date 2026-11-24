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

## Reel "NAWHI Ashwagandha" (composición `NawhiReel`)

Video vertical de ~21 s a partir del afiche del producto: cámara con zooms sobre cada frase del afiche, voz calmada, subtítulos en píldoras, música suave y cierre con marca y aviso. El texto usa solo lo que dice el afiche (sin precios, resultados ni puntos de venta).

```bash
# el afiche va en public/nawhi.jpg (no se sube al repositorio)
python scripts/build_nawhi.py --voces /ruta/voces --whisper /ruta/faster-whisper-small   # voz, música y línea de tiempo
REMOTION_BROWSER=/ruta/a/chromium npx remotion render src/index.ts NawhiReel out/nawhi.mp4
```
Guion y cámara: `SEGMENTS` en `scripts/build_nawhi.py`. Para la voz se usa la ortografía original de "NAWHI", "Ashwagandha" y "Withania somnifera": se comprobó en el fonetizador de Piper que la pronuncia bien (`nˈawi`, `aʃwaɣˈanda`, `witˈanja`).

## Documental "¿Quién es el cuarto gigante de Sudamérica?" (composición `CuartoGigante`)

Documental vertical de ~90 s: estadio animado, tarjetas de selección, podio, gráfico de Copas América, ranking FIFA, tabla de criterios y pantalla final con pregunta. Narrador con voz sintética masculina (Piper `es_MX-ald-medium`, tono más grave). No es una voz clonada. Música y sonidos de estadio sintetizados.

```bash
python scripts/build_gigante.py --voces /ruta/voces --whisper /ruta/faster-whisper-small
REMOTION_BROWSER=/ruta/a/chromium npx remotion render src/index.ts CuartoGigante out/cuarto_gigante.mp4
```

**Datos verificados el 24/11/2026:**
- Ranking FIFA/Coca-Cola del 18/11/2026 (vía el módulo de Wikipedia que lo replica): Colombia 10.ª (+1), Paraguay 31.º, Chile 51.º y Perú 52.º.
- Fichas de cada selección en Wikipedia, y el cuadro eliminatorio del Mundial 2026: Colombia y Paraguay cayeron en octavos.

**Clasificación propia, no oficial** (se muestra en pantalla con sus criterios y fuentes):

| Criterio | Puntos |
|---|---|
| Copas América | 3 por título |
| Mejor resultado mundialista | 3.er puesto = 5; cuartos de final = 3 |
| Participaciones en Mundiales (incluye 2026) | 0,5 cada una |
| Ranking FIFA actual | top 10 = 3; 11-30 = 2; 31-50 = 1; 51+ = 0 |

Resultado: Chile 15,5 · Paraguay 14,5 · Colombia 12,5 · Perú 11,5.

Sin fotos de jugadores ni logos de FIFA, ESPN o CONMEBOL: no hay material con licencia. Las banderas están dibujadas en SVG.
