import csv
import argparse

from typing import List, Dict, Any, Self
from io import StringIO
from pathlib import Path
from datetime import datetime


class Command():
    """
    A base class for commands to inherit from, following a specific structure.
    
    Attributes:
        name (str): The name of the command.
        arguments (List[Dict[str, Any]]): A list of dictionaries, each representing an argument for the command.
    """
    name: str
    arguments: List[Dict[str, Any]]

    @classmethod
    def generate_parser(cls: Self, subparsers: argparse._SubParsersAction):
        """
        Creates a parser for the command and adds it to the subparsers.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers action to add the parser to.

        Returns:
            argparse.ArgumentParser: The parser for the command.
        """
        return subparsers.add_parser(cls.name, help=cls.__doc__)

    @classmethod
    def parse_arguments(cls: Self, subparsers: argparse._SubParsersAction) -> None:
        """
        Parses the arguments for the command and sets the command's execute method as the default function to call.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers action to add the parser to.
        """
        parser = cls.generate_parser(subparsers)
        for argument in cls.arguments:
            argument_copy = {**argument}
            argument_name = argument_copy.pop("name")
            parser.add_argument(argument_name, **argument_copy)
        parser.set_defaults(func=cls.execute)

    @classmethod
    def execute(cls: Self, arguments: argparse.Namespace):
        """
        Executes the command.

        This method should be overridden by subclasses to define the command's behavior.

        Args:
            arguments (argparse.Namespace): The parsed arguments for the command.
        """
        raise NotImplementedError()

    @staticmethod
    def data_from_csv(file_path: str, data_column_name: str = None) -> List[str]:
        """
        Extracts a list of URLs from a specified CSV file.

        Args: file_path (str): The path to the CSV file containing the URLs.
            data_column_name (str, optional): The name of the column in the CSV file that contains the URLs.
                                            If not provided, it defaults to `ChannelId.URL_COLUMN_NAME`.

        Returns:
            List[str]: A list of URLs extracted from the specified CSV file.

        Raises:
            Exception: If the file path is invalid or the file cannot be found.
        """
        data = []

        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(f"Invalid file path: {file_path}")

        with file_path.open('r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            if data_column_name not in reader.fieldnames:
                raise Exception(f"Column {data_column_name} not found on {file_path}")
            for row in reader:
                data.append(row.get(data_column_name))
        return data

    @classmethod
    def data_to_csv(cls: Self, data: List[Dict], output_file_path: str = None) -> str:
        """
        Converts a list of channel IDs into a CSV file.

        Parameters:
        channels_ids (List[str]): List of channel IDs to be written to the CSV.
        output_file_path (str, optional): Path to the file where the CSV will be saved. If not provided, the CSV will be returned as a string.
        channel_id_column_name (str, optional): Name of the column in the CSV that will contain the channel IDs. 
                                                If not provided, the default value defined in ChannelId.CHANNEL_ID_COLUMN_NAME will be used.

        Returns:
        str: The path of the created CSV file or, if no path is provided, the contents of the CSV as a string.
        """
        if output_file_path:
            output_path = Path(output_file_path)
            if output_path.is_dir():
                command_name = cls.name.replace("-", "_")
                timestamp = datetime.now().strftime("%M%S%f")
                output_file_path = output_path / f"{command_name}_{timestamp}.csv"

        with (Path(output_file_path).open('w', newline='') if output_file_path else StringIO()) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(data[0].keys()) if data else [])
            writer.writeheader()
            writer.writerows(data)
            return str(output_file_path) if output_file_path else csv_file.getvalue()
