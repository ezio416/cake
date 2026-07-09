from dataclasses import dataclass
import json
import os

from .util import LanguageError, debug_header


CONFIG_FILE_NAME = 'cake.json'
SOURCE_EXTENSION = '.cake'


@dataclass
class Config:
    author:  str
    name:    str
    path:    str
    version: str

    def __init__(self, path: str):
        if not os.path.isfile(path):
            raise ReaderError(f'missing config file: "{path}"')

        self.path = path

        print(f'reading "{self.path}"')
        with open(self.path) as f:
            data: dict = json.load(f)

        self.author  = data['author']
        self.name    = data['name']
        self.version = data['version']


@dataclass
class Line:
    file:   SourceFile
    locale: list[int]
    num:    int
    string: str

    def __init__(self, file: SourceFile, num: int, string: str):
        self.file   = file
        self.locale = [0, 0]
        self.num    = num
        self.string = string

    def finished(self) -> bool:
        return self.locale[1] >= len(self.string)

    def ignore(self) -> None:
        self.locale[0] = self.locale[1]

    def ignore_spaces(self) -> None:
        while self.next().isspace():
            self.take()
            self.ignore()

    def loc(self) -> str:
        return f'({self.file.path}, line {self.num}, column {self.locale[0] + 1})'

    def new_locale(self) -> tuple[list[int], str]:
        locale = self.locale.copy()
        taken = self.taken()
        self.ignore()
        return locale, taken

    def next(self) -> str:
        return 'EOF' if self.finished() else self.string[self.locale[1]]

    def take(self) -> str:
        symbol = self.next()
        if not self.finished():
            self.locale[1] += 1
        return symbol

    def taken(self) -> str:
        return self.string[self.locale[0]:self.locale[1]]


@dataclass
class Reader:
    dir:        str
    config:     Config
    files:      list[SourceFile]
    lines:      list[Line]
    output_dir: str

    def __init__(self, dir: str, output_dir: str = ''):
        self.dir        = dir
        self.output_dir = output_dir

    def read_config(self) -> None:
        self.config = Config(os.path.join(self.dir, CONFIG_FILE_NAME))

    def read_source(self) -> None:
        self.files = []

        for dir, _, files in os.walk(self.dir):
            for file in files:
                if file.endswith(SOURCE_EXTENSION):
                    self.files.append(SourceFile(os.path.join(dir, file)))

        self.lines = []

        for file in self.files:
            self.lines += file.lines

    def write_debug(self) -> None:
        if not self.output_dir:
            raise ReaderError('no output folder given')

        with open(os.path.join(self.output_dir, '1_reader.cakedebug'), 'w', newline='\n') as f:
            f.write(debug_header(f'step 1: reader'))
            f.write(f'config:\n')
            f.write(f'    path:    "{self.config.path}"\n')
            f.write(f'    author:  {self.config.author}\n')
            f.write(f'    name:    {self.config.name}\n')
            f.write(f'    version: {self.config.version}\n')
            f.write('source files:\n')
            for file in self.files:
                f.write(f'    "{file.path}" ({len(file.lines)} line{'s' if len(file.lines) != 1 else ''})\n')


class ReaderError(LanguageError):
    pass


@dataclass
class SourceFile:
    lines:  list[Line]
    path:   str
    tokens: list

    def __init__(self, path: str):
        self.path = path.replace('\\', '/')

        self.lines = []

        print(f'reading "{self.path}"')
        with open(self.path) as f:
            for i, line in enumerate(f):
                self.lines.append(Line(self, i + 1, line))
