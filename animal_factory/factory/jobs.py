"""Cola de trabajos con historial persistente en disco (un trabajo a la vez)."""
from __future__ import annotations

import json
import queue
import shutil
import subprocess
import threading
import time
import traceback
import uuid
from pathlib import Path

from .config import JOBS_DIR, QUALITY
from .animation.styles import STYLES
from .characters.library import CHARACTERS
from .pipeline import Pipeline
from .story.generator import generate_story

STAGES = ["guion", "voces", "audio", "animacion", "montaje"]
MAX_QUEUED = 3


class JobError(ValueError):
    pass


class JobManager:
    def __init__(self, jobs_dir: Path | None = None, pipeline: Pipeline | None = None, autostart: bool = True):
        self.dir = Path(jobs_dir or JOBS_DIR)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = pipeline or Pipeline()
        self._lock = threading.Lock()
        self._q: queue.Queue[str] = queue.Queue()
        self._jobs: dict[str, dict] = {}
        self._load()
        self._thread = None
        if autostart:
            self._thread = threading.Thread(target=self._worker, daemon=True, name="job-worker")
            self._thread.start()

    # ------------------------------------------------------------------ persistencia
    def _path(self, jid: str) -> Path:
        return self.dir / jid / "job.json"

    def _save(self, job: dict) -> None:
        p = self._path(job["id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(job, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(p)

    def _load(self) -> None:
        for p in self.dir.glob("*/job.json"):
            try:
                job = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if job.get("status") in ("queued", "running"):
                job.update(status="error", error="El servidor se reinició mientras se generaba. Vuelve a intentarlo.")
                self._save(job)
            self._jobs[job["id"]] = job

    def _update(self, jid: str, **kw) -> None:
        with self._lock:
            self._jobs[jid].update(kw)
            self._save(self._jobs[jid])

    # ------------------------------------------------------------------ API
    def submit(self, idea: str, hero: str | None, style: str, quality: str) -> dict:
        idea = (idea or "").strip()
        if style not in STYLES:
            raise JobError(f"Estilo no válido: {style}")
        if quality not in QUALITY:
            raise JobError(f"Calidad no válida: {quality}")
        if hero in ("", "auto"):
            hero = None
        if hero and hero not in CHARACTERS:
            raise JobError(f"Personaje no válido: {hero}")
        generate_story(idea, hero)   # valida la idea ya (lanza ValueError con mensaje en español)
        with self._lock:
            pending = sum(1 for j in self._jobs.values() if j["status"] in ("queued", "running"))
            if pending >= MAX_QUEUED:
                raise JobError("Hay demasiados videos en cola. Espera a que termine alguno.")
            jid = uuid.uuid4().hex[:10]
            job = {"id": jid, "idea": idea, "hero": hero, "style": style, "quality": quality,
                   "status": "queued", "stage": "guion", "progress": 0.0, "message": "En cola…",
                   "created": time.time(), "started": None, "finished": None, "title": None, "theme": None,
                   "warnings": [], "error": None, "stats": {}, "has_video": False}
            self._jobs[jid] = job
            self._save(job)
        self._q.put(jid)
        return dict(job)

    def get(self, jid: str) -> dict | None:
        with self._lock:
            j = self._jobs.get(jid)
            return dict(j) if j else None

    def list(self) -> list[dict]:
        with self._lock:
            return sorted((dict(j) for j in self._jobs.values()), key=lambda j: -j["created"])

    def delete(self, jid: str) -> bool:
        with self._lock:
            j = self._jobs.get(jid)
            if not j:
                return False
            if j["status"] in ("queued", "running"):
                raise JobError("No se puede borrar un video que se está generando.")
            del self._jobs[jid]
        shutil.rmtree(self.dir / jid, ignore_errors=True)
        return True

    def file(self, jid: str, name: str) -> Path | None:
        p = self.dir / jid / name
        return p if p.exists() else None

    # ------------------------------------------------------------------ worker
    def _worker(self) -> None:
        while True:
            jid = self._q.get()
            try:
                self._run(jid)
            except Exception as e:  # nunca matar el hilo
                traceback.print_exc()
                self._update(jid, status="error", error=f"{type(e).__name__}: {e}", message="Falló la generación")

    def _run(self, jid: str) -> None:
        job = self.get(jid)
        if not job:
            return
        self._update(jid, status="running", started=time.time(), stage="guion", progress=0.01, message="Escribiendo el guion…")
        story = generate_story(job["idea"], job["hero"])
        out = self.dir / jid
        (out / "story.json").write_text(json.dumps(story.to_dict(), ensure_ascii=False, indent=1), encoding="utf-8")
        self._update(jid, title=story.title, theme=story.theme)

        def prog(stage: str, pct: float, msg: str) -> None:
            self._update(jid, stage=stage, progress=round(pct, 3), message=msg)

        res = self.pipeline.run(story, out, style=job["style"], quality=job["quality"], progress=prog)
        for ss in ("2", "0"):   # si el video es muy corto, usa el primer fotograma
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", ss, "-i", str(res.video), "-frames:v", "1",
                            "-vf", "scale=270:-2", str(out / "poster.jpg")], capture_output=True)
            if (out / "poster.jpg").exists():
                break
        self._update(jid, status="done", stage="montaje", progress=1.0, message="¡Listo!", finished=time.time(),
                     warnings=res.warnings, stats=res.stats, has_video=True, duration=round(res.duration, 1))
