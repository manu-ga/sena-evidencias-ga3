# Animal Factory AI 2D — imagen para Hugging Face Spaces (Docker) o cualquier servidor.
# NOTA: este Dockerfile NO se pudo probar en el entorno de desarrollo (sin daemon de Docker).
FROM python:3.13-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces ejecuta como usuario 1000
RUN useradd -m -u 1000 app
USER app
ENV PATH="/home/app/.local/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /home/app/animal_factory

COPY --chown=app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app . .
# Descarga las voces durante la construcción (necesita acceso a huggingface.co)
RUN python scripts/descargar_voces.py

EXPOSE 7860
# Para proteger la app pública: define el secreto FACTORY_ACCESS_CODE en el panel del servicio.
CMD ["python", "-m", "uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "7860"]
