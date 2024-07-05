import csv
import pytest

from io import StringIO
from unittest.mock import Mock, call
from datetime import datetime

from youtool.commands.video_search import VideoSearch


def test_video_search_string_output(mocker, videos_ids, videos_urls):
    youtube_mock = mocker.patch("youtool.commands.video_search.YouTube")
    expected_videos_infos = [
        {
            column: f"v_{index}" for column in VideoSearch.INFO_COLUMNS
        } for index, _ in enumerate(videos_ids)
    ]

    csv_file = StringIO()
    csv_writer = csv.DictWriter(csv_file, fieldnames=VideoSearch.INFO_COLUMNS)
    csv_writer.writeheader()
    csv_writer.writerows(expected_videos_infos)

    videos_infos_mock = Mock(return_value=expected_videos_infos)
    youtube_mock.return_value.videos_infos = videos_infos_mock

    result = VideoSearch.execute(ids=videos_ids, urls=videos_urls)

    videos_infos_mock.assert_called_once_with(list(set(videos_ids)))
    assert result == csv_file.getvalue()


def test_video_search_file_output(mocker, videos_ids, videos_urls, tmp_path):
    youtube_mock = mocker.patch("youtool.commands.video_search.YouTube")
    expected_videos_infos = [
        {
            column: f"v_{index}" for column in VideoSearch.INFO_COLUMNS
        } for index, _ in enumerate(videos_ids)
    ]

    expected_csv_file = StringIO()
    csv_writer = csv.DictWriter(expected_csv_file, fieldnames=VideoSearch.INFO_COLUMNS)
    csv_writer.writeheader()
    csv_writer.writerows(expected_videos_infos)

    timestamp = datetime.now().strftime("%f")
    output_file_name = f"output_{timestamp}.csv"
    output_file_path = tmp_path / output_file_name

    videos_infos_mock = Mock(return_value=expected_videos_infos)
    youtube_mock.return_value.videos_infos = videos_infos_mock

    result_file_path = VideoSearch.execute(
        ids=videos_ids, urls=videos_urls, output_file_path=output_file_path
    )

    with open(result_file_path, "r") as result_csv_file:
        result_csv = result_csv_file.read()

    videos_infos_mock.assert_called_once_with(list(set(videos_ids)))
    assert result_csv.replace("\r", "") == expected_csv_file.getvalue().replace("\r", "")


def test_video_search_no_id_and_url_error():
    with pytest.raises(Exception, match="Either 'ids' or 'urls' must be provided"):
        VideoSearch.execute(ids=None, urls=None)
