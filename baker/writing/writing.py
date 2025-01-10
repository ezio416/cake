# c 2025-01-07
# m 2025-01-09

from datetime import datetime as dt, timezone as tz
import json

from transpiling.block import Block
from util.error import LanguageError


class WriterError(LanguageError):
    def __init__(self, component, message):
        super().__init__(component, message)


class LexedWriter:
    def __init__(self, tokens: list[dict], output_dir: str):
        self.tokens: list[dict] = tokens
        self.dir:    str        = output_dir

        with open(f'{self.dir}/lexed.json', 'w', newline='\n') as f:
            json.dump(self.tokens, f, indent=4)
            f.write('\n')


class Writer:
    def __init__(self, blocks: list[Block], output_dir: str, proj: dict):
        self.blocks: list[Block] = blocks
        self.dir:    str         = output_dir
        self.proj:   dict        = proj

        now = dt.now(tz.utc)

        header: list[str] = [
            '// baker - the cake compiler (v0.1.0 copyright 2025 Ezio416)\n',
            f'// generated at {now.year}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)} ',
            f'{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)}:{str(now.second).zfill(2)} UTC\n',
            '// this should be valid C code for which you may use in your compiler of choice\n',
            '// if not, please report it (with your cake code) at https://github.com/ezio416/cake/issues\n'
            f'{'/' * 91}\n',
            f'// project: {proj['name']}\n'
        ]
        if 'author' in proj:
            header.append(f'// author:  {proj['author']}\n')
        if 'version' in proj:
            header.append(f'// version: {proj['version']}\n')
        header.append('\n')

        with open(f'{self.dir}/{proj['name']}.cake.c', 'w', newline='\n') as f:
            f.writelines(header)
            f.write(f'#include "{proj['name']}.cake.h"\n\n')

            for block in self.blocks:
                if block.c:
                    f.write(block.c + '\n')

        with open(f'{self.dir}/{proj['name']}.cake.h', 'w', newline='\n') as f:
            f.writelines(header)

            for block in self.blocks:
                if block.h:
                    f.write(block.h + '\n')
