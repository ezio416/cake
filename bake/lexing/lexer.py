# c 2025-01-02
# m 2025-01-04

from .keywords import KEYWORDS
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

        raise LexerError(
            self.new_token('Number'),
            f"numbers can't have more than one of each of these symbols: . e f\n  {self.line.text}",
            self.line.locale[0]
        )

    def make_operator(self) -> Token:
        op:   str = self.line.take()
        next: str = self.line.next()

        if op == '/' and next == '/':
            while self.line.next() != 'EOF':
                self.line.take()
            return self.new_token('Comment')

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
            f'dangling string\n  {self.line.text}',
            self.line.locale[0]
        )

    def make_token(self) -> Token:
        next: str = self.line.next()

        if next in '0123456789':
            return self.make_number()

        if next in '!%^&*-+=|:,./?':
            return self.make_operator()  # also comments

        if next in r'<>[]{}();':
            return self.make_punctuator()

        if next == '"':
            return self.make_string()

        if next.lower() in 'abcdefghijklmnopqrstuvwxyz':
            return self.make_word()

        self.line.take()
        raise LexerError(
            self.new_token('?'),
            f'unrecognized symbol\n  {self.line.text}',
            self.line.locale[0]
        )

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

    def make_word(self) -> Token:
        while self.line.next().lower() in 'abcdefghijklmnopqrstuvqxyz0123456789_':
            self.line.take()

        word: Token = self.new_token('Word')
        if word.locale[0] < word.locale[1]:
            return word

        raise LexerError(
            word,
            f'error lexing word\n  {self.line.text}',
            self.line.locale[0]
        )

    def new_token(self, kind: str) -> Token:
        return Token(self.line, kind)
