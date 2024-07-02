import csv
import pytest

from io import StringIO

from unittest.mock import patch, call
from youtool.commands.channel_id import ChannelId

@pytest.fixture
def csv_file(tmp_path):
    csv_content = "channel_url\nhttps://www.youtube.com/@Turicas/featured\n"
    csv_file = tmp_path / "urls.csv"
    csv_file.write_text(csv_content)
    return csv_file

@pytest.fixture
def youtube_api_mock():
    with patch("youtool.commands.channel_id.YouTube") as mock:
        mock.return_value.channel_id_from_url.side_effect = lambda url: f"channel-{url}"
        yield mock

def test_channels_ids_csv_preparation(youtube_api_mock):
    urls = ["https://www.youtube.com/@Turicas/featured", "https://www.youtube.com/c/PythonicCaf%C3%A9"]
    api_key = "test_api_key"
    id_column_name = "custom_id_column"
    expected_result_data = [
        {id_column_name: "channel-https://www.youtube.com/@Turicas/featured"},
        {id_column_name: "channel-https://www.youtube.com/c/PythonicCaf%C3%A9"}
    ]
    with StringIO() as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=[id_column_name])
        writer.writeheader()
        writer.writerows(expected_result_data)
        expected_result_csv = csv_file.getvalue()

    result = ChannelId.execute(urls=urls, api_key=api_key, id_column_name=id_column_name)

    youtube_api_mock.return_value.channel_id_from_url.assert_has_calls([call(url) for url in urls], any_order=True)
    assert result == expected_result_csv


def test_resolve_urls_with_direct_urls():
    # Tests whether the function returns the directly given list of URLs.
    urls = ["https://www.youtube.com/@Turicas/featured"]
    result = ChannelId.resolve_urls(urls, None, None)
    assert result == urls

def test_resolve_urls_with_file_path(csv_file):
    result = ChannelId.resolve_urls(None, csv_file, "channel_url")
    assert result == ["https://www.youtube.com/@Turicas/featured"]

def test_resolve_urls_raises_exception():
    # Tests whether the function throws an exception when neither urls nor urls_file_path are provided.
    with pytest.raises(Exception, match="Either 'username' or 'url' must be provided for the channel-id command"):
        ChannelId.resolve_urls(None, None, None)
