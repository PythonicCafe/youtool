from pathlib import Path

from .. import YouTube
from .base import Command


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
        {"name": "--url-column-name", "type": str, "help": "URL column name on csv input files"},
        {"name": "--id-column-name", "type": str, "help": "Channel ID column name on csv output files"},
    ]

    ID_COLUMN_NAME: str = "video_id"
    URL_COLUMN_NAME: str = "video_url"

    @classmethod
    def execute(cls, **kwargs) -> str:
        """Execute the video-transcription command to download transcriptions of videos based on IDs or URLs and save them to files.

        Args:
            ids (List[str]): A list of YouTube video IDs.
            urls (List[str]): A list of YouTube video URLs.
            input_file_path (str): Path to a CSV file containing YouTube video IDs or URLs.
            output_dir (str): Directory path to save the transcription files.
            language_code (str): Language code for the transcription language.
            api_key (str): The API key to authenticate with the YouTube Data API.
            url_column_name (str, optional): Column name for URLs in the CSV input file. Defaults to "video_url".
            id_column_name (str, optional): Column name for IDs in the CSV output file. Defaults to "video_id".

        Returns:
            str: A message indicating the result of the command. Reports success or failure for each video transcription download.
        """
        ids = kwargs.get("ids") or []
        urls = kwargs.get("urls") or []
        input_file_path = kwargs.get("input_file_path")
        output_dir = kwargs.get("output_dir")
        language_code = kwargs.get("language_code")
        api_key = kwargs.get("api_key")

        url_column_name = kwargs.get("url_column_name", cls.URL_COLUMN_NAME)
        id_column_name = kwargs.get("id_column_name", cls.ID_COLUMN_NAME)

        youtube = YouTube([api_key], disable_ipv6=True)

        if input_file_path := kwargs.get("input_file_path"):
            if urls_from_csv := cls.data_from_csv(input_file_path, url_column_name, False):
                ids += [cls.video_id_from_url(url) for url in urls_from_csv]
            if ids_from_csv := cls.data_from_csv(input_file_path, id_column_name, False):
                ids += ids_from_csv

        if not ids and not urls:
            raise Exception("Either 'ids' or 'urls' must be provided for the video-transcription command")

        if urls:
            ids += [cls.video_id_from_url(url) for url in urls]

        # Remove duplicated
        ids = list(set(ids))
        youtube.videos_transcriptions(ids, language_code, output_dir)
        output_dir_path = Path(output_dir)
        saved_transcriptions = [
            str(output_dir_path / f"{v_id}.{language_code}.vtt")
            for v_id in ids
            if (output_dir_path / f"{v_id}.{language_code}.vtt").is_file()
        ]
        return "\n".join(saved_transcriptions)
