import pytest


@pytest.fixture
def channels_urls():
    return ["https://www.youtube.com/@Turicas/featured", "https://www.youtube.com/c/PythonicCaf%C3%A9"]


@pytest.fixture
def videos_ids():
    return ["video_id_1", "video_id_2"]


@pytest.fixture
def videos_urls(videos_ids):
    return [f"https://www.youtube.com/?v={video_id}" for video_id in videos_ids]


@pytest.fixture
def usernames():
    return ["Turicas", "PythonicCafe"]
