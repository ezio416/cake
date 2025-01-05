# c 2025-01-02
# m 2025-01-04

import json
import os
import re

from lexing.lexer import Lexer
from lexing.line import Line
from lexing.token import Token
from util.error import LanguageError


def lex(lines: list[Line]) -> list[Token]:
    lexer = Lexer()
    tokens: list[Token] = []

    for line in lines:
        tokens += lexer.make_tokens(line)

    return tokens


def read(path: str) -> tuple[dict, list[Line]]:
    proj:  dict       = {}
    raw:   list[Line] = []
    lines: list[Line] = []

    os.chdir(path)

    for _, _, files in os.walk('.'):
        for file in files:
            if file == 'cake.json':
                with open(f'{path}/{file}') as f:
                    proj = json.load(f)

            elif file.endswith('.cake'):
                with open(f'{path}/{file}') as f:
                    for i, line in enumerate(f):
                        raw.append(Line(f'{path}/{file}', i + 1, line))

    for line in raw:
        strp: str = line.text.strip()
        if strp in ('', '\n') or strp.startswith(('//', '#')):
            continue

        lines.append(line)

    return proj, lines


def main() -> None:
    dir: str = f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace('\\', '/')}/example'
    proj, lines = read(dir)
    tokens: list[Token] = lex(lines)

    print('cake 0.1.0 (interactive): ')
    lexer = Lexer()

    while True:
        text: str = input('> ')
        if text == '':
            continue
        if text == 'exit':
            break

        try:
            line: Line = Line('interactive', 0, text)
            tokens = lexer.make_tokens(line)
            print(tokens)

        except LanguageError as e:
            print(e)


if __name__ == '__main__':
    main()
