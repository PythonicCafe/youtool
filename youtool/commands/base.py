import csv
import argparse

from typing import List, Dict, Any, Optional
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
    def generate_parser(cls, subparsers: argparse._SubParsersAction):
        """
        Creates a parser for the command and adds it to the subparsers.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers action to add the parser to.

        Returns:
            argparse.ArgumentParser: The parser for the command.
        """
        return subparsers.add_parser(cls.name, help=cls.__doc__)

    @classmethod
    def parse_arguments(cls, subparsers: argparse._SubParsersAction) -> None:
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
    def execute(cls, **kwargs) -> str:
        """
        Executes the command.

        This method should be overridden by subclasses to define the command's behavior.

        Args:
            arguments (argparse.Namespace): The parsed arguments for the command.
        """
        raise NotImplementedError()

    @staticmethod
    def data_from_csv(file_path: Path, data_column_name: Optional[str] = None) -> List[str]:
        """
        Extracts a list of URLs from a specified CSV file.

        Args:
            file_path: The path to the CSV file containing the URLs.
            data_column_name: The name of the column in the CSV file that contains the URLs.
                                If not provided, it defaults to `ChannelId.URL_COLUMN_NAME`.

        Returns:
            A list of URLs extracted from the specified CSV file.

        Raises:
            Exception: If the file path is invalid or the file cannot be found.
        """
        data = []

        if not file_path.is_file():
            raise FileNotFoundError(f"Invalid file path: {file_path}")

        with file_path.open('r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            fieldnames = reader.fieldnames

            if fieldnames is None:
                raise ValueError("Fieldnames is None")
            
            if data_column_name not in fieldnames:
                raise Exception(f"Column {data_column_name} not found on {file_path}")
            for row in reader:
                value = row.get(data_column_name)
                if value is not None:
                    data.append(str(value))
        return data

    @classmethod
    def data_to_csv(cls, data: List[Dict], output_file_path: Optional[str] = None) -> str:
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