# c 2025-01-07
# m 2025-01-08

import json
import os

from lexing.lexing import Lexer
from lexing.token import Token
from parsing.node import Node
from parsing.parsing import Parser
from reading.line import Line
from reading.reading import Reader
from transpiling.block import Block
from transpiling.transpiling import Transpiler
from util.error import LanguageError


def main() -> None:
    reader = Reader(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace('\\', '/')}/example')
    lexer = Lexer(reader.lines)
    parser = Parser(lexer.tokens)

    pass


if __name__ == '__main__':
    main()
