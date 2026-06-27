from dataclasses import dataclass

import reader


__all__ = [
    'LexerError',
    'Token',
    'tokenize'
]


IDENTIFIER_SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'
LOGIC_KEYWORDS     = 'and', 'nand', 'nor', 'not', 'nox', 'or', 'xor'
NUMBER_SYMBOLS     = "0123456789'."
OPERATOR_SYMBOLS   = '=+-*/%!&|^<>'
PUNCTUATOR_SYMBOLS = r'{}[]();,"'
SPECIAL_KEYWORDS   = 'as', 'break', 'case', 'cast', 'continue', 'do', 'else', 'false', 'for', 'if', 'in', 'return',\
    'switch', 'true', 'while', 'with'
TYPE_KEYWORDS      = 'bool', 'char', 'f32', 'f64', 'i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64', 'void'


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
                        raise LexerError(f'numbers must start with a digit: "{line.taken()}"')
                    if line.taken().count('.') > 1:
                        raise LexerError(f'numbers can have a maximum of one decimal point: "{line.taken()}"')
                    tokens.append(Token('Number', line))

                elif line.next() in OPERATOR_SYMBOLS:
                    op = line.take()
                    for char in '=*&|^<>':
                        if op == char and line.next() in char + '=':
                            line.take()
                            break
                    for char in '+-':
                        if op == char and line.next() in char:
                            line.take()
                            break
                    tokens.append(Token('Operator', line))

                elif line.next() in PUNCTUATOR_SYMBOLS:
                    line.take()
                    tokens.append(Token('Punctuator', line))

                elif line.next() in IDENTIFIER_SYMBOLS:
                    while line.next() in IDENTIFIER_SYMBOLS:
                        line.take()
                    if line.taken()[0] in NUMBER_SYMBOLS:
                        raise LexerError(f'identifiers cannot start with a digit: "{line.taken()}"')
                    if line.taken() in SPECIAL_KEYWORDS:
                        tokens.append(Token('Special', line))
                    elif line.taken() in TYPE_KEYWORDS:
                        tokens.append(Token('Type', line))
                    elif line.taken() in LOGIC_KEYWORDS:
                        tokens.append(Token('Operator', line))
                    else:
                        tokens.append(Token('Identifier', line))

                else:
                    raise LexerError(
                        f'unexpected symbol at {line.file.path},{line.num},{line.locale[0]}: "{line.next()}"'
                    )

            tokens.append(Token('Punctuator', line))

    return tokens
