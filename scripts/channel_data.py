# pip install youtool[livechat,transcription]
import argparse
import os
import json
import shelve
from pathlib import Path

from chat_downloader.errors import ChatDisabled, LoginRequired, NoChatReplay
from tqdm import tqdm
from youtool import YouTube


class CsvLazyDictWriter:  # Got and adapted from <https://github.com/turicas/rows>
    """Lazy CSV dict writer, so you don't need to specify field names beforehand

    This class is almost the same as `csv.DictWriter` with the following
    differences:

    - You don't need to pass `fieldnames` (it's extracted on the first
      `.writerow` call);
    - You can pass either a filename or a fobj (like `sys.stdout`);
    """

    def __init__(self, filename_or_fobj, encoding="utf-8", *args, **kwargs):
        self.writer = None
        self.filename_or_fobj = filename_or_fobj
        self.encoding = encoding
        self._fobj = None
        self.writer_args = args
        self.writer_kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def fobj(self):
        if self._fobj is None:
            if getattr(self.filename_or_fobj, "read", None) is not None:
                self._fobj = self.filename_or_fobj
            else:
                self._fobj = open(
                    self.filename_or_fobj, mode="w", encoding=self.encoding
                )

        return self._fobj

    def writerow(self, row):
        if self.writer is None:
            self.writer = csv.DictWriter(
                self.fobj,
                fieldnames=list(row.keys()),
                *self.writer_args,
                **self.writer_kwargs
            )
            self.writer.writeheader()

        self.writerow = self.writer.writerow
        return self.writerow(row)

    def __del__(self):
        self.close()

    def close(self):
        if self._fobj and not self._fobj.closed:
            self._fobj.close()


# TODO: add options to get only part of the data (not all steps)
parser = argparse.ArgumentParser()
parser.add_argument("--api-key", default=os.environ.get("YOUTUBE_API_KEY"), help="Comma-separated list of YouTube API keys to use")
parser.add_argument("username_or_channel_url", type=str)
parser.add_argument("data_path", type=Path)
parser.add_argument("language-code", default="pt-orig", help="See the list by running `yt-dlp --list-subs <video-URL>`")
args = parser.parse_args()

if not args.api_key:
    import sys

    print("ERROR: API key must be provided either by `--api-key` or `YOUTUBE_API_KEY` environment variable", file=sys.stderr)
    exit(1)
api_keys = [key.strip() for key in args.api_key.split(",") if key.strip()]


username = args.username
if username.startswith("https://"):
    channel_url = username
    username = [item for item in username.split("/") if item][-1]
else:
    channel_url = f"https://www.youtube.com/@{username}"
data_path = args.data_path
channel_csv_filename = data_path / f"{username}-channel.csv"
playlist_csv_filename = data_path / f"{username}-playlist.csv"
playlist_video_csv_filename = data_path / f"{username}-playlist-video.csv"
video_csv_filename = data_path / f"{username}-video.csv"
comment_csv_filename = data_path / f"{username}-comment.csv"
livechat_csv_filename = data_path / f"username}-livechat.csv"
language_code = args.language_code
video_transcription_path = data_path / Path(f"{username}-transcriptions")

yt = YouTube(api_keys, disable_ipv6=True)
video_transcription_path.mkdir(parents=True, exist_ok=True)
channel_writer = CsvLazyDictWriter(channel_csv_filename)
playlist_writer = CsvLazyDictWriter(playlist_csv_filename)
video_writer = CsvLazyDictWriter(video_csv_filename)
comment_writer = CsvLazyDictWriter(comment_csv_filename)
livechat_writer = CsvLazyDictWriter(livechat_csv_filename)
playlist_video_writer = CsvLazyDictWriter(playlist_video_csv_filename)

print("Retrieving channel info")
channel_id = yt.channel_id_from_url(channel_url)
channel_info = list(yt.channels_infos([channel_id]))[0]
channel_writer.writerow(channel_info)
channel_writer.close()

main_playlist = {
    "id": channel_info["playlist_id"],
    "title": "Uploads",
    "description": channel_info["description"],
    "videos": channel_info["videos"],
    "channel_id": channel_id,
    "channel_title": channel_info["title"],
    "published_at": channel_info["published_at"],
    "thumbnail_url": channel_info["thumbnail_url"],
}
playlist_writer.writerow(main_playlist)
playlist_ids = [channel_info["playlist_id"]]
for playlist in tqdm(yt.channel_playlists(channel_id), desc="Retrieving channel playlists"):
    playlist_writer.writerow(playlist)
    playlist_ids.append(playlist["id"])
playlist_writer.close()

video_ids = []
for playlist_id in tqdm(playlist_ids, desc="Retrieving playlists' videos"):
    for video in yt.playlist_videos(playlist_id):
        if video["id"] not in video_ids:
            video_ids.append(video["id"])
        row = {
            "playlist_id": playlist_id,
            "video_id": video["id"],
            "video_status": video["status"],
            "channel_id": video["channel_id"],
            "channel_title": video["channel_title"],
            "playlist_channel_id": video["playlist_channel_id"],
            "playlist_channel_title": video["playlist_channel_title"],
            "title": video["title"],
            "description": video["description"],
            "published_at": video["published_at"],
            "added_to_playlist_at": video["added_to_playlist_at"],
            "tags": video["tags"],
        }
        playlist_video_writer.writerow(row)
playlist_video_writer.close()

videos = []
for video in tqdm(yt.videos_infos(video_ids), desc="Retrieving detailed video information"):
    videos.append(video)
    video_writer.writerow(video)
video_writer.close()

for video_id in tqdm(video_ids, desc="Retrieving video comments"):
    try:
        for comment in yt.video_comments(video_id):
            comment_writer.writerow(comment)
    except RuntimeError:  # Comments disabled
        continue
comment_writer.close()

print("Retrieving transcriptions")
yt.videos_transcriptions(
    video_ids,
    language_code=language_code,
    path=video_transcription_path,
    skip_downloaded=True,
    batch_size=10,
)

# TODO: live chat code will freeze if it's not available
for video_id in tqdm(video_ids, desc="Retrieving live chat"):
    try:
        for comment in yt.video_livechat(video_id):
            livechat_writer.writerow(comment)
    except (LoginRequired, NoChatReplay, ChatDisabled):
        continue
livechat_writer.close()
