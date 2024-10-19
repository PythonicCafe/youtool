import os
from typing import Dict, List, Optional, Self

from .. import YouTube
from .base import Command


class ChannelInfo(Command):
    """Get channel info from a list of IDs (or CSV filename with IDs inside), generate CSV output
    (same schema for `channel` dicts)
    """

    name = "channel-info"
    URL_COLUMN_NAME: str = "channel_url"
    USERNAME_COLUMN_NAME: str = "channel_username"
    ID_COLUMN_NAME: str = "channel_id"
    INFO_COLUMNS: List[str] = [
        "id",
        "title",
        "description",
        "published_at",
        "view_count",
        "subscriber_count",
        "video_count",
    ]

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument(
            "--api-key", type=str, help="YouTube API Key", dest="api_key", default=os.environ.get("YOUTUBE_API_KEY")
        )
        parser.add_argument("--urls", type=str, help="Channel URLs", nargs="*")
        parser.add_argument("--usernames", type=str, help="Channel usernames", nargs="*")
        parser.add_argument("--ids", type=str, help="Channel IDs", nargs="*")
        parser.add_argument("--urls-file-path", type=str, help="Channel URLs CSV file path")
        parser.add_argument("--usernames-file-path", type=str, help="Channel usernames CSV file path")
        parser.add_argument("--ids-file-path", type=str, help="Channel IDs CSV file path")
        parser.add_argument("--output-file-path", type=str, help="Output CSV file path")
        parser.add_argument("--url-column-name", type=str, help="URL column name on CSV input files")
        parser.add_argument("--username-column-name", type=str, help="Username column name on CSV input files")
        parser.add_argument("--id-column-name", type=str, help="ID column name on CSV input files")

    @staticmethod
    def filter_fields(channel_info: Dict, info_columns: Optional[List] = None):
        """Filters the fields of a dictionary containing channel information based on
        specified columns.

        Args:
            channel_info (Dict): A dictionary containing channel information.
            info_columns (Optional[List], optional): A list specifying which fields
                to include in the filtered output. If None, returns the entire
                channel_info dictionary. Defaults to None.

        Returns:
            Dict: A dictionary containing only the fields specified in info_columns
                (if provided) or the entire channel_info dictionary if info_columns is None.
        """
        return (
            {field: value for field, value in channel_info.items() if field in info_columns}
            if info_columns
            else channel_info
        )

    @classmethod
    def execute(cls: Self, **kwargs) -> str:
        """Execute the channel-info command to fetch YouTube channel information from URLs or
        usernames and save them to a CSV file.

        Args:
            urls (list[str], optional): A list of YouTube channel URLs. If not provided, `urls_file_path` must be specified.
            usernames (list[str], optional): A list of YouTube channel usernames. If not provided, `usernames_file_path` must be specified.
            urls_file_path (str, optional): Path to a CSV file containing YouTube channel URLs.
            usernames_file_path (str, optional): Path to a CSV file containing YouTube channel usernames.
            output_file_path (str, optional): Path to the output CSV file where channel information will be saved.
            api_key (str): The API key to authenticate with the YouTube Data API.
            url_column_name (str, optional): The name of the column in the `urls_file_path` CSV file that contains the URLs.
                                            Default is "channel_url".
            username_column_name (str, optional): The name of the column in the `usernames_file_path` CSV file that contains the usernames.
                                            Default is "channel_username".
            info_columns (str, optional): Comma-separated list of columns to include in the output CSV.
                                            Default is the class attribute `INFO_COLUMNS`.

        Returns:
            str: A message indicating the result of the command. If `output_file_path` is specified, the message will
                include the path to the generated CSV file. Otherwise, it will return the result as a string.

        Raises:
            Exception: If neither `urls`, `usernames`, `urls_file_path` nor `usernames_file_path` is provided.
        """

        urls = kwargs.get("urls")
        usernames = kwargs.get("usernames")
        urls_file_path = kwargs.get("urls_file_path")
        usernames_file_path = kwargs.get("usernames_file_path")
        output_file_path = kwargs.get("output_file_path")
        api_key = kwargs.get("api_key")

        url_column_name = kwargs.get("url_column_name")
        username_column_name = kwargs.get("username_column_name")
        info_columns = kwargs.get("info_columns")

        info_columns = (
            [column.strip() for column in info_columns.split(",")] if info_columns else ChannelInfo.INFO_COLUMNS
        )

        if urls_file_path and not urls:
            urls = ChannelInfo.data_from_file(urls_file_path, url_column_name)
        if usernames_file_path and not usernames:
            usernames = ChannelInfo.data_from_file(usernames_file_path, username_column_name)

        if not urls and not usernames:
            raise Exception("Either 'urls' or 'usernames' must be provided for the channel-info command")

        youtube = YouTube([api_key], disable_ipv6=True)

        channels_ids = [youtube.channel_id_from_url(url) for url in (urls or []) if url] + [
            youtube.channel_id_from_username(username) for username in (usernames or []) if username
        ]
        channel_ids = list(set([channel_id for channel_id in channels_ids if channel_id]))

        return cls.data_to_csv(
            data=[
                ChannelInfo.filter_fields(channel_info, info_columns)
                for channel_info in youtube.channels_infos(channel_ids)
            ],
            output_file_path=output_file_path,
        )
