# c 2025-01-02
# m 2025-01-04

from .keywords import *
from .line import Line
from .token import Token
from util.error import LanguageError


class LexerError(LanguageError):
    def __init__(self, component, message: str, column: int = 0):
        super().__init__(component, message)
        self.column: int = column

    def __str__(self) -> str:
        msg: str = f'{type(self).__name__} ({self.line.filename}'
        if self.line.filename != 'interactive':
            msg += f', line {self.line.lineno}, column {self.column}'
        return f'{msg}): {self.message}\n{self.line.get_marks()}'


class Lexer:
    def __init__(self):
        self.line: Line | None = None

    def ignore_spaces(self) -> None:
        while self.line.next().isspace():
            self.line.take()
            self.line.ignore()

    def make_identifier(self) -> Token:
        while self.line.next().lower() in IDENTIFIER_SYMBOLS:
            self.line.take()

        identifier: Token = self.new_token('Identifier')
        if identifier.locale[0] < identifier.locale[1]:
            return identifier

        raise LexerError(
            identifier,
            f'error lexing identifier\n  {self.line.string}',
            self.line.locale[0]
        )

    def make_number(self) -> Token:
        while self.line.next() in NUMBER_SYMBOLS:
            self.line.take()

        taken: str = self.line.taken()
        if all((
            taken.count('.') < 2,
            taken.count('d') < 2,
            taken.count('e') < 2
        )):
            return self.new_token('Number')

        raise LexerError(
            self.new_token('Number'),
            f"numbers can't have more than one of each of these symbols: . d e\n  {self.line.string}",
            self.line.locale[0]
        )

    def make_operator(self) -> Token:
        op:   str = self.line.take()
        next: str = self.line.next()

        if op == '/' and next == '/':
            while self.line.next() != 'EOF':
                self.line.take()
            # return self.new_token('Comment')
            return

        if any((
            op == '*' and next == '*',
            op == '&' and next == '&',
            op == '|' and next == '|',
            op == '^' and next == '^',
            op == ':' and next == ':',
        )):
            self.line.take()

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
            else:
                print('took', self.line.taken())

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
        self.line           = line
        tokens: list[Token] = []

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
