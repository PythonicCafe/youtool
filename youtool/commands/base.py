import csv
import argparse

from typing import List, Dict, Any, Optional
from io import StringIO
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qsl


class Command:
    """A base class for commands to inherit from, following a specific structure.
    
    Attributes:
        name (str): The name of the command.
        arguments (List[Dict[str, Any]]): A list of dictionaries, each representing an argument for the command.
    """
    name: str
    arguments: List[Dict[str, Any]]

    @staticmethod
    def video_id_from_url(video_url: str) -> Optional[str]:
        parsed_url = urlparse(video_url)
        parsed_url_query = dict(parse_qsl(parsed_url.query))
        return parsed_url_query.get("v")

    @classmethod
    def generate_parser(cls, subparsers: argparse._SubParsersAction):
        """Creates a parser for the command and adds it to the subparsers.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers action to add the parser to.

        Returns:
            argparse.ArgumentParser: The parser for the command.
        """
        return subparsers.add_parser(cls.name, help=cls.__doc__)

    @classmethod
    def parse_arguments(cls, subparsers: argparse._SubParsersAction) -> None:
        """Parses the arguments for the command and sets the command's execute method as the default function to call.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers action to add the parser to.
        """
        parser = cls.generate_parser(subparsers)
        for argument in cls.arguments:
            argument_copy = {**argument}
            argument_name = argument_copy.pop("name")
            parser.add_argument(argument_name, **argument_copy)
        parser.set_defaults(func=cls.execute)

    @staticmethod
    def filter_fields(video_info: Dict, info_columns: Optional[List] = None) -> Dict:
        """Filters the fields of a dictionary containing video information based on specified columns.

        Args:
            video_info (Dict): A dictionary containing video information.
            info_columns (Optional[List], optional): A list specifying which fields to include in the filtered output. 
            If None, returns the entire video_info dictionary. Defaults to None.

        Returns:
            A dictionary containing only the fields specified in info_columns (if provided) 
            or the entire video_info dictionary if info_columns is None.
        """
        return {
            field: value for field, value in video_info.items() if field in info_columns
        } if info_columns else video_info


    @classmethod
    def execute(cls, **kwargs) -> str:  # noqa: D417
        """Executes the command.

        This method should be overridden by subclasses to define the command's behavior.

        Args:
            arguments (argparse.Namespace): The parsed arguments for the command.
        """
        raise NotImplementedError()

    @staticmethod
    def data_from_csv(file_path: Path, data_column_name: Optional[str] = None) -> List[str]:
        """Extracts a list of URLs from a specified CSV file.

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
                if raise_column_exception:
                    raise Exception(f"Column {data_column_name} not found on {file_path}")
                return data

            for row in reader:
                value = row.get(data_column_name)
                if value is not None:
                    data.append(str(value))
        return data

    @classmethod
    def data_to_csv(cls, data: List[Dict], output_file_path: Optional[str] = None) -> str:
        """Converts a list of channel IDs into a CSV file.

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
