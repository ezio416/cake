from dataclasses import dataclass
import json
import os


__all__ = [
    'Config',
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


class ReaderError(Exception):
    pass


@dataclass
class SourceFile:
    lines: list[str]
    path:  str

    def __init__(self, path: str):
        self.path = path.replace('\\', '/')

        with open(self.path) as f:
            self.lines = f.readlines()


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
