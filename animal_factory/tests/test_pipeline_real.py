"""Prueba de extremo a extremo con voces Piper reales y FFmpeg. Tarda ~1 min (calidad borrador)."""
import json

import pytest

from factory.audio.tts import PiperProvider
from factory.pipeline import Pipeline
from factory.story.generator import generate_story
from factory.video.encoder import ffmpeg_available, probe

pytestmark = pytest.mark.slow


@pytest.mark.skipif(not PiperProvider().available_voices(), reason="No hay voces Piper")
def test_idea_to_mp4_draft(tmp_path):
    ffmpeg_available()
    story = generate_story("Una rana quiere ser famosa cantando")
    stages = []
    res = Pipeline(workers=4).run(story, tmp_path, style="pastel", quality="borrador", progress=lambda s, p, m: stages.append(s))
    info = probe(res.video)
    kinds = {s["codec_type"]: s for s in info["streams"]}
    assert kinds["video"]["codec_name"] == "h264" and (kinds["video"]["width"], kinds["video"]["height"]) == (540, 960)
    assert kinds["audio"]["codec_name"] == "aac"
    assert 55 <= float(info["format"]["duration"]) <= 66
    assert res.video.stat().st_size > 500_000
    assert [s for s in dict.fromkeys(stages)] == ["voces", "audio", "animacion", "montaje", "listo"]
    assert res.srt.read_text(encoding="utf-8").count("-->") >= 14
    assert json.loads(res.story_json.read_text(encoding="utf-8"))["title"] == story.title
    assert all(7.99 <= s.duration <= 10.01 for s in story.scenes), [s.duration for s in story.scenes]
    assert res.stats["audio"]["rms_voz"] > 0.05
    assert not (tmp_path / "work").exists()    # limpia archivos temporales
