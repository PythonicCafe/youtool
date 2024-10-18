.. youtool documentation master file, created by
   sphinx-quickstart on Mon Jul  8 14:31:22 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to youtool documentation!
=================================

Easily access YouTube Data API v3 in batches
--------------------------------------------

.. toctree::
   :maxdepth: 2

   contributing

--------------------------------------------

Python library and command-line interface to crawl YouTube Data API v3 in batch operations and other related tasks.
Easier to use than alternatives - you don't need to spend time learning the YouTube API and its caveats. 
With this library you can get:

- Channel ID from channel URL (scraping) or username (API)
- Channel information (title, subscribers etc.)
- List of playlists for a channel
- List of videos for a playlist
- Video information (title, description, likes, comments etc.)
- Comments
- Livechat, including superchat (scraping using chat-downloader)
- Automatic transcription (scraping using yt-dlp)

The library will automatically:

- Try as many keys as you provide
- Use batch of 50 items in supported API endpoints
- Paginate when needed

Installation
------------

Install project by running

.. code-block:: python

   pip install youtool

Using as a library
------------------
Just follow the tutorial/examples below and check the ``help()`` for ``YouTube`` methods.

`GitHub Repository <https://github.com/PythonicCafe/youtool?tab=readme-ov-file#using-as-a-library:~:text=Using%20as%20a-,library,-Just%20follow%20the>`_

1. Initializing the YouTube API:

.. code-block:: python

   from youtool import YouTube

   api_keys = ["key1", "key2", ...]
   yt = YouTube(api_keys, disable_ipv6=True)

Here, we are creating an instance of the YouTube class using a list of YouTube API keys. 
The disable_ipv6=True option is passed to disable IPv6 usage.

2. Extracting Channel IDs by url:

.. code-block:: python

   channel_id_1 = yt.channel_id_from_url("https://youtube.com/c/PythonicCafe/")
   print(f"Pythonic Café's channel ID (got from URL): {channel_id_1}")

3. Extracting Channel IDs by username:

.. code-block:: python

   channel_id_2 = yt.channel_id_from_username("turicas")
   print(f"Turicas' channel ID (got from username): {channel_id_2}")

4. Listing Playlists from a Channel:

.. code-block:: python

   for playlist in yt.channel_playlists(channel_id_2):
      for video in yt.playlist_videos(playlist["id"]):
         print(f"  Video: {video}")

Here, we iterate through playlists of a specific channel (channel_id_2) and list the videos in each playlist.

5. Searching for Videos:

.. code-block:: python

   for index, video in enumerate(yt.video_search(term="Álvaro Justen")):
      print(f"  Video: {video}")
      if index == 4:
         break

This snippet searches for videos related to a specific term using the video_search method of the yt instance.

6. Fetching Detailed Video Information:

.. code-block:: python

   last_video = list(yt.videos_infos([video["id"]]))[0]
   pprint(last_video)

Here, we fetch detailed information about a specific video using the videos_infos method of the yt instance.

7. Fetching Channel Information:

.. code-block:: python

   for channel in yt.channels_infos([channel_id_1, channel_id_2]):
      print(channel)

This snippet fetches detailed information about multiple channels using the channels_infos method of the yt instance.

8. Fetching Video Comments and Live Chat:

.. code-block:: python

   for comment in yt.video_comments(video_id):
      print(comment)
   for chat_message in yt.video_livechat(live_video_id):
      print(chat_message)

Here, we fetch comments and live chat messages from specific videos using the video_comments and video_livechat methods of the yt instance.

9. Downloading Video Transcriptions:

.. code-block:: python

   yt.videos_transcriptions([video_id, live_video_id], language_code="pt", path=download_path)

This snippet downloads transcriptions for specific videos using the videos_transcriptions method of the yt instance.

How to contribute
------------------

Welcome to contributing documentation youtool project

See :doc:`contributing` for more detail.

- `Issue Tracker <https://github.com/PythonicCafe/youtool/issues>`_
- `Source Code <https://github.com/PythonicCafe/youtool/blob/develop/youtool.py>`_

Support
-------

If you are having issues, please let us know

License
-------
GNU Lesser General Public License (LGPL) version3

This project was developed in a partnership between Pythonic Café and `Novelo Data <https://www.novelo.io/>`_