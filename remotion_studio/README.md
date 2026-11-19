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
