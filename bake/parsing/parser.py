# c 2025-01-04
# m 2025-01-04

from parsing.expressions.expression import Expression
from lexing.token import Token
from util.error import LanguageError


class ParserError(LanguageError):
    pass


class Parser:
    @property
    def expression(self) -> type[Expression]:
        return Expression

    def __init__(self):
        self.tokens: list[Token] | None = None
        self.i:      int                = -1

    def expecting_has(self, *strings) -> Token:
        if self.next().has(*strings):
            return self.take()

        raise ParserError(self.next(), f'expecting has {strings}')

    def expecting_of(self, *kinds) -> Token:
        if self.next().of(*kinds):
            return self.take()

        raise ParserError(self.next(), f'expecting of {kinds}')

    def next(self) -> Token:
        return self.tokens[self.i]

    def take(self) -> Token:
        token = self.next()
        self.i += 1
        return token

    def make_tree(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.i = 0
        node = Expression.construct(self)

        if self.next().has('EOF'):
            return node

        raise ParserError(self.next(), f'unexpected token {self.next()}')
