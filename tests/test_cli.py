import pytest

from subprocess import run

from youtool.commands import COMMANDS

from youtool.commands.base import Command


@pytest.mark.parametrize(
    "command", COMMANDS
)
def test_missing_api_key(monkeypatch: pytest.MonkeyPatch, command: Command):
    """Test to verify behavior when the YouTube API key is missing.
    
    This test ensures that when the YouTube API key is not set, running any command
    from the youtool CLI results in an appropriate error message and exit code.
    """
    monkeypatch.delenv('YOUTUBE_API_KEY', raising=False)
    cli_path = "youtool/cli.py"
    command = ["python", cli_path, command.name]
    result = run(command, capture_output=True, text=True, check=False)

    assert result.returncode == 2
    assert "YouTube API Key is required" in result.stderr