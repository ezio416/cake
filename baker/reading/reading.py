# c 2025-01-07
# m 2025-01-09

import json
import os

from util.error import LanguageError
from .line import Line


class ReaderError(LanguageError):
    def __init__(self, component, message: str):
        super().__init__(component, message)


class Reader:
    def __init__(self, dir: str):
        self.dir: str = dir.rstrip('/')

        self.files:     list[str]  = []
        self.lines:     list[Line] = []
        self.proj:      dict       = {}
        self.proj_file: str        = ''

        raw: list[Line] = []

        os.chdir(self.dir)

        for dir, _, files in os.walk('.'):
            for file in files:
                if file == 'cake.json':
                    self.proj_file = f'{self.dir}/{file}'
                    with open(self.proj_file) as f:
                        self.proj = json.load(f)

                elif file.endswith('.cake'):
                    par: str = dir.lstrip('.')
                    par = f'{self.dir}/{par.replace('\\', '/').lstrip('/')}'.rstrip('/')
                    self.files.append(path := f'{par}/{file}')
                    with open(path) as f:
                        for i, line in enumerate(f):
                            raw.append(Line(path, i + 1, line))

        if not self.proj:
            raise ReaderError(self, 'invalid/missing project file')

        if not self.files:
            raise ReaderError(self, 'no files in project')

        if not raw:
            raise ReaderError(self, 'no source code in files')

        for line in raw:
            strp: str = line.string.strip()
            if strp in ('', '\n') or strp.startswith(('//', '#')):
                continue

            self.lines.append(line)

    @property
    def line(self) -> None:
        pass

    def mark(self) -> None:
        pass
