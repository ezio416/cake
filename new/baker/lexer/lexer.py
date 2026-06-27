from dataclasses import dataclass

import reader


__all__ = [
    'LexerError',
    'Token',
    'tokenize'
]


NUMBER_SYMBOLS     = "0123456789'."
OPERATOR_SYMBOLS   = '%*-+=/'
PUNCTUATOR_SYMBOLS = r'{}[]();,'


class LexerError(RuntimeError):
    pass


@dataclass
class Token:
    kind:   str
    line:   reader.Line
    locale: list[int]
    text:   str

    def __init__(self, kind: str, line: reader.Line):
        self.kind = kind
        self.line = line
        self.locale, self.text = line.new_locale()

        self.text = self.text or 'EOF'

    def __repr__(self):
        return f"{self.kind[0]}'{self.text}'"


def tokenize(source: list[reader.SourceFile]) -> list[Token]:
    tokens: list[Token] = []

    for file in source:
        for line in file.lines:
            while not line.finished():
                line.ignore_spaces()

                if line.finished():
                    break

                if line.next() in NUMBER_SYMBOLS:
                    while line.next() in NUMBER_SYMBOLS:
                        line.take()
                    if line.taken()[0] not in NUMBER_SYMBOLS:
                        raise LexerError('numbers must start with a digit')
                    if line.taken().count('.') > 1:
                        raise LexerError('numbers can have, at most, one decimal point')
                    tokens.append(Token('Number', line))

                elif line.next() in OPERATOR_SYMBOLS:
                    op = line.take()
                    if op == '*' and line.next() == "*":
                        line.take()
                    tokens.append(Token('Operator', line))

                elif line.next() in PUNCTUATOR_SYMBOLS:
                    line.take()
                    tokens.append(Token('Punctuator', line))

                else:
                    raise LexerError(
                        f'unexpected symbol at {line.file.path},{line.num},{line.locale[0]}: "{line.next()}"'
                    )

            tokens.append(Token('Punctuator', line))

    return tokens
