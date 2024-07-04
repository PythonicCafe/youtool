import csv
from pathlib import Path
from typing import List, Dict
from .base import Command
from youtool import YouTube

class VideoTranscription(Command):
    """Download video transcriptions based on language code, path, and list of video IDs or URLs (or CSV filename with URLs/IDs inside).
       Download files to destination and report results."""

    name = "video-transcription"
    arguments = [
        {"name": "--ids", "type": str, "help": "Video IDs", "nargs": "*"},
        {"name": "--urls", "type": str, "help": "Video URLs", "nargs": "*"},
        {"name": "--input-file-path", "type": str, "help": "CSV file path containing video IDs or URLs"},
        {"name": "--output-dir", "type": str, "help": "Output directory to save transcriptions"},
        {"name": "--language-code", "type": str, "help": "Language code for transcription"},
        {"name": "--api-key", "type": str, "help": "API key for YouTube Data API"},
    ]

    TRANSCRIPTION_COLUMNS: List[str] = [
        "video_id", "transcription_text"
    ]

    @classmethod
    def execute(cls, **kwargs) -> str:
        """
        Execute the video-transcription command to download transcriptions of videos based on IDs or URLs and save them to files.

        Args:
            ids: A list of YouTube video IDs.
            urls: A list of YouTube video URLs.
            input_file_path: Path to a CSV file containing YouTube video IDs or URLs.
            output_dir: Directory path to save the transcription files.
            language_code: Language code for the transcription language.
            api_key: The API key to authenticate with the YouTube Data API.

        Returns:
            A message indicating the result of the command. Reports success or failure for each video transcription download.
        """
        ids = kwargs.get("ids")
        urls = kwargs.get("urls")
        input_file_path = kwargs.get("input_file_path")
        output_dir = kwargs.get("output_dir")
        language_code = kwargs.get("language_code")
        api_key = kwargs.get("api_key")

        youtube = YouTube([api_key], disable_ipv6=True)

        if input_file_path:
            ids += cls.data_from_csv(Path(input_file_path), "video_id")

        if urls:
            ids += [cls.video_id_from_url(url) for url in urls]

        # Remove duplicated
        ids = list(set(ids))
        
        # youtube.videos_transcriptions(ids, language_code, output_dir)

        results = []
        for video_id in ids:
            try:
                transcription = youtube.video_transcription(video_id, language_code)
                output_file_path = cls.save_transcription_to_file(video_id, transcription, output_dir)
                results.append(f"Transcription saved to {output_file_path}")
            except Exception as e:
                results.append(f"Error processing video {video_id}: {str(e)}")

        return "\n".join(results)