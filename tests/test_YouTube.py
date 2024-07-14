import datetime
import os
import shutil
import tempfile
from decimal import Decimal
from itertools import islice
from pathlib import Path

import pytest

from youtool import YouTube


def assert_types(row_type, expected_types, rows):
    for row in rows:
        all_keys = list(row.keys())
        for type_, keys in expected_types.items():
            for key in keys:
                assert key in row, f"Key {repr(key)} not found in row ({row_type}) {row}"
                value = row[key]
                assert type(value) in (
                    type(None),
                    type_,
                ), f"Key {repr(key)} has not the expected type ({type(value)}, expected {type_})"
                all_keys.remove(key)
        assert not all_keys, f"Row has remaining keys: {', '.join(repr(key) for key in all_keys)}"


@pytest.fixture()
def tmpdir():
    global TMP_FILE_PATH

    TMP_FILE_PATH = Path(tempfile.mkdtemp(prefix="youtool-tests-"))
    yield
    shutil.rmtree(str(TMP_FILE_PATH))
    TMP_FILE_PATH = None


api_keys = ["non-working-key"] + os.environ["YOUTUBE_API_KEY"].split(",")
channel_url = "https://youtube.com/c/PythonicCafe"
username = "turicas"
live_video_id = "yyzIPQsa98A"
vtt_videos_ids = ["Uo8Ct54wf-M", "mWQfIrD_qbg", "xDA64oA0DMs"]
expected_channel_id_1 = "UC9rtYzWLlYRfbYjDUDsVmUg"
expected_channel_id_2 = "UC6ewEyR2ZNTS7_oOeyQSXsQ"
expected_br_category = {
    "id": 28,
    "title": "Science & Technology",
    "assignable": True,
    "channel_id": "UCBR8-60-B28hp2BmDPdntcQ",
}
expected_channel_types = {
    str: "id title description custom_username thumbnail_url playlist_id".split(),
    int: "views subscribers videos".split(),
    datetime.datetime: ["published_at"],
}
expected_playlist_types = {
    str: "id title description channel_id channel_title thumbnail_url".split(),
    datetime.datetime: ["published_at"],
    int: ["videos"],
}
expected_video_types = {
    str: "id definition status channel_id channel_title title description playlist_channel_id playlist_channel_title".split(),
    int: "views likes dislikes favorites comments concurrent_viewers".split(),
    float: ["duration"],
    datetime.datetime: "scheduled_to started_at finished_at published_at added_to_playlist_at".split(),
    list: ["tags"],
}
expected_live_comment_types = {
    str: "id video_id type action author author_id author_image_url text money_currency".split(),
    datetime.datetime: ["created_at"],
    Decimal: ["money_amount"],
    float: ["video_time"],
}
expected_comment_types = {
    str: "id video_id text author author_profile_image_url author_channel_id parent_id".split(),
    int: "likes replies".split(),
    datetime.datetime: ["published_at", "updated_at"],
}
yt = YouTube(api_keys=api_keys, disable_ipv6=True)


def test_YouTube_channel_id_from_url():
    channel_id_1 = yt.channel_id_from_url(channel_url)
    assert channel_id_1 == expected_channel_id_1, "Cannot scrape channel ID"


def test_YouTube_channel_id_from_username():
    channel_id_2 = yt.channel_id_from_username(username)
    assert channel_id_2 == expected_channel_id_2, "Cannot get channel ID via API"


def test_YouTube_request():
    # Check if the first tried key was discarded
    assert yt._YouTube__current_key == api_keys[1], "First API key was not discarded"


def test_YouTube_categories():
    assert expected_br_category in yt.categories("BR"), "Science & Technology category not found in BR"


def test_YouTube_most_popular():
    most_popular_videos = list(islice(yt.most_popular(region_code="BR"), 10))
    assert_types("video from most popular", expected_video_types, most_popular_videos)


@pytest.mark.dependency()
def test_YouTube_channels_infos():
    global channels_infos_data

    channels_infos_data = list(yt.channels_infos([expected_channel_id_1, expected_channel_id_2]))
    assert len(channels_infos_data) == 2, "Number of returned channels differs"
    assert_types("channel", expected_channel_types, channels_infos_data)
    assert channels_infos_data[0]["id"] == expected_channel_id_1
    assert channels_infos_data[1]["id"] == expected_channel_id_2


@pytest.mark.dependency(depends=["test_YouTube_channels_infos"])
def test_YouTube_channel_playlists():
    global channel_playlists_data, number_of_playlists

    channel_playlists_data = list(yt.channel_playlists(expected_channel_id_2))
    channel_playlists_data.sort(key=lambda row: row["published_at"])
    number_of_playlists = len(channel_playlists_data)
    assert number_of_playlists >= 20
    assert_types("playlist", expected_playlist_types, channel_playlists_data)
    assert all(
        expected_channel_id_2 == playlist["channel_id"] for playlist in channel_playlists_data
    ), "Unknown channel in playlists result"
    assert all(channels_infos_data[1]["title"] == playlist["channel_title"] for playlist in channel_playlists_data)


@pytest.mark.dependency(depends=["test_YouTube_channel_playlists"])
def test_YouTube_paginate():
    # Force a maxResults little than the number of results to check if pagination works properly
    old_max_results = yt._YouTube__params["maxResults"]
    yt._YouTube__params["maxResults"] = int(number_of_playlists / 2)
    channel_playlists_data_2 = list(yt.channel_playlists(expected_channel_id_2))
    assert len(channel_playlists_data_2) == number_of_playlists
    yt._YouTube__params["maxResults"] = old_max_results


@pytest.mark.dependency(depends=["test_YouTube_channel_playlists"])
def test_YouTube_playlist_videos():
    global playlist_videos_data

    playlist_id = channel_playlists_data[0]["id"]
    playlist_videos_data = list(yt.playlist_videos(playlist_id))
    assert_types("video from playlist", expected_video_types, playlist_videos_data)


@pytest.mark.dependency(depends=["test_YouTube_playlist_videos"])
def test_YouTube_videos_infos():
    global videos_infos_data

    videos_ids = [video["id"] for video in playlist_videos_data]
    videos_infos_data = list(yt.videos_infos(videos_ids))
    assert_types("video", expected_video_types, videos_infos_data)

    # Check only the main keys since stats could change between requests and playlist-related data won't be the same
    include_keys = "id channel_id channel_title title description published_at".split()
    videos_1 = {
        video["id"]: {key: value for key, value in video.items() if key in include_keys}
        for video in playlist_videos_data
    }
    # Remove videos that were deleted on the playlist -- they won't be in `videos_2`
    for video_id, video in list(videos_1.items()):
        if video["channel_id"] is None:
            del videos_1[video_id]
    videos_2 = {
        video["id"]: {key: value for key, value in video.items() if key in include_keys} for video in videos_infos_data
    }
    assert videos_1 == videos_2


def test_YouTube_video_comments():
    video_comments_data = list(yt.video_comments(live_video_id))
    assert len(video_comments_data) >= 20, "Wrong number of comments"
    assert_types("comment", expected_comment_types, video_comments_data)
    comments_with_replies = sum(1 for comment in video_comments_data if comment["replies"])
    assert comments_with_replies >= 2, "Comments with replies not found"
    unique_parent_ids = set(comment["parent_id"] for comment in video_comments_data if comment["parent_id"])
    assert len(unique_parent_ids) == comments_with_replies, "Parent comments do not match replies count"


def test_YouTube_video_livechat():
    video_livechat_data = list(yt.video_livechat(live_video_id))
    assert_types("live_comment", expected_live_comment_types, video_livechat_data)
    assert len(video_livechat_data) > 500
    assert sum(video["money_amount"] for video in video_livechat_data if video["money_currency"] == "BRL") == Decimal(
        "70.9"
    )


@pytest.mark.usefixtures("tmpdir")
def test_YouTube_download_transcriptions():
    lang = "pt"
    filenames = [TMP_FILE_PATH / f"{video_id}.{lang}.vtt" for video_id in vtt_videos_ids]
    # Make sure files do not exist before downloading
    for filename in filenames:
        if filename.exists():
            filename.unlink()

    for status in yt.download_transcriptions(vtt_videos_ids, lang, TMP_FILE_PATH):
        assert status[
            "filename"
        ].exists(), f"Cannot download transcriptions for {status['video_id']} (status: {status['status']})"


def test_YouTube_video_search():
    video_search_data = list(
        yt.video_search(
            term="Arduino",
            region_code=None,
            language_code=None,
            since=None,
            until=None,
            order="date",
            channel_id=expected_channel_id_2,
            channel_type=None,
            event_type=None,
            topic=None,
            video_type=None,
            location=None,
            location_radius=None,
            safe_search=None,
            video_caption=None,
            video_definition=None,
            video_dimension=None,
            video_embeddable=None,
            video_paid_product_placement=None,
            video_syndicated=None,
            video_license=None,
            video_category_id=None,
        )
    )
    assert len(video_search_data) > 5
    assert_types("video from search", expected_video_types, video_search_data)
