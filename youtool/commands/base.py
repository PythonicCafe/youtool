import argparse

from typing import List, Dict, Any


class Command():
    """
    classe para os comandos herdarem dela, obedecendo a estrutura
    """
    name: str
    arguments: List[Dict[str, Any]]

    @classmethod
    def generate_parser(cls, subparsers: argparse._SubParsersAction):
        return subparsers.add_parser(cls.name, help=cls.__doc__)

    @classmethod
    def parse_arguments(cls, subparsers: argparse._SubParsersAction) -> None:
        parser = cls.generate_parser(subparsers)
        for argument in cls.arguments:
            argument_copy = {**argument}
            argument_name = argument_copy.pop("name")
            parser.add_argument(argument_name, **argument_copy)
        parser.set_defaults(func=cls.execute)

    @classmethod
    def execute(cls, arguments: argparse.Namespace):
        """método que vai executar o comando"""
