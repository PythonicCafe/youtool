import pytest

from subprocess import run

from youtool.commands import COMMANDS

from youtool.commands.base import Command


@pytest.mark.parametrize(
    "command", COMMANDS
)
def test_missing_api_key(monkeypatch: pytest.MonkeyPatch, command: Command):
    monkeypatch.delenv('YOUTUBE_API_KEY', raising=False)
    cli_path = "youtool/cli.py"
    command = ["python", cli_path, command.name]
    result = run(command, capture_output=True, text=True, check=False)

    assert result.returncode == 2
    assert "YouTube API Key is required" in result.stderr