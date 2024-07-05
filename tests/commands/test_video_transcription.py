from unittest.mock import Mock

from youtool.commands import VideoTranscription


def test_video_transcription(mocker, videos_ids, videos_urls, tmp_path):
    youtube_mock = mocker.patch("youtool.commands.video_transcription.YouTube")

    language_code = "pt_br"

    videos_transcriptions_mock = Mock()
    youtube_mock.return_value.videos_transcriptions = videos_transcriptions_mock

    for video_id in videos_ids:
        open(tmp_path / f"{video_id}.{language_code}.vtt", "a").close()

    result = VideoTranscription.execute(
        ids=videos_ids, urls=videos_urls, language_code=language_code, output_dir=tmp_path
    )

    videos_transcriptions_mock.assert_called_once_with(
        list(set(videos_ids)), language_code, tmp_path
    )

    for video_id in videos_ids:
        assert str(tmp_path / f"{video_id}.{language_code}.vtt") in result


def test_video_transcription_input_from_file(mocker, videos_ids, tmp_path):
    youtube_mock = mocker.patch("youtool.commands.video_transcription.YouTube")

    language_code = "pt_br"

    videos_transcriptions_mock = Mock()
    youtube_mock.return_value.videos_transcriptions = videos_transcriptions_mock

    input_file_path = tmp_path / "input_file.csv"

    with open(input_file_path, "w") as input_csv:
        input_csv.write("video_id\n" + "\n".join(videos_ids))

    for video_id in videos_ids:
        open(tmp_path / f"{video_id}.{language_code}.vtt", "a").close()

    result = VideoTranscription.execute(
        ids=None, urls=None,
        language_code=language_code, output_dir=tmp_path,
        input_file_path=input_file_path
    )

    videos_transcriptions_mock.assert_called_once_with(
        list(set(videos_ids)), language_code, tmp_path
    )

    for video_id in videos_ids:
        assert str(tmp_path / f"{video_id}.{language_code}.vtt") in result