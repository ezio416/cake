# c 2025-01-07
# m 2025-01-09

import json
import os

from lexing.lexing import Lexer
from lexing.token import Token
from parsing.node import Node
from parsing.parsing import Parser
from reading.line import Line
from reading.reading import Reader
from transpiling.transpiling import Transpiler
from util.error import LanguageError
from writing.writing import LexedWriter, Writer


def main() -> None:
    example_dir: str = f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace('\\', '/')}/example'

    reader = Reader(example_dir)
    # reader.write(f'{example_dir}/output')

    lexer = Lexer(reader.lines)
    lexer.write(f'{example_dir}/output')

    parser = Parser(lexer.tokens)
    # parser.write(f'{example_dir}/output')

    transpiler = Transpiler(parser)
    transpiler.write(f'{example_dir}/output', reader.proj)

    pass


if __name__ == '__main__':
    main()
