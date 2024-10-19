import argparse
import os

from .commands import COMMANDS


def main():
    """Main function for the YouTube CLI Tool.

    This function sets up the argument parser for the CLI tool, including options for the YouTube API key and
    command-specific subparsers. It then parses the command-line arguments, retrieving the YouTube API key
    from either the command-line argument '--api-key' or the environment variable 'YOUTUBE_API_KEY'. If the API
    key is not provided through any means, it raises an argparse.ArgumentError.

    Finally, the function executes the appropriate command based on the parsed arguments. If an exception occurs
    during the execution of the command, it is caught and raised as an argparse error for proper handling.

    Raises:
        argparse.ArgumentError: If the YouTube API key is not provided.
        argparse.ArgumentError: If there is an error during the execution of the command.
    """
    parser = argparse.ArgumentParser(description="CLI Tool for managing YouTube videos add playlists")
    parser.add_argument("--api-key", type=str, help="YouTube API Key", dest="api_key")
    parser.add_argument("--debug", default=False, action="store_true", help="Debug mode", dest="debug")

    subparsers = parser.add_subparsers(required=True, dest="command", title="Command", help="Command to be executed")

    for command in COMMANDS:
        command.parse_arguments(subparsers)

    args = parser.parse_args()
    args.api_key = args.api_key or os.environ.get("YOUTUBE_API_KEY")

    if not args.api_key:
        parser.error("YouTube API Key is required")

    try:
        print(args.func(**args.__dict__))
    except Exception as error:
        if args.debug:
            raise error
        parser.error(error)


if __name__ == "__main__":
    main()
