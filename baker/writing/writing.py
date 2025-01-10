# c 2025-01-07
# m 2025-01-07

from parsing.node import Node
from util.error import LanguageError


class WriterError(LanguageError):
    def __init__(self, component, message):
        super().__init__(component, message)


class Writer:
    def __init__(self, nodes: list[Node], output_dir: str):
        self.nodes: list[Node] = nodes
        self.dir:   str        = output_dir

    def write(self) -> None:
        pass
