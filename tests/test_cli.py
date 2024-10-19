from subprocess import run

import pytest

ERROR_RETURN_CODE = 2
ERROR_STRING = "You must specify either --api-key or set YOUTUBE_API_KEY for this command"

# Commands that DO NOT REQUIRE YouTube API key


def test_missing_api_key_channel_id(monkeypatch: pytest.MonkeyPatch):
    """Test to verify behavior when the YouTube API key is missing for some commands"""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    command = ["python", "-m", "youtool.cli", "channel-id", "--urls", "https://youtube.com/c/PythonicCafe"]
    result = run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0


def test_missing_api_key_video_livechat(monkeypatch: pytest.MonkeyPatch):
    """Test to verify behavior when the YouTube API key is missing for some commands"""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    command = ["python", "-m", "youtool.cli", "video-livechat", "--id", "NtZY3AmsBSk"]
    result = run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0


def test_missing_api_key_video_transcription(monkeypatch: pytest.MonkeyPatch):
    """Test to verify behavior when the YouTube API key is missing for some commands"""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    command = ["python", "-m", "youtool.cli", "video-transcription", "pt", "--ids", "NtZY3AmsBSk"]
    result = run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0


# Commands that REQUIRE YouTube API key


def test_missing_api_key_channel_info(monkeypatch: pytest.MonkeyPatch):
    """Test to verify behavior when the YouTube API key is missing for some commands"""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    command = ["python", "-m", "youtool.cli", "channel-info", "--urls", "https://youtube.com/c/PythonicCafe"]
    result = run(command, capture_output=True, text=True, check=False)
    assert result.returncode == ERROR_RETURN_CODE
    assert ERROR_STRING in result.stderr


def test_missing_api_key_video_info(monkeypatch: pytest.MonkeyPatch):
    """Test to verify behavior when the YouTube API key is missing for some commands"""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    command = ["python", "-m", "youtool.cli", "video-info", "--ids", "Q3Kgd1IirgM"]
    result = run(command, capture_output=True, text=True, check=False)
    assert result.returncode == ERROR_RETURN_CODE
    assert ERROR_STRING in result.stderr


def test_missing_api_key_video_search(monkeypatch: pytest.MonkeyPatch):
    """Test to verify behavior when the YouTube API key is missing for some commands"""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    # TODO: fix call
    command = ["python", "-m", "youtool.cli", "video-search", "--ids", "Q3Kgd1IirgM"]
    result = run(command, capture_output=True, text=True, check=False)
    assert result.returncode == ERROR_RETURN_CODE
    assert ERROR_STRING in result.stderr


def test_missing_api_key_video_comments(monkeypatch: pytest.MonkeyPatch):
    """Test to verify behavior when the YouTube API key is missing for some commands"""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    command = ["python", "-m", "youtool.cli", "video-comments", "--id", "Q3Kgd1IirgM"]
    result = run(command, capture_output=True, text=True, check=False)
    assert result.returncode == ERROR_RETURN_CODE
    assert ERROR_STRING in result.stderr
