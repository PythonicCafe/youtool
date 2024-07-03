import csv

from typing import List, Dict, Optional, Self

from youtool import YouTube

from .base import Command


class VideoSearch(Command):
    """Search video info from a list of IDs or URLs (or CSV filename with URLs/IDs inside), generate CSV output (simplified video dict schema or option to get full video info)
    """
    name = "video-search"
    arguments = [
        {"name": "--ids", "type": str, "help": "Video IDs", "nargs": "*"},
        {"name": "--urls", "type": str, "help": "Video URLs", "nargs": "*"},
        {"name": "--input-file-path", "type": str, "help": "Input CSV file path with URLs/IDs"},
        {"name": "--output-file-path", "type": str, "help": "Output CSV file path"},
        {"name": "--full-info", "type": bool, "help": "Option to get full video info", "default": False}
    ]

    ID_COLUMN_NAME: str = "video_id"
    URL_COLUMN_NAME: str = "video_url"
    INFO_COLUMNS: List[str] = [
        "id", "title", "published_at", "view_count"
    ]
    FULL_INFO_COLUMNS: List[str] = [
        "id", "title", "description", "published_at", "view_count", "like_count", "comment_count"
    ]

    @staticmethod
    def filter_fields(video_info: Dict, info_columns: Optional[List] = None) -> Dict:
        """Filters the fields of a dictionary containing video information based on specified columns.

        Args:
            video_info (Dict): A dictionary containing video information.
            info_columns (Optional[List], optional): A list specifying which fields to include in the filtered output. 
            If None, returns the entire video_info dictionary. Defaults to None.

        Returns:
            A dictionary containing only the fields specified in info_columns (if provided) 
            or the entire video_info dictionary if info_columns is None.
        """
        return {
            field: value for field, value in video_info.items() if field in info_columns
        } if info_columns else video_info

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

        Returns:
            A message indicating the result of the command. If output_file_path is specified, 
            the message will include the path to the generated CSV file. 
            Otherwise, it will return the result as a string.

        Raises:
            Exception: If neither ids, urls, nor input_file_path is provided.
        """
        ids = kwargs.get("ids")
        urls = kwargs.get("urls")
        input_file_path = kwargs.get("input_file_path")
        output_file_path = kwargs.get("output_file_path")
        api_key = kwargs.get("api_key")
        full_info = kwargs.get("full_info", False)

        info_columns = VideoSearch.FULL_INFO_COLUMNS if full_info else VideoSearch.INFO_COLUMNS

        if input_file_path:
            with open(input_file_path, mode='r') as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    if cls.ID_COLUMN_NAME in row and row[cls.ID_COLUMN_NAME]:
                        ids.append(row[cls.ID_COLUMN_NAME])
                    elif cls.URL_COLUMN_NAME in row and row[cls.URL_COLUMN_NAME]:
                        urls.append(row[cls.URL_COLUMN_NAME])

        if not ids and not urls:
            raise Exception("Either 'ids' or 'urls' must be provided for the video-search command")

        youtube = YouTube([api_key], disable_ipv6=True)
        
        videos_infos = []

        if ids:
            videos_infos += list(youtube.videos_infos(ids))
        if urls:
            # TODO: add get videos_infos using urls to youtool
            raise NotImplementedError("videos_infos by url not implemented yet")
                                     
        return cls.data_to_csv(
            data=[
                VideoSearch.filter_fields(
                    video_info, info_columns
                ) for video_info in videos_infos
            ],
            output_file_path=output_file_path
        )
