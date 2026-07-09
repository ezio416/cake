from dataclasses import dataclass
import os

from .lexer import Lexer
from .reader import Reader
from .util import debug_header


@dataclass
class Baker:
    dir:        str
    lexer:      Lexer
    output_dir: str
    reader:     Reader

    def __init__(self, dir: str):
        self.dir = dir.replace('\\', '/')
        self.output_dir = os.path.join(self.dir, 'output')

    def bake(self, debug: bool = False) -> None:
        print(f'baking "{self.dir}"{' (debug)' if debug else ''}')

        if debug:
            if not os.path.isdir(self.output_dir):
                os.mkdir(self.output_dir)

            with open(os.path.join(self.output_dir, '0_baker.cakedebug'), 'w', newline='\n') as f:
                f.write(debug_header(f'step 0: baker'))
                f.write(f'input dir:\n\t"{self.dir}"\n')

        self.reader = Reader(self.dir, self.output_dir if debug else '')
        self.reader.read_config()
        self.reader.read_source()
        if debug:
            self.reader.write_debug()

        self.lexer = Lexer(self.reader.files, self.output_dir if debug else '')
        self.lexer.lex()
        if debug:
            self.lexer.write_debug()

        ...
