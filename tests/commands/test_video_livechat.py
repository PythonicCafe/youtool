import csv
import pytest

from io import StringIO
from datetime import datetime
from unittest.mock import Mock
from youtool.commands import VideoLiveChat


CHAT_MESSAGE_COLUMNS = [
    "id",
    "video_id",
    "created_at",
    "type",
    "action",
    "video_time",
    "author",
    "author_id",
    "author_image_url",
    "text",
    "money_currency",
    "money_amount",
]

def test_video_livechat(mocker):
    """Test case for fetching live chat messages from a YouTube video.

    Mocks the YouTube API to return expected live chat messages and verifies if the execute method correctly formats and returns the data.
    """
    youtube_mock = mocker.patch("youtool.commands.video_livechat.YouTube")
    video_id = "video_id_mock"

    expected_result = [{column: "data" for column in CHAT_MESSAGE_COLUMNS}]

    csv_file = StringIO()
    csv_writer = csv.DictWriter(csv_file, fieldnames=expected_result[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(expected_result)

    videos_livechat_mock = Mock(return_value=expected_result)
    youtube_mock.return_value.video_livechat = videos_livechat_mock
    result = VideoLiveChat.execute(id=video_id)

    videos_livechat_mock.assert_called_once_with(video_id, expand_emojis=True)

    assert result == csv_file.getvalue()


def test_video_livechat_with_file_output(mocker, tmp_path):
    """Test case for fetching live chat messages from a YouTube video and saving them to a CSV file.

    Mocks the YouTube API to return expected live chat messages and verifies if the execute method correctly saves the data to a CSV file.
    """
    youtube_mock = mocker.patch("youtool.commands.video_livechat.YouTube")
    video_id = "video_id_mock"

    expected_result = [{column: "data" for column in CHAT_MESSAGE_COLUMNS}]

    csv_file = StringIO()
    csv_writer = csv.DictWriter(csv_file, fieldnames=expected_result[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(expected_result)

    timestamp = datetime.now().strftime("%f")
    output_file_name = f"output_{timestamp}.csv"
    output_file_path = tmp_path / output_file_name

    videos_livechat_mock = Mock(return_value=expected_result)
    youtube_mock.return_value.video_livechat = videos_livechat_mock

    result_file_path = VideoLiveChat.execute(id=video_id, output_file_path=output_file_path)

    with open(result_file_path, "r") as result_csv_file:
        result_csv = result_csv_file.read()

    videos_livechat_mock.assert_called_once_with(video_id, expand_emojis=True)

    assert result_csv.replace("\r", "") == csv_file.getvalue().replace("\r", "")
