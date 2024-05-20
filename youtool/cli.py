import argparse


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

    elif args.command == "video-comments":
        print(f"Implement: {args.command}")  # TODO: implement

    elif args.command == "video-livechat":
        print(f"Implement: {args.command}")  # TODO: implement

    elif args.command == "video-transcription":
        print(f"Implement: {args.command}")  # TODO: implement


if __name__ == "__main__":
    main()
