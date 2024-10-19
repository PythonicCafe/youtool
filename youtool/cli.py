import argparse

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
    main_parser = argparse.ArgumentParser(description="CLI Tool for managing YouTube videos add playlists")
    main_parser.add_argument("--debug", "-d", action="store_true")

    subparsers = main_parser.add_subparsers(
        required=True, dest="command", title="Command", help="Command to be executed"
    )
    for command in COMMANDS:
        subparser = subparsers.add_parser(command.name, help=command.__doc__)
        subparser.set_defaults(func=command.execute)
        if hasattr(command, "add_arguments"):
            command.add_arguments(subparser)
    args = main_parser.parse_args()

    try:
        result = args.func(**args.__dict__)
        if result:
            print(result)
    except Exception as error:
        import traceback

        if args.debug:
            print(traceback.format_exc())
        main_parser.error(error)


if __name__ == "__main__":
    main()
