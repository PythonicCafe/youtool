from unittest.mock import Mock, call

from youtool.commands.channel_info import ChannelInfo


def test_filter_fields():
    """Test to verify the filtering of channel information fields.

    This test checks if the `filter_fields` method of the `ChannelInfo` class correctly
    filters out unwanted fields from the channel information dictionary based on the provided columns.
    """
    channel_info = {
        'channel_id': '123456',
        'channel_name': 'Test Channel',
        'subscribers': 1000,
        'videos': 50,
        'category': 'Tech'
    }
    
    info_columns = ['channel_id', 'channel_name', 'subscribers']
    filtered_info = ChannelInfo.filter_fields(channel_info, info_columns)
    
    expected_result = {
        'channel_id': '123456',
        'channel_name': 'Test Channel',
        'subscribers': 1000
    }
    
    assert filtered_info == expected_result, f"Expected {expected_result}, but got {filtered_info}"


def test_channel_ids_from_urls_and_usernames(mocker):
    """Test to verify fetching channel IDs from both URLs and usernames.

    This test checks if the `execute` method of the `ChannelInfo` class correctly fetches channel IDs
    from a list of URLs and usernames, and then calls the `channels_infos` method with these IDs.
    """
    urls = ["https://www.youtube.com/@Turicas/featured", "https://www.youtube.com/c/PythonicCaf%C3%A9"]
    usernames = ["Turicas", "PythonicCafe"]

    ids_from_urls_mock = "id_from_url"
    ids_from_usernames_mock = "id_from_username"
    youtube_mock = mocker.patch("youtool.commands.channel_info.YouTube")

    channel_id_from_url_mock = Mock(return_value=ids_from_urls_mock)
    channel_id_from_username_mock = Mock(return_value=ids_from_usernames_mock)
    channels_infos_mock = Mock(return_value=[])

    youtube_mock.return_value.channel_id_from_url = channel_id_from_url_mock
    youtube_mock.return_value.channel_id_from_username = channel_id_from_username_mock
    youtube_mock.return_value.channels_infos = channels_infos_mock

    ChannelInfo.execute(urls=channels_urls, usernames=usernames)

    channel_id_from_url_mock.assert_has_calls(
        [call(url) for url in channels_urls]
    )
    channel_id_from_username_mock.assert_has_calls(
        [call(username) for username in usernames]
    )
    channels_infos_mock.assert_called_once()
    assert ids_from_usernames_mock in channels_infos_mock.call_args.args[0]
    assert ids_from_urls_mock in channels_infos_mock.call_args.args[0]
