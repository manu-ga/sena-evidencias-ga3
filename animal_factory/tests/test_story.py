import pytest

from factory.animation.backgrounds import LOCATIONS
from factory.animation.backgrounds import prop_svg
from factory.animation.styles import get_style
from factory.audio.sfx import SFX
from factory.characters.library import CHARACTERS
from factory.story.generator import detect_species, detect_theme, generate_story, scene_word_count
from factory.video.encoder import XFADE_OK

IDEAS = {
    "Un gato pobre quiere hacerse millonario, pero sus decisiones lo meten en problemas": ("dinero", "michi"),
    "Un perro tímido quiere conquistar a una coneja": ("amor", "rocco"),
    "Una rana quiere ser famosa cantando": ("fama", "rita"),
    "Un conejo cobarde le tiene miedo a la oscuridad": ("valentia", "lola"),
    "Un oso quiere ser bombero": ("superacion", "bruno"),
}


@pytest.mark.parametrize("idea,expected", IDEAS.items())
def test_story_structure(idea, expected):
    s = generate_story(idea)
    assert (s.theme, next(iter(s.characters)) in CHARACTERS) == (expected[0], True)
    assert 6 <= len(s.scenes) <= 8
    assert s.title and s.message
    hero = s.scenes[0].cast[0]
    assert hero == expected[1] or expected[1] in s.characters


@pytest.mark.parametrize("idea", IDEAS)
def test_story_is_renderable(idea):
    """Todo lo que el guion referencia debe existir en los motores."""
    s = generate_story(idea)
    for sc in s.scenes:
        assert sc.location in LOCATIONS, sc.location
        assert sc.transition in XFADE_OK, sc.transition
        assert 1 <= len(sc.lines) <= 4
        assert scene_word_count(sc) <= 20, (sc.index, scene_word_count(sc))
        for l in sc.lines:
            assert l.text.strip(), "línea vacía"
            assert l.speaker == "narrador" or l.speaker in s.characters
        for b in sc.beats:
            assert b.actor in s.characters and 0 <= b.t0 < b.t1 <= 1
        for c in sc.sfx:
            assert c.name in SFX, c.name
            assert 0 <= c.t <= 1
        for p in sc.props:
            assert prop_svg(p.name, p.x, p.y, p.scale, 0.0, p.anim, get_style("cartoon")).startswith("<g")
        for k in sc.camera:
            assert k.shot in ("wide", "medium", "close", "follow")


@pytest.mark.parametrize("idea", IDEAS)
def test_every_scene_has_dialogue_or_narration_without_filler(idea):
    s = generate_story(idea)
    for sc in s.scenes:
        total = " ".join(l.text for l in sc.lines)
        assert len(total.split()) >= 5, f"escena {sc.index} casi vacía"
    assert len({l.text for sc in s.scenes for l in sc.lines}) == sum(len(sc.lines) for sc in s.scenes), "líneas repetidas"


def test_deterministic_and_hero_override():
    idea = "Un gato quiere ser famoso"
    assert generate_story(idea).title == generate_story(idea).title
    s = generate_story(idea, hero_id="bruno")
    assert "Bruno" in s.understood["protagonista"]
    s2 = generate_story(idea, hero_id="fausto")
    assert "fausto" in s2.characters
    # el rival nunca es el mismo que el protagonista
    names = [c.name for c in s2.characters.values()]
    assert len(names) == len(set(names))


def test_detectors():
    assert detect_species("la coneja salta") == "conejo"
    assert detect_species("nada") is None
    assert detect_theme("quiere ser millonario") == "dinero"
    assert detect_theme("cosas al azar") == "superacion"


def test_invalid_ideas():
    with pytest.raises(ValueError):
        generate_story("  ab ")
    with pytest.raises(ValueError):
        generate_story("x" * 401)
    with pytest.raises(ValueError):
        generate_story("un gato", hero_id="dragon")
