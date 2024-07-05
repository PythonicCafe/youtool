import pytest

from pathlib import Path
from subprocess import run

from youtool.commands import COMMANDS

from youtool.commands.base import Command


@pytest.mark.parametrize(
    "command", COMMANDS
)
def test_missing_api_key(monkeypatch: pytest.MonkeyPatch, command: Command):
    monkeypatch.delenv('YOUTUBE_API_KEY', raising=False)
    cli_path = Path("youtool") / "cli.py"
    command_string = ["python", cli_path, command.name]
    for arg in command.arguments:
        if arg.get("required"):
            command_string.append(arg.get("name"))
            command_string.append("test_value")
    result = run(command_string, capture_output=True, text=True, check=False)

    assert result.returncode == 2
    assert "YouTube API Key is required" in result.stderr
