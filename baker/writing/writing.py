# c 2025-01-07
# m 2025-01-09

import json

from parsing.node import Node
from util.error import LanguageError


class WriterError(LanguageError):
    def __init__(self, component, message):
        super().__init__(component, message)


class LexedWriter:
    def __init__(self, tokens: list[dict], output_dir: str):
        self.tokens: list[dict] = tokens
        self.dir:    str        = output_dir

    def write(self) -> None:
        with open(f'{self.dir}/lexed.json', 'w', newline='\n') as f:
            json.dump(self.tokens, f, indent=4)


class Writer:
    def __init__(self, nodes: list[Node], output_dir: str):
        self.nodes: list[Node] = nodes
        self.dir:   str        = output_dir

    def write(self) -> None:
        pass
