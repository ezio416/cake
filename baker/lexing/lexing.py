# c 2025-01-02
# m 2025-01-09

import re

from reading.line import Line
from util.error import LanguageError
from .keywords import *
from .token import Token


class LexerError(LanguageError):
    def __init__(self, component, message: str, column: int = 0):
        super().__init__(component, message)
        self.column: int = column

    def __str__(self) -> str:
        return f'{type(self).__name__} ({self.line.filename}, line {self.line.lineno}, column {self.column}): {self.message}\n  {self.line.string}\n{self.line.get_marks()}'


class Lexer:
    def __init__(self, lines: list[Line]):
        self.line:   Line | None = None
        self.lines:  list[Line]  = lines
        self.tokens: list[Token] = []

        file: str = ''
        for i, line in enumerate(self.lines):
            if file != line.filename:
                file = line.filename
                if i:
                    self.tokens.append(self.new_token('Punctuator'))

            self.tokens += self.make_tokens(line)

        self.tokens.append(self.new_token('Punctuator'))

    def ignore_spaces(self) -> None:
        while self.line.next().isspace():
            self.line.take()
            self.line.ignore()

    def make_identifier(self) -> Token:
        while self.line.next().lower() in IDENTIFIER_SYMBOLS:
            self.line.take()

        identifier: Token = self.new_token('Identifier')

        fixed_type: bool = identifier.string.startswith(('dec', 'int', 'str')) \
            and bool(re.match(r'(?:dec|int|str)[0-9]*(?:[0-9]*)$', identifier.string))

        if identifier.locale[0] < identifier.locale[1]:
            if fixed_type or identifier.has(*KEYWORDS):
                identifier.kind = 'Keyword'
            return identifier

        raise LexerError(
            identifier,
            f'error lexing identifier\n  {self.line.string}',
            self.line.locale[0]
        )

    def make_number(self) -> Token:
        while self.line.next() in NUMBER_SYMBOLS:
            self.line.take()

        return self.new_token('Number')

    def make_operator(self) -> Token:
        op:   str = self.line.take()
        next: str = self.line.next()

        if op == '/' and next == '/':
            while self.line.next() != 'EOF':
                self.line.take()
            # return self.new_token('Comment')
            return

        return self.new_token('Operator')

    def make_punctuator(self) -> Token:
        self.line.take()
        return self.new_token('Punctuator')

    def make_string(self) -> Token:
        self.line.take()

        while True:
            took: bool = False

            if self.line.taken().endswith('\\') and self.line.next() == '"':
                self.line.take()
                took = True

            while self.line.next() not in '"EOF':
                self.line.take()
                took = True

            if not took:
                break
            # else:
            #     print('took', self.line.taken())

        if self.line.next() == '"':
            self.line.take()
            return self.new_token('String')

        raise LexerError(
            self.new_token('String'),
            f'dangling string\n  {self.line.string}',
            self.line.locale[0]
        )

    def make_token(self) -> Token:
        next: str = self.line.next()

        if next in IDENTIFIER_START_SYMBOLS:
            return self.make_identifier()

        if next in NUMBER_START_SYMBOLS:
            return self.make_number()

        if next in OPERATOR_SYMBOLS:
            return self.make_operator()  # also comments

        if next in PUNCTUATOR_SYMBOLS:
            return self.make_punctuator()

        if next == '"':
            return self.make_string()

        self.line.take()
        raise LexerError(
            self.new_token('?'),
            f'unrecognized symbol\n  {self.line.string}',
            self.line.locale[0]
        )

    def make_tokens(self, line: Line) -> list[Token]:
        tokens: list[Token] = []

        self.line = line
        while not self.line.finished():
            self.ignore_spaces()
            if self.line.finished():
                break

            token: Token | None = self.make_token()
            if token is not None:
                tokens.append(token)

        return tokens

    def new_token(self, kind: str) -> Token:
        return Token(self.line, kind)

    def to_dict(self) -> list[dict]:
        ret: list[dict] = []

        for token in self.tokens:
            ret.append({ 'k': token.kind[0], 's': token.string if token.string != 'EOF' else '' })

        return ret
