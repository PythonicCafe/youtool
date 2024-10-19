from typing import List, Self

from .. import YouTube
from .base import Command


class VideoSearch(Command):
    """
    Search video info from a list of IDs or URLs (or CSV filename with URLs/IDs inside),
    generate CSV output (simplified video dict schema or option to get full video info)
    """

    name = "video-search"
    arguments = [
        {"name": "--ids", "type": str, "help": "Video IDs", "nargs": "*"},
        {"name": "--urls", "type": str, "help": "Video URLs", "nargs": "*"},
        {"name": "--input-file-path", "type": str, "help": "Input CSV file path with URLs/IDs"},
        {"name": "--output-file-path", "type": str, "help": "Output CSV file path"},
        {"name": "--full-info", "type": bool, "help": "Option to get full video info", "default": False},
        {"name": "--url-column-name", "type": str, "help": "URL column name on csv input files"},
        {"name": "--id-column-name", "type": str, "help": "Channel ID column name on csv output files"},
    ]

    ID_COLUMN_NAME: str = "video_id"
    URL_COLUMN_NAME: str = "video_url"
    INFO_COLUMNS: List[str] = ["id", "title", "published_at", "view_count"]
    FULL_INFO_COLUMNS: List[str] = [
        "id",
        "title",
        "description",
        "published_at",
        "view_count",
        "like_count",
        "comment_count",
    ]

    @classmethod
    def execute(cls: Self, **kwargs) -> str:
        """
        Execute the video-search command to fetch YouTube video information from IDs or URLs and save them to a CSV file.

        Args:
            ids (list[str], optional): A list of YouTube video IDs. If not provided, input_file_path must be specified.
            urls (list[str], optional): A list of YouTube video URLs. If not provided, input_file_path must be specified.
            input_file_path (str, optional): Path to a CSV file containing YouTube video URLs or IDs.
            output_file_path (str, optional): Path to the output CSV file where video information will be saved.
            api_key (str): The API key to authenticate with the YouTube Data API.
            full_info (bool, optional): Flag to indicate whether to get full video info. Default is False.
            url_column_name (str, optional): The name of the column in the input CSV file that contains the URLs. Default is "video_url".
            id_column_name (str, optional): The name of the column in the input CSV file that contains the IDs. Default is "video_id".

        Returns:
            str: A message indicating the result of the command. If output_file_path is specified,
            the message will include the path to the generated CSV file.
            Otherwise, it will return the result as a string.

        Raises:
            Exception: If neither ids, urls, nor input_file_path is provided.
        """
        ids = kwargs.get("ids", [])
        urls = kwargs.get("urls", [])
        output_file_path = kwargs.get("output_file_path")
        api_key = kwargs.get("api_key")
        full_info = kwargs.get("full_info", False)

        url_column_name = kwargs.get("url_column_name", cls.URL_COLUMN_NAME)
        id_column_name = kwargs.get("id_column_name", cls.ID_COLUMN_NAME)

        info_columns = VideoSearch.FULL_INFO_COLUMNS if full_info else VideoSearch.INFO_COLUMNS

        if input_file_path := kwargs.get("input_file_path"):
            if urls_from_csv := cls.data_from_csv(input_file_path, url_column_name):
                ids += [cls.video_id_from_url(url) for url in urls_from_csv]
            if ids_from_csv := cls.data_from_csv(input_file_path, id_column_name):
                ids += ids_from_csv

        if not ids and not urls:
            raise Exception("Either 'ids' or 'urls' must be provided for the video-search command")

        youtube = YouTube([api_key], disable_ipv6=True)

        if urls:
            ids += [cls.video_id_from_url(url) for url in urls]

        # Remove duplicated
        ids = list(set(ids))
        videos_infos = list(youtube.videos_infos([_id for _id in ids if _id]))

        return cls.data_to_csv(
            data=[VideoSearch.filter_fields(video_info, info_columns) for video_info in videos_infos],
            output_file_path=output_file_path,
        )
