import csv
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qsl, urlparse


class Command:
    """A base class for commands to inherit from, following a specific structure.

    Attributes:
        name (str): The name of the command.
    """

    name: str

    @staticmethod
    def video_id_from_url(video_url: str) -> Optional[str]:
        parsed_url = urlparse(video_url)
        parsed_url_query = dict(parse_qsl(parsed_url.query))
        return parsed_url_query.get("v")

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
        return (
            {field: value for field, value in video_info.items() if field in info_columns}
            if info_columns
            else video_info
        )

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
        if not file_path.exists():
            raise FileNotFoundError(f"Invalid filename: {file_path}")
        with file_path.open(mode="r") as csv_file:
            reader = csv.DictReader(csv_file)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError(f"No fields found for file: {file_path}")
            elif data_column_name not in fieldnames:
                raise Exception(f"Column {data_column_name} not found on {file_path}")
            for row in reader:
                value = row[data_column_name].strip()
                if value:
                    yield value

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
        output_path = None
        if output_file_path:
            output_path = Path(output_file_path)

        with output_path.open(mode="w") if output_path else StringIO() as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(data[0].keys()) if data else [])
            writer.writeheader()
            writer.writerows(data)
            return str(output_file_path) if output_file_path else csv_file.getvalue()
