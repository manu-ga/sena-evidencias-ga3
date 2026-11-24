# Instalación y uso desde el iPhone

La fábrica es un servidor web. El iPhone solo abre una página en Safari; el trabajo pesado (dibujar, voces, FFmpeg) ocurre en el servidor.

## Lo que está probado y lo que no

| Camino | Estado |
|---|---|
| Instalación local con `pip` en Linux + servidor + interfaz en un navegador con tamaño de iPhone 13 | **Probado** (flujo completo: escribir idea → guion → generar → ver video → descargar MP4) |
| GitHub Codespaces | **No probado** (guía siguiendo la documentación oficial) |
| Hugging Face Spaces con el `Dockerfile` | **No probado** (en el entorno de desarrollo no hay Docker) |
| Safari real en un iPhone | **No probado** (se usó Chromium emulando un iPhone). El video es H.264 + AAC con `faststart`, y el servidor soporta `Range`, que es lo que Safari necesita |

## A. Instalación (Linux o Codespaces)

Requisitos: Python 3.13 (la única versión probada), FFmpeg y la fuente DejaVu.

```bash
sudo apt-get install -y ffmpeg fonts-dejavu-core      # FFmpeg y fuente para subtítulos
cd animal_factory
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/descargar_voces.py                      # ~240 MB, una sola vez
python -m pytest -m "not slow"                         # 117 pruebas (≈10 s)
python -m uvicorn web.app:app --host 0.0.0.0 --port 8000
```

Abre `http://localhost:8000`. Si la página muestra "La fábrica no está lista", el mensaje dice qué falta (FFmpeg o voces).

Para proteger la página cuando esté en internet:
```bash
FACTORY_ACCESS_CODE="mi-clave-larga" python -m uvicorn web.app:app --host 0.0.0.0 --port 8000
```

## B. Desde el iPhone con GitHub Codespaces (sin computador)

1. En Safari abre el repositorio en GitHub → botón verde **Code** → pestaña **Codespaces** → **Create codespace**.
2. Cuando cargue el editor, abre la terminal y ejecuta los comandos de la sección A.
3. En el panel **Ports**, el puerto 8000 aparece con una dirección. Ábrela en Safari (por defecto es privada: solo tu cuenta de GitHub puede entrar).
4. Escribe tu idea, toca **GENERAR VIDEO** y, cuando termine, **Descargar MP4**. En Safari el archivo queda en la app **Archivos → Descargas**.

El codespace se apaga solo por inactividad; al volver a abrirlo, vuelve a ejecutar el comando `uvicorn`. Los videos generados quedan en `animal_factory/output/`.

## C. Servidor siempre disponible con Hugging Face Spaces

1. Crea una cuenta gratuita en huggingface.co → **New Space** → SDK **Docker** → hardware **CPU basic (free)**.
2. Sube el contenido de la carpeta `animal_factory/` a la raíz del Space (incluye el `Dockerfile`).
3. Agrega al inicio del `README.md` del Space:
   ```yaml
   ---
   title: Animal Factory
   sdk: docker
   app_port: 7860
   ---
   ```
4. En **Settings → Variables and secrets** crea el secreto `FACTORY_ACCESS_CODE` con tu clave. Sin él, cualquiera con el enlace gastaría tu servidor.
5. Espera la construcción (descarga las voces) y abre la URL del Space en Safari.

Los archivos del Space gratuito son temporales: descarga tus MP4 antes de que se reinicie.

## Instalar como app en el iPhone

En Safari: botón compartir → **Añadir a pantalla de inicio**.

## Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| "No hay voces instaladas" | Ejecuta `python scripts/descargar_voces.py`. Si falla, tu red debe permitir `huggingface.co` y `us.aws.cdn.hf.co`. |
| "FFmpeg no está instalado" | `sudo apt-get install ffmpeg` |
| Subtítulos con letra rara | Instala `fonts-dejavu-core` |
| El video tarda mucho | Usa la calidad **Borrador** para probar y **Final** solo al terminar |
| Pide un código | El servidor tiene `FACTORY_ACCESS_CODE`; escríbelo en la pantalla de entrada |
