# c 2025-01-07
# m 2025-01-10

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
        name:        str         = proj['name']

        now = dt.now(tz.utc)

        header: list[str] = [
            '// baker - the cake compiler (v0.1.0 copyright 2025 Ezio416)\n',
            f'// generated at {now.year}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)} '
            f'{str(now.hour).zfill(2)}:{str(now.minute).zfill(2)}:{str(now.second).zfill(2)} UTC\n',
            '// this should be valid C23 code for which you may use in your compiler of choice\n',
            '// if not, please report it (with your cake code) at https://github.com/ezio416/cake/issues\n',
            f'{'/' * 91}\n',
            f'// project: {name}\n'
        ]
        if 'author' in proj:
            header.append(f'// author:  {proj['author']}\n')
        if 'version' in proj:
            header.append(f'// version: {proj['version']}\n')
        header.append('\n')

        with open(f'{self.dir}/{name}.cake.c', 'w', newline='\n') as f:
            f.writelines(header)

            extra: list[str] = [
                '#include <math.h>\n',
                '#include <stdio.h>\n',
                '#include <stdlib.h>\n',
                f'#include "{name}.cake.h"\n\n',
            ]
            f.writelines(extra)

            for block in self.blocks:
                if block.c:
                    f.write(block.c + '\n\n')

            # temporary until functions are figured out
            f.write('int main(int argc, char *argv[]) {\n    return 0;\n}\n')

        with open(f'{self.dir}/{name}.cake.h', 'w', newline='\n') as f:
            f.writelines(header)

            extra: list[str] = [
                '#include <stdint.h>\n\n',
                'typedef bool    cake_bool;\n',
                'typedef int8_t  cake_int1;  // -128 - 127\n',
                'typedef int16_t cake_int2;  // -32768 - 32767\n',
                'typedef int32_t cake_int4;  // -2.1b - 2.1b\n',
                'typedef int64_t cake_int8;  // -9e18 - 9e18\n\n'
            ]
            f.writelines(extra)

            for block in self.blocks:
                if block.h:
                    f.write(block.h + '\n\n')

        with open(f'{self.dir}/make.cmd', 'w', newline='\n') as f:
            f.write('@echo off\n')
            for i, line in enumerate(header):
                header[i] = 'rem' + line
            f.writelines(header)

            script: list[str] = [
                'rem// this batch script is meant for use on Windows\n',
                'rem// to get GCC, you can use MSYS2: https://www.msys2.org\n\n',
                f'gcc {name}.cake.c -o {name}.cake.o -c -std=gnu23\n',
                f'gcc {name}.cake.o -o {name}\n'
            ]
            f.writelines(script)
