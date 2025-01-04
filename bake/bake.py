# c 2025-01-02
# m 2025-01-03

import json
import os
import re


class Block:
    pass


class Char:
    def __init__(self, line, column: int, char: str):
        self.line         = line
        self.column: int  = column
        self.char:   str  = char

    def __repr__(self) -> str:
        return f'{self.line.__repr__()} {self.column} "{self.char}"'


class Line:
    def __init__(self, filename: str, line: int, text: str):
        self.filename: str = filename
        self.line:     int = line

        self.text: str = text
        if self.text.endswith('\n'):
            self.text = self.text[:-1]

        self.chars: list[Char] = []

    def __repr__(self) -> str:
        return f'{type(self)} {self.filename} {self.line}'

    def add_char(self, char: Char) -> None:
        self.chars.append(char)


def lex(lines: list[Line]) -> list[Block]:
    pass


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
        line.text = line.text.strip()
        if line.text in ('', '\n') or line.text.startswith(('//', '#')):
            continue

        for i, c in enumerate(line.text):
            char: Char = Char(line, i, c)
            line.add_char(char)

        lines.append(line)

    return proj, lines


def main() -> None:
    dir: str = f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace('\\', '/')}/example'
    proj, lines = read(dir)

    # blocks: list[Block] = lex(lines)

    pass


if __name__ == '__main__':
    main()
