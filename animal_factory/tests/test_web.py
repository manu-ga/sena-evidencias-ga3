import subprocess
import time

import pytest
from fastapi.testclient import TestClient

from factory.jobs import JobManager
from factory.pipeline import Pipeline, Result
from web.app import create_app


class FakePipeline(Pipeline):
    """Genera un MP4 real y pequeño para probar la API sin esperar un render completo."""

    def __init__(self):
        pass

    def run(self, story, outdir, style="cartoon", quality="final", progress=lambda *a: None):
        outdir.mkdir(parents=True, exist_ok=True)
        progress("voces", 0.2, "voces")
        progress("animacion", 0.6, "animando")
        v = outdir / "video.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=270x480:rate=12:duration=2",
                        "-f", "lavfi", "-i", "sine=duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                        "-movflags", "+faststart", str(v)], check=True)
        (outdir / "subtitulos.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHola\n", encoding="utf-8")
        return Result(v, outdir / "subtitulos.srt", outdir / "story.json", 2.0, {"segundos_de_render": 1.0, "probe": {"bytes": v.stat().st_size}}, [])


@pytest.fixture
def client(tmp_path):
    mgr = JobManager(tmp_path / "jobs", FakePipeline())
    return TestClient(create_app(mgr, access_code=""))


def wait_done(c, jid, timeout=30):
    t = time.time()
    while time.time() - t < timeout:
        j = c.get(f"/api/jobs/{jid}").json()
        if j["status"] in ("done", "error"):
            return j
        time.sleep(0.2)
    raise AssertionError("el trabajo no terminó")


def test_status_and_options(client):
    s = client.get("/api/status").json()
    assert s["ffmpeg"].startswith("ffmpeg") and s["voces"]
    o = client.get("/api/options").json()
    assert len(o["personajes"]) == 8 and {e["id"] for e in o["estilos"]} == {"cartoon", "pastel", "neon"}
    assert {c["id"] for c in o["calidades"]} == {"borrador", "final"}
    svg = client.get("/api/characters/michi.svg")
    assert svg.status_code == 200 and svg.headers["content-type"].startswith("image/svg")
    assert client.get("/api/characters/nadie.svg").status_code == 404


def test_index_served_and_has_real_controls(client):
    html = client.get("/").text
    for ident in ("idea", "goBtn", "previewBtn", "heroes", "styles", "scenes", "video", "downloadBtn", "history", "steps"):
        assert f'id="{ident}"' in html
    assert "viewport-fit=cover" in html and "playsinline" in html


def test_story_preview_has_thumbnails(client):
    r = client.post("/api/story", json={"idea": "Un gato pobre quiere ser millonario", "hero": "rocco", "style": "pastel"})
    assert r.status_code == 200
    d = r.json()
    assert d["theme"] == "dinero" and len(d["scenes"]) == 7
    assert all(s["miniatura"].startswith("data:image/png;base64,") for s in d["scenes"])
    assert "Rocco" in d["understood"]["protagonista"]


def test_job_lifecycle_download_range_and_delete(client):
    r = client.post("/api/jobs", json={"idea": "Una rana quiere ser famosa cantando", "style": "neon", "quality": "borrador"})
    assert r.status_code == 201
    jid = r.json()["id"]
    j = wait_done(client, jid)
    assert j["status"] == "done" and j["has_video"] and j["story"]["title"] == j["title"]
    assert any(x["id"] == jid for x in client.get("/api/jobs").json())

    full = client.get(f"/api/jobs/{jid}/video")
    assert full.status_code == 200 and full.headers["content-type"] == "video/mp4" and full.content[4:8] == b"ftyp"
    part = client.get(f"/api/jobs/{jid}/video", headers={"Range": "bytes=0-99"})
    assert part.status_code == 206 and len(part.content) == 100            # Safari/iPhone lo exige
    dl = client.get(f"/api/jobs/{jid}/video?download=1")
    assert "attachment" in dl.headers["content-disposition"] and ".mp4" in dl.headers["content-disposition"]
    assert client.get(f"/api/jobs/{jid}/poster").status_code == 200
    assert "Hola" in client.get(f"/api/jobs/{jid}/subtitles").text

    assert client.delete(f"/api/jobs/{jid}").status_code == 200
    assert client.get(f"/api/jobs/{jid}").status_code == 404


@pytest.mark.parametrize("body,fragment", [
    ({"idea": "a", "style": "cartoon", "quality": "final"}, "al menos 4"),
    ({"idea": "Un gato feliz", "style": "raro", "quality": "final"}, "Estilo"),
    ({"idea": "Un gato feliz", "style": "cartoon", "quality": "4k"}, "Calidad"),
    ({"idea": "Un gato feliz", "hero": "dragon", "style": "cartoon", "quality": "final"}, "Personaje"),
])
def test_invalid_requests_have_spanish_errors(client, body, fragment):
    r = client.post("/api/jobs", json=body)
    assert r.status_code == 400 and fragment in r.json()["detail"]


def test_idea_too_long_is_rejected(client):
    assert client.post("/api/jobs", json={"idea": "x" * 500}).status_code == 422


def test_access_code(tmp_path):
    c = TestClient(create_app(JobManager(tmp_path / "j", FakePipeline()), access_code="secreto"))
    assert c.get("/api/status").json()["requiere_codigo"] is True
    assert c.get("/api/jobs").status_code == 401
    assert c.get("/api/jobs", headers={"X-Access-Code": "malo"}).status_code == 401
    assert c.get("/api/jobs", headers={"X-Access-Code": "secreto"}).status_code == 200
    assert c.get("/api/jobs?code=secreto").status_code == 200      # para <video src> y descargas


def test_history_survives_restart_and_interrupted_jobs_are_marked(tmp_path):
    m1 = JobManager(tmp_path / "j", FakePipeline())
    c = TestClient(create_app(m1, access_code=""))
    jid = c.post("/api/jobs", json={"idea": "Un oso quiere ser bombero", "style": "cartoon", "quality": "borrador"}).json()["id"]
    wait_done(c, jid)
    m1.delete  # noqa
    # simula un trabajo que estaba generando cuando se apagó el servidor
    m1._update(jid, status="running")
    m2 = JobManager(tmp_path / "j", FakePipeline(), autostart=False)
    j = m2.get(jid)
    assert j["status"] == "error" and "reinici" in j["error"]


def test_queue_limit(tmp_path):
    mgr = JobManager(tmp_path / "j", FakePipeline(), autostart=False)   # sin worker: todo queda en cola
    c = TestClient(create_app(mgr, access_code=""))
    for _ in range(3):
        assert c.post("/api/jobs", json={"idea": "Un gato feliz"}).status_code == 201
    r = c.post("/api/jobs", json={"idea": "Un gato feliz"})
    assert r.status_code == 400 and "cola" in r.json()["detail"]
