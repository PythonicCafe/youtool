# youtool - Easily access YouTube Data API v3 in batches

Python library (and future command-line interface) to crawl YouTube Data API v3 in batch operations and other related
tasks. Easier to use than alternatives - you don't need to spend time learning the YouTube API and its caveats. With
this library you can get:

- Channel ID from channel URL (scraping) or username (API)
- Channel information (title, subscribers etc.)
- List of playlists for a channel
- List of videos for a playlist
- Video search (many parameters)
- Video information (title, description, likes, comments etc.)
- Comments
- Livechat, including superchat (scraping using
  [chat-downloader](https://chat-downloader.readthedocs.io/en/latest/))
- Automatic transcription (scraping using [yt-dlp](https://github.com/yt-dlp/yt-dlp))

The library will automatically:

- Try as many keys as you provide
- Use batch of 50 items in supported API endpoints
- Paginate when needed


## Installing


```shell
pip install youtool
```

You may also want some extras:

```shell
pip install youtool[livechat]
pip install youtool[transcription]
```

## Using as a libray


Just follow the tutorial/examples below and check the `help()` for `YouTube` methods.

```python
from pprint import pprint
from pathlib import Path

from youtool import YouTube

api_keys = ["key1", "key2", ...]  # Create one in Google Cloud Console
yt = YouTube(api_keys, disable_ipv6=True)  # Will try all keys

channel_id = yt.channel_id_from_url("https://youtube.com/c/PythonicCafe/")
print(f"Pythonic Café's channel ID: {channel_id}")

print("Playlists found:")
for playlist in yt.channel_playlists(channel_id):
    # `playlist` is a `dict`
    print(f"Playlist: {playlist}")
    for video in yt.playlist_videos(playlist["id"]):
        # `video` is a `dict`, but this endpoint doesn't provide full video information (use `videos_infos` to get them)
        print(f"  Video: {video}")
    print("-" * 80)

print("Videos found:")
for video in yt.video_search(channel_id=channel_id):  # Will paginate automcatically
    # `video` is a `dict`, but this endpoint doesn't provide full video information (use `videos_infos` to get them)
    print(f"Video: {video}")
# `video_search` has many other parameters also!

# The method below can be used to get information in batches (50 videos per request) - you can pass a list of video IDs
# (more than 50) and it'll get data in batches from the API.
last_video = list(yt.videos_infos([video["id"]]))[0]
print("Complete information for last video:")
pprint(last_video)

print("Categories in Brazilian YouTube:")
for category in yt.categories(region_code="BR"):
    # `category` is a `dict`
    print(category)

print("Current most popular videos in Brazil:")
for video in yt.most_popular(region_code="BR"):  # Will paginate automatically
    # `video` is a `dict`, but this endpoint doesn't provide full video information (use `videos_infos` to get them)
    print(f"{video['id']} {video['title']}")

print("Channel information (2 channels in one request):")
channel_id_2 = yt.channel_id_from_username("turicas")
for channel in yt.channels_infos([channel_id, channel_id_2]):
    # `channel` is a `dict`
    print(channel)

video_id = "b1FjmUzgFB0"
print(f"Comments for video {video_id}:")
for comment in yt.video_comments(video_id):
    # `comment` is a `dict`
    print(comment)

live_video_id = "yyzIPQsa98A"
print(f"Live chat for video {live_video_id}:")
for chat_message in yt.video_livechat(live_video_id):
    # `chat_message` is a `dict`
    print(chat_message)  # It has the superchat information (`money_currency` and `money_amount` keys)

download_path = Path("transcriptions")
if not download_path.exists():
    download_path.mkdir(parents=True)
print(f"Downloading Portuguese (pt) transcriptions for videos {video_id} and {live_video_id} - saving at {download_path.absolute()}")
yt.videos_transcriptions([video_id, live_video_id], language_code="pt", path=download_path)
for vid in [video_id, live_video_id]:
    result = list(download_path.glob(f"{vid}*vtt"))
    if not result:
        print(f"  Transcription for video {vid} could not be downloaded.")
    else:
        filename = result[0]
        print(f"  Downloaded: {filename} ({filename.stat().st_size / 1024:.1f} KiB)")
```

## Tests

To run all tests, execute:

```shell
make test
```

## Future improvments

Pull requests are welcome! :)

- Command-line interface with the following subcommands:
  - channel-id: get channel IDs from a list of URLs (or CSV filename with URLs inside), generate CSV output (just the
    IDs)
  - channel-info: get channel info from a list of IDs (or CSV filename with IDs inside), generate CSV output (same
    schema for `channel` dicts)
  - video-info: get video info from a list of IDs or URLs (or CSV filename with URLs/IDs inside), generate CSV output
    (same schema for `video` dicts)
  - video-search: get video info from a list of IDs or URLs (or CSV filename with URLs/IDs inside), generate CSV output
    (simplified `video` dict schema or option to get full video info after)
  - video-comments: get comments from a video ID, generate CSV output (same schema for `comment` dicts)
  - video-livechat: get comments from a video ID, generate CSV output (same schema for `chat_message` dicts)
  - video-transcriptions: download video transcriptions based on language code, path and list of video IDs or URLs (or
    CSV filename with URLs/IDs inside), download files to destination and report results
- Replace `dict`s with dataclasses
- Create a website with docs/reference


## License

GNU Lesser General Public License (LGPL) version3.

This project was developed in a partnership between [Pythonic Café](https://pythonic.cafe/) and [Novelo
Data](https://novelo.io/).
