# c 2025-01-02
# m 2025-01-03

import json
import os
import re


class Block:
    pass


class Line:
    def __init__(self, filename: str, line: int, text: str):
        self.filename: str = filename
        self.line:     int = line

        self.text: str = text
        if self.text.endswith('\n'):
            self.text = self.text[:-1]

    def __repr__(self) -> str:
        return f'{type(self)} {self.filename} {self.line}'


def lex(lines: list[Line]) -> list[Block]:
    for line in lines:
        pass


def read(path: str) -> tuple[dict, list[Line]]:
    proj:  dict       = {}
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
                        line = line.strip()
                        if line in ('', '\n') or line.startswith(('//', '#')):
                            continue
                        lines.append(Line(f'{path}/{file}', i + 1, line))

    return proj, lines


def main() -> None:
    dir: str = f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace('\\', '/')}/example'
    proj, lines = read(dir)

    # blocks: list[Block] = lex(lines)

    pass


if __name__ == '__main__':
    main()
