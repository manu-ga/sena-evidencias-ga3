import numpy as np
import pytest

from factory.audio.mixer import auto_sfx, mix_soundtrack
from factory.audio.music import MOODS, render_music
from factory.audio.sfx import SFX, get_sfx
from factory.audio.tts import PiperProvider, envelope, speak
from factory.models import Beat, Scene, SfxCue


@pytest.mark.parametrize("name", list(SFX))
def test_sfx_are_audible_and_bounded(name):
    x = get_sfx(name)
    assert len(x) > 500
    assert np.isfinite(x).all()
    assert 0.1 < np.abs(x).max() <= 1.0
    assert np.sqrt((x ** 2).mean()) > 0.01


@pytest.mark.parametrize("mood", list(MOODS))
def test_music_length_and_level(mood):
    m = render_music(mood, 5.0)
    assert abs(len(m) - 5 * 44100) <= 1
    assert np.isfinite(m).all() and 0.1 < np.abs(m).max() <= 0.6


def test_mix_has_voice_sfx_music_and_no_clipping():
    sc = Scene(1, "t", "parque", "alegre", [], [Beat("a", "walk", 0.0, 0.6, -100, 500)], ["a"],
               sfx=[SfxCue(0.5, "coin")], duration=8.0, line_times=[])
    voice = (np.sin(2 * np.pi * 200 * np.arange(44100 * 2) / 44100) * 0.4).astype(np.float32)
    mix, stats = mix_soundtrack([sc], [0.0], 8.5, [[(1.0, voice)]])
    assert len(mix) == int(8.5 * 44100)
    assert stats["pico"] > 0 and np.abs(mix).max() <= 0.93
    assert stats["rms_voz"] > 0 and stats["rms_musica"] > 0 and stats["rms_efectos"] > 0
    assert any(c[1] == "step" for c in auto_sfx(sc))


requires_voices = pytest.mark.skipif(not PiperProvider().available_voices(), reason="No hay voces Piper descargadas")


@requires_voices
@pytest.mark.parametrize("voice", PiperProvider().available_voices())
def test_piper_really_speaks(tmp_path, voice):
    audio, env = speak(PiperProvider(), "Hola, soy un animal que habla.", voice, 1.0, 1.0, tmp_path, "t")
    assert len(audio) / 44100 > 1.0
    assert np.sqrt((audio ** 2).mean()) > 0.02
    assert max(env) > 0.8 and sum(1 for v in env if v > 0.3) > 30   # la boca tendría movimiento


@requires_voices
def test_pitch_changes_the_voice_but_not_the_duration(tmp_path):
    p = PiperProvider()
    voice = p.available_voices()[0]
    txt = "Una frase de prueba para el tono."
    # Piper varía ~8 % la duración entre dos síntesis iguales: se comparan promedios
    a_all = [speak(p, txt, voice, 1.0, 1.0, tmp_path, f"a{i}")[0] for i in range(4)]
    b_all = [speak(p, txt, voice, 1.3, 1.0, tmp_path, f"b{i}")[0] for i in range(4)]
    a, b = a_all[0], b_all[0]
    mean_a = sum(len(x) for x in a_all) / 4
    mean_b = sum(len(x) for x in b_all) / 4
    assert abs(mean_a - mean_b) / mean_a < 0.06

    def f0(x):
        x = x[: 44100]
        ac = np.correlate(x - x.mean(), x - x.mean(), "full")[len(x) - 1:]
        lo, hi = 110, 600
        return 44100 / (lo + np.argmax(ac[lo:hi]))
    assert f0(b[10000:]) != f0(a[10000:])


def test_envelope_silence_is_zero():
    assert max(envelope(np.zeros(44100, np.float32)) or [0]) == 0
