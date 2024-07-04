import csv
import pytest

from unittest.mock import Mock
from pathlib import Path
from youtool.commands import VideoInfo


@pytest.fixture
def youtube_mock(mocker, mock_video_info):
    mock = mocker.patch("youtool.commands.video_info.YouTube")
    mock_instance = mock.return_value
    mock_instance.videos_infos = Mock(return_value=mock_video_info)
    return mock_instance

@pytest.fixture
def mock_video_info():
    return [
        {"id": "tmrhPou85HQ", "title": "Title 1", "description": "Description 1", "published_at": "2021-01-01", "view_count": 100, "like_count": 10, "comment_count": 5},
        {"id": "qoI_x9fylaw", "title": "Title 2", "description": "Description 2", "published_at": "2021-02-01", "view_count": 200, "like_count": 20, "comment_count": 10} 
    ]

def test_execute_with_ids_and_urls(youtube_mock, mocker, tmp_path, mock_video_info):
    ids = ["tmrhPou85HQ", "qoI_x9fylaw"]
    urls = ["https://www.youtube.com/watch?v=tmrhPou85HQ&ab_channel=Turicas", "https://www.youtube.com/watch?v=qoI_x9fylaw&ab_channel=PythonicCaf%C3%A9"]
    output_file_path = tmp_path / "output.csv"

    VideoInfo.execute(ids=ids, urls=urls, output_file_path=str(output_file_path), api_key="test_api_key")

    assert Path(output_file_path).is_file()
    with open(output_file_path, 'r') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)

    assert csv_data[0]["id"] == "tmrhPou85HQ"
    assert csv_data[1]["id"] == "qoI_x9fylaw"

def test_execute_missing_arguments():
    with pytest.raises(Exception) as exc_info:
        VideoInfo.execute(api_key="test_api_key")
    
    assert str(exc_info.value) == "Either 'ids' or 'urls' must be provided for the video-info command"

def test_execute_with_input_file_path(youtube_mock, mocker, tmp_path, mock_video_info):
    input_csv_content = """video_id,video_url
    tmrhPou85HQ,https://www.youtube.com/watch?v=tmrhPou85HQ&ab_channel=Turicas
    qoI_x9fylaw,https://www.youtube.com/watch?v=qoI_x9fylaw&ab_channel=PythonicCaf%C3%A9
    """
    input_file_path = tmp_path / "input.csv"
    output_file_path = tmp_path / "output.csv"

    with open(input_file_path, 'w') as f:
        f.write(input_csv_content)

    VideoInfo.execute(input_file_path=str(input_file_path), output_file_path=str(output_file_path), api_key="test_api_key")

    assert Path(output_file_path).is_file()
    with open(output_file_path, 'r') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)
      
    assert csv_data[0]["id"] == "tmrhPou85HQ"
    assert csv_data[1]["id"] == "qoI_x9fylaw"


def test_execute_with_info_columns(youtube_mock, mocker, tmp_path, mock_video_info):
    ids = ["tmrhPou85HQ", "qoI_x9fylaw"]
    output_file_path = tmp_path / "output.csv"

    VideoInfo.execute(ids=ids, output_file_path=str(output_file_path), api_key="test_api_key", info_columns="id,title")

    assert Path(output_file_path).is_file()
    with open(output_file_path, 'r') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)

    assert csv_data[0]["id"] == "tmrhPou85HQ"
    assert csv_data[0]["title"] == "Title 1"
    assert csv_data[1]["id"] == "qoI_x9fylaw"
    assert csv_data[1]["title"] == "Title 2"
