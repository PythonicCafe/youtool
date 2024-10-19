from typing import Self

from .. import YouTube
from .base import Command


class VideoLiveChat(Command):
    """Get live chat comments from a video ID, generate CSV output (same schema for chat_message dicts)"""

    name = "video-livechat"

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("--id", type=str, help="Video ID", required=True)
        parser.add_argument("--output-file-path", type=str, help="Output CSV file path")
        parser.add_argument("--expand-emojis", type=bool, help="Expand emojis in chat messages", default=True)

    @classmethod
    def execute(cls: Self, **kwargs) -> str:
        """
        Execute the video-livechat command to fetch live chat messages from a YouTube video and save them to a CSV file.

        Args:
            id (str): The ID of the YouTube video.
            output_file_path (str): Path to the output CSV file where chat messages will be saved.
            expand_emojis (bool): Whether to expand emojis in chat messages. Defaults to True.

        Returns:
            A message indicating the result of the command. If output_file_path is specified,
            the message will include the path to the generated CSV file.
            Otherwise, it will return the result as a string.
        """
        video_id = kwargs.get("id")
        output_file_path = kwargs.get("output_file_path")
        expand_emojis = kwargs.get("expand_emojis", True)

        yt = YouTube([None], disable_ipv6=True)
        chat_messages = yt.video_livechat(video_id, expand_emojis=expand_emojis)
        return cls.data_to_csv(list(chat_messages), output_file_path)
