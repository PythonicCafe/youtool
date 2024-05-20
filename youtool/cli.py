import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key")
    subparsers = parser.add_subparsers(required=True, dest="command")

    api_key = args.api_key or os.environ.get("YOUTUBE_API_KEY")

    cmd_channel_id = subparsers.add_parser("channel-id", help="Get channel IDs from a list of URLs (or CSV filename with URLs inside), generate CSV output (just the IDs)")
    cmd_channel_info = subparsers.add_parser("channel-info", help="Get channel info from a list of IDs (or CSV filename with IDs inside), generate CSV output (same schema for `channel` dicts)")
    cmd_video_info = subparsers.add_parser("video-info", help="Get video info from a list of IDs or URLs (or CSV filename with URLs/IDs inside), generate CSV output (same schema for `video` dicts)")
    cmd_video_search = subparsers.add_parser("video-search", help="Get video info from a list of IDs or URLs (or CSV filename with URLs/IDs inside), generate CSV output (simplified `video` dict schema or option to get full video info after)")
    cmd_video_comments = subparsers.add_parser("video-comments", help="Get comments from a video ID, generate CSV output (same schema for `comment` dicts)")
    cmd_video_livechat = subparsers.add_parser("video-livechat", help="Get comments from a video ID, generate CSV output (same schema for `chat_message` dicts)")
    cmd_video_transcriptions = subparsers.add_parser("video-transcription", help="Download video transcriptions based on language code, path and list of video IDs or URLs (or CSV filename with URLs/IDs inside), download files to destination and report results")

    args = parser.parse_args()

    if args.command == "channel-id":
        print(f"Implement: {args.command}")  # TODO: implement

    elif args.command == "channel-info":
        print(f"Implement: {args.command}")  # TODO: implement

    elif args.command == "video-info":
        print(f"Implement: {args.command}")  # TODO: implement

    elif args.command == "video-search":
        print(f"Implement: {args.command}")  # TODO: implement
        exit(1)

        # TODO: update code below based on new YouTube class API
        import rows
        from loguru import logger
        from tqdm import tqdm

        from youtool import YouTube

        parser = argparse.ArgumentParser()
        parser.add_argument("--key")
        parser.add_argument("csv_filename")
        parser.add_argument("url", nargs="+")
        args = parser.parse_args()

        key = args.key or os.environ.get("YOUTUBE_API_KEY")
        if not key:
            print("ERROR: Must provide an API key (--key or YOUTUBE_API_KEY env var)", file=sys.stderr)
            exit(1)

        if not Path(args.csv_filename).parent.exists():
            Path(args.csv_filename).parent.mkdir(parents=True)
        writer = rows.utils.CsvLazyDictWriter(args.csv_filename)  # TODO: use csv
        yt = YouTube(key)
        videos_urls = []
        channels = {}
        for url in tqdm(args.url, desc="Retrieving channel IDs"):
            url = url.strip()
            if "/watch?" in url:
                videos_urls.append(url)
                continue
            channel_id = yt.channel_id_from_url(url)
            if not channel_id:
                username = url.split("youtube.com/")[1].split("?")[0].split("/")[0]
                logger.warning(f"Channel ID not found for URL {url}")
                continue
            channels[channel_id] = {
                "id": channel_id,
                "url": url,
            }
        for channel_id, playlist_id in yt.playlists_ids(list(channels.keys())).items():
            channels[channel_id]["playlist_id"] = playlist_id
        fields = "id duration definition status views likes dislikes favorites comments channel_id title description published_at scheduled_to finished_at concurrent_viewers started_at".split()
        # TODO: check fields
        for data in tqdm(channels.values(), desc="Retrieving videos"):
            try:
                for video_batch in ipartition(yt.playlist_videos(data["playlist_id"]), 50):
                    for video in yt.videos_infos([row["id"] for row in video_batch]):
                        writer.writerow({field: video.get(field) for field in fields})
            except RuntimeError:  # Cannot find playlist
                continue
        videos_ids = (video_url.split("watch?v=")[1].split("&")[0] for video_url in videos_urls)
        for video in tqdm(yt.videos_infos(videos_ids), desc="Retrieving individual videos"):
            writer.writerow({field: video.get(field) for field in fields})
        writer.close()

        # SEARCH
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        timezone_br = datetime.timezone(offset=datetime.timedelta(hours=-3))
        now_br = now.astimezone(timezone_br)
        search_start = (now - datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        search_stop = search_start + datetime.timedelta(hours=1)

        parent = Path(__file__).parent
        parser = argparse.ArgumentParser()
        parser.add_argument("--keys-filename", default=parent / "youtube-keys.csv")
        parser.add_argument("--terms-filename", default=parent / "search-terms.csv")
        parser.add_argument("--channels-filename", default=parent / "search-channels.csv")
        parser.add_argument("--start", default=str(search_start))
        parser.add_argument("--stop", default=str(search_stop))
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument("--order", default="viewCount")
        parser.add_argument("data_path")
        args = parser.parse_args()

        data_path = Path(args.data_path)
        keys_filename = Path(args.keys_filename)
        terms_filename = Path(args.terms_filename)
        channels_filename = Path(args.channels_filename)
        now_path_name = now_br.strftime("%Y-%m-%dT%H")
        youtube_keys = read_keys(keys_filename)
        channels_groups = read_channels(args.channels_filename)
        search_start, search_stop = args.start, args.stop
        if isinstance(search_start, str):
            search_start = datetime.datetime.fromisoformat(search_start)
        if isinstance(search_stop, str):
            search_stop = datetime.datetime.fromisoformat(search_stop)
        search_start_str = search_start.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        search_stop_str = search_stop.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        search_limit = args.limit
        search_order = args.order
        terms_categories = read_csv_dictlist(terms_filename, "categoria", "termo")

        print(search_start_str)
        print(search_stop_str)

        search_start_br = search_start.astimezone(timezone_br)
        result_filename = data_path / f"search_{search_start_br.strftime('%Y-%m-%dT%H')}.csv"
        writer = rows.utils.CsvLazyDictWriter(result_filename)
        search_results = youtube_search(
            terms_categories=terms_categories,
            keys=youtube_keys["search"],
            start=search_start_str,
            stop=search_stop_str,
            channels_groups=channels_groups,
            order=search_order,
            limit=search_limit,
        )
        for result in search_results:
            writer.writerow(result)
        writer.close()


    elif args.command == "video-comments":
        print(f"Implement: {args.command}")  # TODO: implement

    elif args.command == "video-livechat":
        print(f"Implement: {args.command}")  # TODO: implement

    elif args.command == "video-transcription":
        print(f"Implement: {args.command}")  # TODO: implement


if __name__ == "__main__":
    main()
