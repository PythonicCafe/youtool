import csv
import os
from typing import List, Self

from .. import YouTube
from .base import Command


class VideoInfo(Command):
    """Get video info from a list of IDs or URLs (or CSV filename with URLs/IDs inside), generate CSV output (same schema for video dicts)")"""

    name = "video-info"
    ID_COLUMN_NAME: str = "video_id"
    URL_COLUMN_NAME: str = "video_url"
    INFO_COLUMNS: List[str] = [
        "id",
        "title",
        "description",
        "published_at",
        "view_count",
        "like_count",
        "comment_count",
    ]

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument(
            "--api-key", type=str, help="YouTube API Key", dest="api_key", default=os.environ.get("YOUTUBE_API_KEY")
        )
        parser.add_argument("--ids", type=str, help="Video IDs", nargs="*")
        parser.add_argument("--urls", type=str, help="Video URLs", nargs="*")
        parser.add_argument("--input-file-path", type=str, help="Input CSV file path with URLs/IDs")
        parser.add_argument("--output-file-path", type=str, help="Output CSV file path")

    @classmethod
    def execute(cls: Self, **kwargs) -> str:
        """
        Execute the video-info command to fetch YouTube video information from IDs or URLs and save them to a CSV file.

        Args:
            ids (list[str], optional): A list of YouTube video IDs. If not provided, input_file_path must be specified.
            urls (list[str], optional): A list of YouTube video URLs. If not provided, input_file_path must be specified.
            input_file_path (str, optional): Path to a CSV file containing YouTube video URLs or IDs.
            output_file_path (str, optional): Path to the output CSV file where video information will be saved.
            api_key (str): The API key to authenticate with the YouTube Data API.
            url_column_name (str, optional): The name of the column in the input_file_path CSV file that contains the URLs.
                                            Default is "video_url".
            id_column_name (str, optional): The name of the column in the input_file_path CSV file that contains the IDs.
                                            Default is "video_id".
            info_columns (str, optional): Comma-separated list of columns to include in the output CSV.
                                            Default is the class attribute INFO_COLUMNS.

        Returns:
            str: A message indicating the result of the command. If output_file_path is specified, the message will
                include the path to the generated CSV file. Otherwise, it will return the result as a string.

        Raises:
            Exception: If neither ids, urls, nor input_file_path is provided.
        """

        ids = kwargs.get("ids", [])
        urls = kwargs.get("urls", [])
        input_file_path = kwargs.get("input_file_path")
        output_file_path = kwargs.get("output_file_path")
        api_key = kwargs.get("api_key")
        if api_key is None:
            raise ValueError("You must specify either --api-key or set YOUTUBE_API_KEY for this command")

        info_columns = kwargs.get("info_columns")

        info_columns = (
            [column.strip() for column in info_columns.split(",")] if info_columns else VideoInfo.INFO_COLUMNS
        )

        if input_file_path:
            with open(input_file_path, mode="r") as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    if cls.ID_COLUMN_NAME in row:
                        ids.append(row[cls.ID_COLUMN_NAME])
                    elif cls.URL_COLUMN_NAME in row:
                        urls.append(row[cls.URL_COLUMN_NAME])

        if not ids and not urls:
            raise Exception("Either 'ids' or 'urls' must be provided for the video-info command")

        youtube = YouTube([api_key], disable_ipv6=True)

        if urls:
            ids += [cls.video_id_from_url(url) for url in urls]

        # Remove duplicated
        ids = list(set(ids))
        videos_infos = list(youtube.videos_infos([_id for _id in ids if _id]))
        return cls.data_to_csv(
            data=[VideoInfo.filter_fields(video_info, info_columns) for video_info in videos_infos],
            output_file_path=output_file_path,
        )
