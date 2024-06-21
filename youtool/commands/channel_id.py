import os
import csv

from typing import List
from datetime import datetime
from io import StringIO

from youtool import YouTube

from .base import Command


class ChannelId(Command):
    """
    Get channel IDs from a list of URLs (or CSV filename with URLs inside), generate CSV output (just the IDs)
    """
    name = "channel-id"
    arguments = [
        {"name": "--urls", "type": str, "help": "Channels urls", "nargs": "*"},
        {"name": "--urls-file-path", "type": str, "help": "Channels urls csv file path"},
        {"name": "--output-file-path", "type": str, "help": "Output csv file path"},
        {"name": "--url-column-name", "type": str, "help": "URL column name on csv input files"},
        {"name": "--id-column-name", "type": str, "help": "Channel ID column name on csv output files"}
    ]

    URL_COLUMN_NAME: str = "channel_url"
    CHANNEL_ID_COLUMN_NAME: str = "channel_id"

    @staticmethod
    def urls_from_file(file_path: str, url_column_name: str = None) -> List[str]:
        """
        Extracts a list of URLs from a specified CSV file.

        Args: file_path (str): The path to the CSV file containing the URLs.
            url_column_name (str, optional): The name of the column in the CSV file that contains the URLs.
                                            If not provided, it defaults to `ChannelId.URL_COLUMN_NAME`.

        Returns:
            List[str]: A list of URLs extracted from the specified CSV file.

        Raises:
            Exception: If the file path is invalid or the file cannot be found.
        """
        url_column_name = url_column_name or ChannelId.URL_COLUMN_NAME
        urls = []

        if not os.path.isfile(file_path):
            raise Exception(f"Invalid file path: {file_path}")

        with open(file_path, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                urls.append(row.get(url_column_name))
        return urls

    @staticmethod
    def ids_to_csv(channels_ids: List[str], output_file_path: str = None, channel_id_column_name: str = None) -> str:
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
        channel_id_column_name = channel_id_column_name or ChannelId.CHANNEL_ID_COLUMN_NAME

        if output_file_path and os.path.isdir(output_file_path):
            timestamp = datetime.now().strftime("%M%S%f")
            output_file_path = os.path.join(output_file_path, f"channel_ids_{timestamp}.csv")

        with (output_file_path and open(output_file_path, 'w', newline='') or StringIO()) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=[channel_id_column_name])
            writer.writeheader()
            writer.writerows(
                [{channel_id_column_name: channel_id} for channel_id in channels_ids]
            )
            return output_file_path or csv_file.getvalue()

    @staticmethod
    def execute(**kwargs) -> str:
        """
        Execute the channel-id command to fetch YouTube channel IDs from URLs and save them to a CSV file.

        This method retrieves YouTube channel IDs from a list of provided URLs or from a file containing URLs.
        It then saves these channel IDs to a CSV file if an output file path is specified.

        Args:
            urls (list[str], optional): A list of YouTube channel URLs. If not provided, `urls_file_path` must be specified.
            urls_file_path (str, optional): Path to a CSV file containing YouTube channel URLs. 
                                            The file should contain a column with URLs, specified by `url_column_name`.
            output_file_path (str, optional): Path to the output CSV file where channel IDs will be saved.
                                            If not provided, the result will be returned as a string.
            api_key (str): The API key to authenticate with the YouTube Data API.
            url_column_name (str, optional): The name of the column in the `urls_file_path` CSV file that contains the URLs.
                                            Default is "url".
            id_column_name (str, optional): The name of the column for channel IDs in the output CSV file.
                                            Default is "channel_id".

        Returns:
            str: A message indicating the result of the command. If `output_file_path` is specified, the message will
                include the path to the generated CSV file. Otherwise, it will return the result as a string.

        Raises:
            Exception: If neither `urls` nor `urls_file_path` is provided.
        """
        urls = kwargs.get("urls")
        urls_file_path = kwargs.get("urls_file_path")
        output_file_path = kwargs.get("output_file_path")
        api_key = kwargs.get("api_key")

        url_column_name = kwargs.get("url_column_name")
        id_column_name = kwargs.get("id_column_name")

        urls = urls or ChannelId.urls_from_file(urls_file_path, url_column_name)

        if not urls:
            raise Exception("username or url required on channel-id command")

        youtube = YouTube([api_key], disable_ipv6=True)

        channels_ids = [
            youtube.channel_id_from_url(url) for url in urls
        ]

        result = ChannelId.ids_to_csv(
            channels_ids=channels_ids,
            output_file_path=output_file_path,
            channel_id_column_name=id_column_name
        )

        if output_file_path:
            return f"CSV File with channels ids generated: {result}"
        return result
