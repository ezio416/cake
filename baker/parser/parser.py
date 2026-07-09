from dataclasses import dataclass
import os

from .expressions.expression import Expression
from .node import Node
from ..lexer import Token
from ..util import LanguageError, debug_header


@dataclass
class Parser:
    index:      int
    output_dir: str
    tokens:     list[Token]
    tree:       Node

    @property
    def expression(self):
        return Expression

    def __init__(self, tokens: list[Token], output_dir: str = ''):
        self.tokens     = tokens
        self.output_dir = output_dir

    def next(self) -> Token:
        return self.tokens[self.index]

    def take(self) -> Token:
        token = self.next()
        self.index += 1
        return token

    def expecting_has(self, *strings: str) -> Token:
        if self.next().has(*strings):
            return self.take()

        raise ParserError(self.next(), f'expecting has {strings}')

    def expecting_of(self, *kinds: str) -> Token:
        if self.next().of(*kinds):
            return self.take()

        raise ParserError(self.next(), f'expecting of {kinds}')

    def parse(self) -> None:
        print(f'parsing {len(self.tokens)} tokens')

        self.index = 0
        node = Expression.construct(self)
        next = self.next()

        if next.has('EOF'):
            self.tree = node
        else:
            raise ParserError(next, f'unexpected token {next}')

    def write_debug(self) -> None:
        if not self.output_dir:
            raise ParserError('no output folder given')

        with open(os.path.join(self.output_dir, '3_parser.cakedebug'), 'w', newline='\n') as f:
            f.write(debug_header('step 3: parser'))
            f.write(f'tree:\n\t{self.tree}\n')


class ParserError(LanguageError):
    pass
