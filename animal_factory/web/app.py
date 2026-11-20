"""API web (FastAPI) y servidor de la interfaz móvil."""
from __future__ import annotations

import base64
import hmac
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from factory import config
from factory.animation.styles import STYLES, get_style
from factory.characters.library import CHARACTERS
from factory.characters.rig import Pose, character_svg
from factory.jobs import JobError, JobManager
from factory.pipeline import Pipeline, make_thumbnails
from factory.story.generator import generate_story
from factory.video.encoder import ffmpeg_available

STATIC = Path(__file__).parent / "static"


class StoryRequest(BaseModel):
    idea: str = Field(..., max_length=400)
    hero: str | None = None
    style: str = "cartoon"


class JobRequest(StoryRequest):
    quality: str = "final"


def create_app(manager: JobManager | None = None, access_code: str | None = None) -> FastAPI:
    app = FastAPI(title="Animal Factory AI 2D", version="1.0")
    code = config.ACCESS_CODE if access_code is None else access_code
    app.state.manager = manager

    def mgr() -> JobManager:
        if app.state.manager is None:
            app.state.manager = JobManager()
        return app.state.manager

    def guard(request: Request, codigo: str | None = Query(None, alias="code")) -> None:
        if not code:
            return
        given = request.headers.get("x-access-code") or codigo or ""
        if not hmac.compare_digest(given, code):
            raise HTTPException(401, "Código de acceso incorrecto.")

    @app.exception_handler(ValueError)
    async def _val(_: Request, e: ValueError):
        return JSONResponse({"detail": str(e)}, status_code=400)

    @app.exception_handler(JobError)
    async def _job(_: Request, e: JobError):
        return JSONResponse({"detail": str(e)}, status_code=400)

    # ---------------------------------------------------------------- información
    @app.get("/api/status")
    def status():
        info = {"requiere_codigo": bool(code), "ok": True, "problemas": []}
        try:
            info["ffmpeg"] = ffmpeg_available()
        except Exception as e:
            info["ok"] = False
            info["problemas"].append(str(e))
        voices = Pipeline().tts.available_voices()
        info["voces"] = voices
        if not voices:
            info["ok"] = False
            info["problemas"].append("No hay voces instaladas (python scripts/descargar_voces.py).")
        return info

    @app.get("/api/options", dependencies=[Depends(guard)])
    def options():
        return {
            "personajes": [{"id": c.id, "nombre": c.name, "especie": c.species, "personalidad": c.personality}
                           for c in CHARACTERS.values()],
            "estilos": [{"id": s.id, "nombre": s.label} for s in STYLES.values()],
            "calidades": [
                {"id": "borrador", "nombre": "Borrador rápido (540×960)", "detalle": "para probar ideas"},
                {"id": "final", "nombre": "Final (1080×1920)", "detalle": "para publicar"},
            ],
            "ejemplos": [
                "Un gato pobre quiere hacerse millonario, pero sus decisiones lo meten en problemas",
                "Un perro tímido quiere conquistar a una coneja",
                "Una rana quiere ser famosa cantando",
                "Un conejo le tiene miedo a la oscuridad y pasa la noche en el bosque",
                "Un oso quiere ser bombero",
            ],
        }

    @app.get("/api/characters/{cid}.svg")
    def character_image(cid: str):
        if cid not in CHARACTERS:
            raise HTTPException(404, "Personaje no encontrado")
        spec = CHARACTERS[cid]
        body = character_svg(spec, Pose(x=0, y=0, mouth=0.0, arm_l=14, arm_r=14), get_style("cartoon"), ground_y=0)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-230 -700 460 740">{body}</svg>'
        return Response(svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    # ---------------------------------------------------------------- guion
    @app.post("/api/story", dependencies=[Depends(guard)])
    async def story(req: StoryRequest):
        if req.style not in STYLES:
            raise HTTPException(400, "Estilo no válido")
        hero = None if req.hero in (None, "", "auto") else req.hero
        st = generate_story(req.idea, hero)
        thumbs = await run_in_threadpool(make_thumbnails, st, req.style)
        d = st.to_dict()
        for s, png in zip(d["scenes"], thumbs):
            s["miniatura"] = "data:image/png;base64," + base64.b64encode(png).decode()
        return d

    # ---------------------------------------------------------------- trabajos
    @app.post("/api/jobs", dependencies=[Depends(guard)], status_code=201)
    def create_job(req: JobRequest):
        return mgr().submit(req.idea, req.hero, req.style, req.quality)

    @app.get("/api/jobs", dependencies=[Depends(guard)])
    def list_jobs():
        return mgr().list()

    @app.get("/api/jobs/{jid}", dependencies=[Depends(guard)])
    def get_job(jid: str):
        j = mgr().get(jid)
        if not j:
            raise HTTPException(404, "No existe ese trabajo")
        story_file = mgr().file(jid, "story.json")
        if story_file:
            import json
            j["story"] = json.loads(story_file.read_text(encoding="utf-8"))
        j["elapsed"] = round(((j["finished"] or time.time()) - j["started"]), 1) if j.get("started") else 0
        return j

    @app.delete("/api/jobs/{jid}", dependencies=[Depends(guard)])
    def delete_job(jid: str):
        if not mgr().delete(jid):
            raise HTTPException(404, "No existe ese trabajo")
        return {"ok": True}

    def _file(jid: str, name: str, media: str, download: str | None = None):
        p = mgr().file(jid, name)
        if not p:
            raise HTTPException(404, "Archivo no disponible todavía")
        kw = {"filename": download} if download else {}
        return FileResponse(p, media_type=media, content_disposition_type="attachment" if download else "inline", **kw)

    @app.get("/api/jobs/{jid}/video", dependencies=[Depends(guard)])
    def video(jid: str, download: int = 0):
        return _file(jid, "video.mp4", "video/mp4", f"animal-factory-{jid}.mp4" if download else None)

    @app.get("/api/jobs/{jid}/poster", dependencies=[Depends(guard)])
    def poster(jid: str):
        return _file(jid, "poster.jpg", "image/jpeg")

    @app.get("/api/jobs/{jid}/subtitles", dependencies=[Depends(guard)])
    def subtitles(jid: str):
        return _file(jid, "subtitulos.srt", "application/x-subrip", f"animal-factory-{jid}.srt")

    app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
    return app


app = create_app()
