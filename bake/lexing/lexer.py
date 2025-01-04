# c 2025-01-02
# m 2025-01-04

from .line import Line
from .token import Token
from util.error import LanguageError

class LexerError(LanguageError):
    pass

class Lexer:
    def __init__(self):
        self.line: Line | None = None

    def ignore_spaces(self) -> None:
        while self.line.next().isspace():
            self.line.take()
            self.line.ignore()

    def make_number(self) -> Token:
        while self.line.next() in "0123456789.'ef":
            self.line.take()

        taken: str = self.line.taken()
        if all((
            taken.count('.') < 2,
            taken.count('e') < 2,
            taken.count('f') < 2
        )):
            return self.new_token('Number')

        raise LexerError(self.new_token('Number'), "numbers can't have more than one of each of these symbols: . e f")

    def make_operator(self) -> Token:
        op: str = self.line.take()

        if any((
            op == '*' and self.line.next() == '*',
            op == '&' and self.line.next() == '&',
            op == '|' and self.line.next() == '|',
            op == '^' and self.line.next() == '^',
        )):
            self.line.take()

        return self.new_token('Operator')

    def make_punctuator(self) -> Token:
        self.line.take()
        return self.new_token('Punctuator')

    def make_token(self) -> Token:
        if self.line.next() in '0123456789':
            return self.make_number()

        if self.line.next() in '=+-*/%!&|^':
            return self.make_operator()

        if self.line.next() in r'<>[]{}();':
            return self.make_punctuator()

        self.line.take()
        raise LexerError(self.new_token('?'), 'unrecognized symbol')

    def make_tokens(self, line: Line) -> list[Token]:
        self.line           = line
        tokens: list[Token] = []

        while not self.line.finished():
            self.ignore_spaces()
            if self.line.finished():
                break

            tokens.append(self.make_token())

        tokens.append(self.new_token('Punctuator'))
        return tokens

    def new_token(self, kind: str) -> Token:
        return Token(self.line, kind)
