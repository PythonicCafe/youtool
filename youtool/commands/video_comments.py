import os
from typing import List, Self
from pathlib import Path

from .. import YouTube
from .base import Command


class VideoComments(Command):
    """Get comments from a video ID, generate CSV output (same schema for comment dicts)"""

    name = "video-comments"
    COMMENT_COLUMNS: List[str] = ["comment_id", "author_display_name", "text_display", "like_count", "published_at"]

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument(
            "--api-key", type=str, help="YouTube API Key", dest="api_key", default=os.environ.get("YOUTUBE_API_KEY")
        )
        parser.add_argument("--id", type=str, help="Video ID", required=True)
        parser.add_argument("--output-filename", "-o", type=Path, help="Output CSV file path")

    @classmethod
    def execute(cls: Self, **kwargs) -> str:
        """
        Execute the get-comments command to fetch comments from a YouTube video and save them to a CSV file.

        Args:
            id (str): The ID of the YouTube video.
            output_filename: Path to the output CSV file where comments will be saved.
            api_key (str): The API key to authenticate with the YouTube Data API.

        Returns:
            A message indicating the result of the command. If output_filename is specified,
            the message will include the path to the generated CSV file.
            Otherwise, it will return the result as a string.
        """
        video_id = kwargs.get("id")
        output_filename = kwargs.get("output_filename")
        api_key = kwargs.get("api_key")
        if api_key is None:
            raise ValueError("You must specify either --api-key or set YOUTUBE_API_KEY for this command")

        youtube = YouTube([api_key], disable_ipv6=True)
        comments = list(youtube.video_comments(video_id))
        return cls.data_to_csv(data=comments, output_filename=output_filename)
