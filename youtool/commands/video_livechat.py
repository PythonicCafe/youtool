import csv
from typing import List, Dict
from .base import Command
from youtool import YouTube

class VideoLiveChat(Command):
    """Get live chat messages from a video ID, generate CSV output (same schema for chat_message dicts)"""

    name = "video-livechat"
    arguments = [
        {"name": "--id", "type": str, "help": "Video ID", "required": True},
        {"name": "--output-file-path", "type": str, "help": "Output CSV file path"}
    ]

    CHAT_MESSAGE_COLUMNS: List[str] = [
        "message_id", "author_name", "message", "published_at"
    ]

    @classmethod
    def execute(cls, **kwargs) -> str:
        """
        Execute the video-livechat command to fetch live chat messages from a YouTube video and save them to a CSV file.

        Args:
            id (str): The ID of the YouTube video.
            output_file_path (str): Path to the output CSV file where live chat messages will be saved.
            api_key (str): The API key to authenticate with the YouTube Data API.

        Returns:
            str: A message indicating the result of the command. If output_file_path is specified,
                 the message will include the path to the generated CSV file. Otherwise, it will return the result as a string.
        """
        video_id = kwargs.get("id")
        output_file_path = kwargs.get("output_file_path")
        api_key = kwargs.get("api_key")

        youtube = YouTube([api_key], disable_ipv6=True)
        
        live_chat_messages = list(youtube.video_livechat(video_id))  # Assuming you have a method for fetching live chat messages

        return cls.data_to_csv(
            data=live_chat_messages,
            output_file_path=output_file_path
        )
