import csv
from datetime import datetime
from io import StringIO
from unittest.mock import Mock

import pytest

from youtool.commands.video_search import VideoSearch


def test_video_search_string_output(mocker, videos_ids, videos_urls):
    """Test the execution of the video-search command and verify the output as string.

    This test simulates the execution of the `VideoSearch.execute` command with a list of video IDs and URLs,
    and checks if the output is correctly formatted as a CSV string.
    """
    youtube_mock = mocker.patch("youtool.commands.video_search.YouTube")
    expected_videos_infos = [
        {column: f"v_{index}" for column in VideoSearch.INFO_COLUMNS} for index, _ in enumerate(videos_ids)
    ]

    csv_file = StringIO()
    csv_writer = csv.DictWriter(csv_file, fieldnames=VideoSearch.INFO_COLUMNS)
    csv_writer.writeheader()
    csv_writer.writerows(expected_videos_infos)

    videos_infos_mock = Mock(return_value=expected_videos_infos)
    youtube_mock.return_value.videos_infos = videos_infos_mock

    result = VideoSearch.execute(ids=videos_ids, urls=videos_urls, api_key="test")

    videos_infos_mock.assert_called_once_with(list(set(videos_ids)))
    assert result == csv_file.getvalue()


def test_video_search_file_output(mocker, videos_ids, videos_urls, tmp_path):
    """Test the execution of the video-search command and verify the output to a file.

    This test simulates the execution of the `VideoSearch.execute` command with a list of video IDs and URLs,
    and checks if the output is correctly written to a CSV file.
    """
    youtube_mock = mocker.patch("youtool.commands.video_search.YouTube")
    expected_videos_infos = [
        {column: f"v_{index}" for column in VideoSearch.INFO_COLUMNS} for index, _ in enumerate(videos_ids)
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
        ids=videos_ids, urls=videos_urls, output_file_path=output_file_path, api_key="test"
    )

    with open(result_file_path, "r") as result_csv_file:
        result_csv = result_csv_file.read()

    videos_infos_mock.assert_called_once_with(list(set(videos_ids)))
    assert result_csv.replace("\r", "") == expected_csv_file.getvalue().replace("\r", "")


def test_video_search_no_id_and_url_error():
    """Test if the video-search command raises an exception when neither IDs nor URLs are provided.

    This test checks if executing the `VideoSearch.execute` command without providing IDs or URLs
    raises the expected exception.

    Assertions:
        - Assert that the raised exception matches the expected error message.
    """
    with pytest.raises(Exception, match="Either 'ids' or 'urls' must be provided"):
        VideoSearch.execute(ids=None, urls=None, api_key="test")
