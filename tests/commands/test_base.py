import csv
import argparse
import pytest

from io import StringIO
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from youtool.commands import Command


class TestCommand(Command):
    name = "command_name"
    arguments = [
        {"name": "--test-arg", "help": "Test argument", "default": "default_value", "type": str}
    ]

    @classmethod
    def execute(cls, **kwargs):
        return "executed"

@pytest.fixture
def subparsers():
    """Fixture to create subparsers for argument parsing."""
    parser = argparse.ArgumentParser()
    return parser.add_subparsers()


def test_generate_parser(subparsers):
    """Test to verify the parser generation.

    This test checks if the `generate_parser` method correctly generates a parser
    for the command and sets the appropriate properties
    """
    parser = TestCommand.generate_parser(subparsers)

    assert parser is not None, "Parser should not be None"
    assert isinstance(parser, argparse.ArgumentParser), "Parser should be an instance of argparse.ArgumentParser"
    assert parser.prog.endswith(TestCommand.name), f"Parser prog should end with '{TestCommand.name}'"


def test_parse_arguments(subparsers):
    """Test to verify argument parsing.

    This test checks if the `parse_arguments` method correctly adds the command's
    arguments to the parser and sets the default function to the command's execute method.
    """
    subparsers_mock = MagicMock(spec=subparsers)

    TestCommand.parse_arguments(subparsers_mock)

    subparsers_mock.add_parser.assert_called_once_with(TestCommand.name, help=TestCommand.__doc__)
    parser_mock = subparsers_mock.add_parser.return_value
    parser_mock.add_argument.assert_called_once_with("--test-arg", help="Test argument", default="default_value", type=str)
    parser_mock.set_defaults.assert_called_once_with(func=TestCommand.execute)


def test_command():
    """Test to verify that the `execute` method is implemented.

    This test ensures that if a command does not implement the `execute` method,
    a `NotImplementedError` is raised.
    """
    class MyCommand(Command):
        pass

    with pytest.raises(NotImplementedError):
        MyCommand.execute()


@pytest.fixture
def mock_csv_file():
    """Fixture to provide mock CSV content for tests."""

    csv_content = """URL
    http://example.com
    http://example2.com
    """
    return csv_content

def test_data_from_csv_valid(mock_csv_file):
    """Test to verify reading data from a valid CSV file.

    This test checks if the `data_from_csv` method correctly reads data from a valid CSV file
    and returns the expected list of URLs.

    Args:
        mock_csv_file (str): The mock CSV file content.
    """
    with patch('pathlib.Path.is_file', return_value=True):
        with patch('builtins.open', mock_open(read_data=mock_csv_file)):
            data_column_name = "URL"
            file_path = Path("tests/commands/csv_valid.csv")
            result = Command.data_from_csv(file_path, data_column_name)
            assert len(result) == 2
            assert result[0] == "http://example.com"
            assert result[1] == "http://example2.com"

def test_data_from_csv_file_not_found():
    """Test to verify behavior when the specified column is not found in the CSV file.

    This test checks if the `data_from_csv` method raises an exception when the specified
    column does not exist in the CSV file.
    """
    with patch('pathlib.Path.is_file', return_value=False):
        file_path = Path("/fake/path/not_found.csv")
        with pytest.raises(FileNotFoundError):
            Command.data_from_csv(file_path, "URL")

def test_data_from_csv_column_not_found(mock_csv_file):
    with patch('pathlib.Path.is_file', return_value=True):
        with patch('builtins.open', mock_open(read_data=mock_csv_file)):
            file_path = Path("tests/commands/csv_column_not_found.csv")
            with pytest.raises(Exception) as exc_info:
                Command.data_from_csv(file_path, "NonExistentColumn")
            assert "Column NonExistentColumn not found on tests/commands/csv_column_not_found.csv" in str(exc_info.value), "Exception message should contain column not found error"


@pytest.fixture
def sample_data():
    """Fixture to provide sample data for tests."""
    return [
        {"id": "123", "name": "Channel One"},
        {"id": "456", "name": "Channel Two"}
    ]

def test_data_to_csv_with_output_file_path(tmp_path, sample_data):
    """Test to verify writing data to a CSV file with an output file path specified.

    This test checks if the `data_to_csv` method correctly writes the sample data to
    a CSV file when an output file path is provided.
    """
    output_file_path = tmp_path / "output.csv"
    
    result_path = Command.data_to_csv(sample_data, str(output_file_path))
    
    assert result_path == str(output_file_path), "The returned path should match the provided output file path"
    assert output_file_path.exists(), "The output file should exist"
    with output_file_path.open('r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2, "There should be two rows in the output CSV"
        assert rows[0]["id"] == "123" and rows[1]["id"] == "456", "The IDs should match the sample data"

def test_data_to_csv_without_output_file_path(sample_data):
    """Test to verify writing data to a CSV format without an output file path specified.

    This test checks if the `data_to_csv` method correctly returns the CSV content
    as a string when no output file path is provided.
    """
    csv_content = Command.data_to_csv(sample_data)
    
    assert "id,name" in csv_content
    assert "123,Channel One" in csv_content
    assert "456,Channel Two" in csv_content

def test_data_to_csv_output(tmp_path):
    """
    Test to verify the content of the output CSV file.

    This test checks if the `data_to_csv` method writes the expected content
    to the output CSV file.
    """
    output_file_path = tmp_path / "output.csv"

    data = [
        {"id": 1, "name": "Test1"},
        {"id": 2, "name": "Test2"}
    ]

    expected_output = "id,name\n1,Test1\n2,Test2\n"
    result = Command.data_to_csv(data, str(output_file_path))
    assert Path(output_file_path).is_file()
    assert expected_output == Path(output_file_path).read_text()
