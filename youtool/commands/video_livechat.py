import csv
from typing import List, Dict, Optional, Self
from chat_downloader import ChatDownloader
from chat_downloader.errors import ChatDisabled, LoginRequired, NoChatReplay
from .base import Command
from datetime import datetime

class VideoLiveChat(Command):
    """Get live chat comments from a video ID, generate CSV output (same schema for chat_message dicts)"""
    name = "video-livechat"
    arguments = [
        {"name": "--id", "type": str, "help": "Video ID", "required": True},
        {"name": "--output-file-path", "type": str, "help": "Output CSV file path"},
        {"name": "--expand-emojis", "type": bool, "help": "Expand emojis in chat messages", "default": True}
    ]

    CHAT_COLUMNS: List[str] = [
        "id", "video_id", "created_at", "type", "action", "video_time", 
        "author", "author_id", "author_image_url", "text", 
        "money_currency", "money_amount"
    ]

    @staticmethod
    def parse_timestamp(timestamp: str) -> str:
        return datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def parse_decimal(value: Optional[str]) -> Optional[float]:
        return float(value.replace(',', '')) if value else None

    @classmethod
    def execute(cls: Self, **kwargs) -> str:
        """
        Execute the video-livechat command to fetch live chat messages from a YouTube video and save them to a CSV file.

        Args:
            id (str): The ID of the YouTube video.
            output_file_path (str): Path to the output CSV file where chat messages will be saved.
            expand_emojis (bool): Whether to expand emojis in chat messages. Defaults to True.
            api_key (str): The API key to authenticate with the YouTube Data API.

        Returns:
            A message indicating the result of the command. If output_file_path is specified, 
            the message will include the path to the generated CSV file. 
            Otherwise, it will return the result as a string.
        """
        video_id = kwargs.get("id")
        output_file_path = kwargs.get("output_file_path")
        expand_emojis = kwargs.get("expand_emojis", True)

        downloader = ChatDownloader()
        video_url = f"https://youtube.com/watch?v={video_id}"

        chat_messages = []
        try:
            live = downloader.get_chat(video_url, message_groups=["messages", "superchat"])
            for message in live:
                text = message["message"]
                if expand_emojis:
                    for emoji in message.get("emotes", []):
                        for shortcut in emoji["shortcuts"]:
                            text = text.replace(shortcut, emoji["id"])
                money = message.get("money", {}) or {}
                chat_messages.append({
                    "id": message["message_id"],
                    "video_id": video_id,
                    "created_at": cls.parse_timestamp(message["timestamp"]),
                    "type": message["message_type"],
                    "action": message["action_type"],
                    "video_time": float(message["time_in_seconds"]),
                    "author": message["author"]["name"],
                    "author_id": message["author"]["id"],
                    "author_image_url": [img for img in message["author"]["images"] if img["id"] == "source"][0]["url"],
                    "text": text,
                    "money_currency": money.get("currency"),
                    "money_amount": cls.parse_decimal(money.get("amount")),
                })
        except (LoginRequired, NoChatReplay, ChatDisabled):
            raise

        return cls.data_to_csv(chat_messages, output_file_path)
