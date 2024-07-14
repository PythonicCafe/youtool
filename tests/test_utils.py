import io
import re
from pathlib import Path

import webvtt

from youtool import utils

TEST_DATA_DIR = Path(__file__).parent / "data"


def extract_vtt_words(content):
    vtt = webvtt.read_buffer(io.StringIO(content))
    words = " ".join(caption.text for caption in vtt.captions)
    return re.sub("[[:punct:]]+", "", words).lower().split()


def test_simplify_vtt():
    # Each transcription has 3 versions:
    # - whisper-clean: whisper transcription of the audio file without word timings (similar to "simplified" version)
    # - whisper-words: whisper transcription of the audio file with word timings (more verbose)
    # - youtube-auto: automatic transcription downloaded from YouTube, with lots of garbage
    filenames = [
        TEST_DATA_DIR / "whisper-clean-hd-notebook.vtt",
        TEST_DATA_DIR / "whisper-words-hd-notebook.vtt",
        TEST_DATA_DIR / "youtube-auto-hd-notebook.vtt",
    ]
    content = []
    for filename in filenames:
        with open(filename) as fobj:
            content.append(fobj.read())
    # Check if VTTs are different (some have duplication, word timings etc.)
    assert content[0] != content[1]
    assert content[1] != content[2]
    # Check if all whisper simplified versions are the same (timings will be the same)
    assert utils.simplify_vtt(content[0]) == utils.simplify_vtt(content[1])
    # Check if simplified version of whisper with no word timings has more or less the same number of words of
    # simplified YouTube version
    whisper_words = extract_vtt_words(utils.simplify_vtt(content[0]))
    youtube_words = extract_vtt_words(utils.simplify_vtt(content[2]))
    # Number of words (not unique) will be more or less the same if simplification worked - if not, difference will be
    # huge (`youtube_words` would be higher).
    assert 0.9 <= len(whisper_words) / len(youtube_words) <= 1.1

    filenames = [
        TEST_DATA_DIR / "whisper-clean-limpeza-nespresso.vtt",
        TEST_DATA_DIR / "whisper-words-limpeza-nespresso.vtt",
        TEST_DATA_DIR / "youtube-auto-limpeza-nespresso.vtt",
    ]
    content = []
    for filename in filenames:
        with open(filename) as fobj:
            content.append(fobj.read())
    # Check if VTTs are different (some have duplication, word timings etc.)
    assert content[0] != content[1]
    assert content[1] != content[2]
    # Check if all whisper simplified versions are the same (timings will be the same)
    assert utils.simplify_vtt(content[0]) == utils.simplify_vtt(content[1])
    # Check if simplified version of whisper with no word timings has more or less the same number of words of
    # simplified YouTube version
    whisper_words = extract_vtt_words(utils.simplify_vtt(content[0]))
    youtube_words = extract_vtt_words(utils.simplify_vtt(content[2]))
    # Number of words (not unique) will be more or less the same if simplification worked - if not, difference will be
    # huge (`youtube_words` would be higher).
    assert 0.9 <= len(whisper_words) / len(youtube_words) <= 1.1
