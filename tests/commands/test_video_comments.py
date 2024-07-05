import csv
import pytest

from io import StringIO
from datetime import datetime
from unittest.mock import Mock
from youtool.commands import VideoComments


def test_video_comments(mocker):
    youtube_mock = mocker.patch("youtool.commands.video_comments.YouTube")
    video_id = "video_id_mock"
    
    expected_result = [
        {"text": "my_comment", "author": "my_name"}
    ]

    csv_file = StringIO()
    csv_writer = csv.DictWriter(csv_file, fieldnames=expected_result[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(expected_result)

    videos_comments_mock = Mock(return_value=expected_result)
    youtube_mock.return_value.video_comments = videos_comments_mock
    result = VideoComments.execute(id=video_id)

    videos_comments_mock.assert_called_once_with(video_id)

    assert result == csv_file.getvalue()


def test_video_comments_with_file_output(mocker, tmp_path):
    youtube_mock = mocker.patch("youtool.commands.video_comments.YouTube")
    video_id = "video_id_mock"
    
    expected_result = [
        {"text": "my_comment", "author": "my_name"}
    ]

    csv_file = StringIO()
    csv_writer = csv.DictWriter(csv_file, fieldnames=expected_result[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(expected_result)

    timestamp = datetime.now().strftime("%f")
    output_file_name = f"output_{timestamp}.csv"
    output_file_path = tmp_path / output_file_name

    videos_comments_mock = Mock(return_value=expected_result)
    youtube_mock.return_value.video_comments = videos_comments_mock

    result_file_path = VideoComments.execute(id=video_id, output_file_path=output_file_path)

    with open(result_file_path, "r") as result_csv_file:
        result_csv = result_csv_file.read()

    videos_comments_mock.assert_called_once_with(video_id)

    assert result_csv.replace("\r", "") == csv_file.getvalue().replace("\r", "")
