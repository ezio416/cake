from dataclasses import dataclass
import json
import os


__all__ = [
    'Config',
    'Line',
    'ReaderError',
    'SourceFile',
    'read_config',
    'read_source'
]


CONFIG_FILE_NAME = 'cake.json'
SOURCE_EXTENSION = '.cake'


@dataclass
class Config:
    author:  str
    name:    str
    version: str

    def __init__(self, path: str):
        if not os.path.isfile(path):
            raise ReaderError('missing config file')

        with open(path) as f:
            data: dict = json.load(f)

        self.author  = data['author']
        self.name    = data['name']
        self.version = data['version']


@dataclass
class Line:
    file:   SourceFile
    lineno: int
    locale: list[int]
    text:   str

    def __init__(self, file: SourceFile, lineno: int, text: str):
        self.file   = file
        self.lineno = lineno
        self.locale = [0, 0]
        self.text   = text

    def finished(self) -> bool:
        return self.locale[1] >= len(self.text)

    def ignore(self) -> None:
        self.locale[0] = self.locale[1]

    def new_locale(self) -> tuple[list[int], str]:
        locale = self.locale.copy()
        taken = self.taken()
        self.ignore()
        return locale, taken

    def next(self) -> str:
        return 'EOF' if self.finished() else self.text[self.locale[1]]

    def take(self) -> str:
        symbol = self.next()
        if self.finished():
            self.locale[1] += 1
        return symbol

    def taken(self) -> str:
        return self.text[self.locale[0]:self.locale[1]]


class ReaderError(Exception):
    pass


@dataclass
class SourceFile:
    lines: list[Line]
    path:  str

    def __init__(self, path: str):
        self.path = path.replace('\\', '/')

        self.lines = []

        with open(self.path) as f:
            for i, line in enumerate(f):
                self.lines.append(Line(self, i + 1, line))


def read_config(folder: str) -> Config:
    _verify_folder_exists(folder)

    return Config(os.path.join(folder, CONFIG_FILE_NAME))


def read_source(folder: str) -> list[SourceFile]:
    _verify_folder_exists(folder)

    ret: list[SourceFile] = []

    for dir, _, files in os.walk(folder):
        for file in files:
            if file.endswith(SOURCE_EXTENSION):
                ret.append(SourceFile(os.path.join(dir, file)))

    return ret


def _verify_folder_exists(folder: str) -> None:
    if not os.path.isdir(folder):
        raise ReaderError(f'given folder does not exist: "{folder}"')
