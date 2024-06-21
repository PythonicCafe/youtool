import argparse

from typing import List, Dict, Any


class Command():
    """
    A base class for commands to inherit from, following a specific structure.
    
    Attributes:
        name (str): The name of the command.
        arguments (List[Dict[str, Any]]): A list of dictionaries, each representing an argument for the command.
    """
    name: str
    arguments: List[Dict[str, Any]]

    @classmethod
    def generate_parser(cls, subparsers: argparse._SubParsersAction):
        """
        Creates a parser for the command and adds it to the subparsers.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers action to add the parser to.

        Returns:
            argparse.ArgumentParser: The parser for the command.
        """
        return subparsers.add_parser(cls.name, help=cls.__doc__)

    @classmethod
    def parse_arguments(cls, subparsers: argparse._SubParsersAction) -> None:
        """
        Parses the arguments for the command and sets the command's execute method as the default function to call.

        Args:
            subparsers (argparse._SubParsersAction): The subparsers action to add the parser to.
        """
        parser = cls.generate_parser(subparsers)
        for argument in cls.arguments:
            argument_copy = {**argument}
            argument_name = argument_copy.pop("name")
            parser.add_argument(argument_name, **argument_copy)
        parser.set_defaults(func=cls.execute)

    @classmethod
    def execute(cls, arguments: argparse.Namespace):
        """
        Executes the command.

        This method should be overridden by subclasses to define the command's behavior.

        Args:
            arguments (argparse.Namespace): The parsed arguments for the command.
        """