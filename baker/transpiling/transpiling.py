# c 2025-01-07
# m 2025-01-09

from writing.writing import Writer
from parsing.parsing import Parser
from .block import Block


class Transpiler:
    def __init__(self, parser: Parser):
        self.parser: Parser      = parser
        self.blocks: list[Block] = []

        # for key, val in self.parser.classes.items():
        #     self.blocks.append(Block(val))
        for key, val in self.parser.enums.items():
            self.blocks.append(Block(val))
        # for key, val in self.parser.functions.items():
        #     self.blocks.append(Block(val))
        # for key, val in self.parser.namespaces.items():
        #     self.blocks.append(Block(val))
        # for key, val in self.parser.structs.items():
        #     self.blocks.append(Block(val))

    def write(self, dir: str, proj: dict) -> None:
        Writer(self.blocks, dir, proj)
