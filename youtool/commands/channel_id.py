
from pathlib import Path

from youtool import YouTube

from .base import Command


class ChannelId(Command):
    """Get channel IDs from a list of URLs (or CSV filename with URLs inside), generate CSV output (just the IDs)."""
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

    @classmethod
    def execute(cls, **kwargs) -> str:  # noqa: D417
        """Execute the channel-id command to fetch YouTube channel IDs from URLs and save them to a CSV file.

        This method retrieves YouTube channel IDs from a list of provided URLs or from a file containing URLs.
        It then saves these channel IDs to a CSV file if an output file path is specified.

        Args:
            urls (list[str], optional): A list of YouTube channel URLs. Either this or urls_file_path must be provided.
            urls_file_path (str, optional): Path to a CSV file containing YouTube channel URLs.
                                            Requires url_column_name to specify the column with URLs.
            output_file_path (str, optional): Path to the output CSV file where channel IDs will be saved.
                                              If not provided, the result will be returned as a string.
            api_key (str): The API key to authenticate with the YouTube Data API.
            url_column_name (str, optional): The name of the column in the urls_file_path CSV file that contains the URLs.
                                             Default is "url".
            id_column_name (str, optional): The name of the column for channel IDs in the output CSV file.
                                            Default is "channel_id".

        Returns:
            str: A message indicating the result of the command. If output_file_path is specified, the message will
                 include the path to the generated CSV file. Otherwise, it will return the result as a string.

        Raises:
            Exception: If neither urls nor urls_file_path is provided.
        """
        urls = kwargs.get("urls")
        urls_file_path = kwargs.get("urls_file_path")
        output_file_path = kwargs.get("output_file_path")
        api_key = kwargs.get("api_key")

        url_column_name = kwargs.get("url_column_name")
        id_column_name = kwargs.get("id_column_name")

        if urls_file_path and not urls:
            urls = cls.data_from_csv(
                file_path=Path(urls_file_path),
                data_column_name=url_column_name or cls.URL_COLUMN_NAME
            )

        if not urls:
            raise Exception("Either 'username' or 'url' must be provided for the channel-id command")

        youtube = YouTube([api_key], disable_ipv6=True)

        channels_ids = [
            youtube.channel_id_from_url(url) for url in urls if url
        ]

        result = cls.data_to_csv(
            data=[
                {
                    (id_column_name or cls.CHANNEL_ID_COLUMN_NAME): channel_id for channel_id in channels_ids
                }
            ],
            output_file_path=output_file_path
        )

        return result