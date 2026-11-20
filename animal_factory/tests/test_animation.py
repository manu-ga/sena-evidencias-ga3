import math
import xml.etree.ElementTree as ET

import pytest
import resvg_py

from factory.animation.backgrounds import LOCATIONS, background_svg
from factory.animation.poses import actor_pose
from factory.animation.scene_renderer import SceneRenderer, subtitle_chunks, wrap
from factory.animation.styles import STYLES, get_style
from factory.characters.library import CHARACTERS
from factory.characters.rig import Pose, character_svg
from factory.models import Beat, CameraKey, Line, Prop, Scene
from factory.pipeline import plan_durations

ACTIONS = ["idle", "walk", "run", "jump", "laugh", "cry", "angry", "surprise", "dance", "fall", "think",
           "celebrate", "shiver", "shrug"]


def _wrap_svg(inner):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">{inner}</svg>'


@pytest.mark.parametrize("cid", list(CHARACTERS))
@pytest.mark.parametrize("style", list(STYLES))
def test_every_character_renders(cid, style):
    svg = _wrap_svg(character_svg(CHARACTERS[cid], Pose(x=540, mouth=0.7), get_style(style)))
    ET.fromstring(svg)  # XML válido
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg, width=270, height=480))
    assert png[:4] == b"\x89PNG"


def test_character_design_is_stable_between_poses():
    spec = CHARACTERS["michi"]
    a = character_svg(spec, Pose(), get_style("cartoon"))
    b = character_svg(spec, Pose(), get_style("cartoon"))
    assert a == b
    for color in (spec.fur, spec.outfit_color):
        assert color in character_svg(spec, Pose(arm_l=100, mouth=1), get_style("cartoon"))


@pytest.mark.parametrize("action", ACTIONS)
def test_poses_are_finite_for_every_action(action):
    spec = CHARACTERS["fausto"]
    beats = [Beat("fausto", action, 0.0, 1.0, 200, 800)]
    for tf in (0.0, 0.1, 0.5, 0.99, 1.0):
        p = actor_pose(spec, beats, tf, tf * 9.0, mouth=0.5)
        for v in (p.x, p.y, p.bob, p.leg_l, p.leg_r, p.arm_l, p.arm_r, p.rot, p.sx, p.sy):
            assert math.isfinite(v)


def test_walking_moves_and_legs_swing():
    spec = CHARACTERS["michi"]
    beats = [Beat("michi", "walk", 0.0, 1.0, 100, 900)]
    p0, p1 = actor_pose(spec, beats, 0.1, 1.0, None), actor_pose(spec, beats, 0.8, 7.0, None)
    assert p1.x > p0.x + 300
    assert p0.leg_l != p1.leg_l or abs(p0.leg_l) > 1


def test_mouth_follows_audio_envelope():
    spec = CHARACTERS["lola"]
    beats = [Beat("lola", "idle", 0.0, 1.0, 500)]
    assert actor_pose(spec, beats, 0.5, 4.0, 0.9).mouth > actor_pose(spec, beats, 0.5, 4.0, 0.0).mouth


@pytest.mark.parametrize("loc", list(LOCATIONS))
def test_backgrounds_are_valid_svg(loc):
    for t in (0.0, 3.3):
        ET.fromstring(_wrap_svg(background_svg(loc, get_style("cartoon"), t, 40)))


def test_subtitles_wrap_and_chunk():
    long = "Esta es una frase bastante larga para comprobar que los subtítulos se parten bien en trozos."
    chunks = subtitle_chunks(long, 1.0, 7.0)
    assert len(chunks) >= 2
    assert chunks[0][0] == 1.0 and abs(chunks[-1][1] - 7.0) < 1e-6
    assert all(len(wrap(c[2])) <= 2 for c in chunks)
    assert " ".join(c[2] for c in chunks) == long


def test_scene_frames_change_over_time_and_camera_stays_inside_world():
    sc = Scene(1, "t", "parque", "alegre", [Line("michi", "Hola amigos, ¿cómo están todos hoy?")],
               [Beat("michi", "walk", 0, 1, 100, 900)], ["michi"],
               camera=[CameraKey(0, "wide"), CameraKey(0.5, "close", "michi")], props=[Prop("moneda", 500, 1200, 1, "spin")],
               duration=9.0, line_times=[(0.5, 4.0)])
    r = SceneRenderer(sc, CHARACTERS, get_style("cartoon"), [[0.5] * 400])
    assert r.frame_svg(1.0) != r.frame_svg(1.5)
    for t in (0.0, 4.4, 4.6, 8.9):
        cx, cy, z = r.camera_at(t, {"michi": 300})
        assert z >= 1.0
        assert 540 / z - 1e-6 <= cx <= 1080 - 540 / z + 1e-6
        assert 960 / z - 1e-6 <= cy <= 1920 - 960 / z + 1e-6
    assert "Hola amigos" in r.frame_svg(1.0)     # subtítulo visible mientras habla
    assert "Hola amigos" not in r.frame_svg(8.5)  # y oculto cuando termina


def test_plan_durations_bounds():
    d = plan_durations([7.5, 8.9, 6.0, 9.9, 5.0, 8.0, 9.0])
    assert all(8.0 <= x <= 10.0 for x in d)
    assert abs(sum(d) - 60) <= 3
