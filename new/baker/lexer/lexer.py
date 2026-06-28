from dataclasses import dataclass

import reader


__all__ = [
    'LexerError',
    'Token',
    'tokenize'
]


DIGIT_SYMBOLS      = '0123456789'
IDENTIFIER_SYMBOLS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
LOGIC_KEYWORDS     = 'and', 'nand', 'nor', 'not', 'nox', 'or', 'xor'
NUMBER_SYMBOLS     = "'-.0123456789ABCDEFabcdefox"
OPERATOR_SYMBOLS   = '!%&*+-./:<=>^|~'
PUNCTUATOR_SYMBOLS = r'"(),;[]{}'
SPECIAL_KEYWORDS   = 'abstract', 'as', 'async', 'await', 'break', 'case', 'cast', 'catch', 'class', 'continue',\
    'default', 'do', 'else', 'enum', 'escape', 'extern', 'false', 'final', 'finally', 'for', 'funcdef', 'global', 'if',\
    'in', 'interface', 'mixin', 'mut', 'namespace', 'nonlocal', 'of', 'override', 'private', 'protected', 'return',\
    'static', 'struct', 'super', 'switch', 'this', 'throw', 'true', 'try', 'typedef', 'union', 'while', 'with', 'yield'
TYPE_KEYWORDS      = 'auto', 'bool', 'char', 'f32', 'f64', 'i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64', 'void'
UNUSED_SYMBOLS     = '#$?@`'


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

                if line.next() in OPERATOR_SYMBOLS:
                    op = line.take()
                    if op == '/' and line.next() == '/':
                        line.ignore()
                        break
                    for char in '!%&*+-/<=>^|':
                        if op == char and line.next() in char + '=':
                            line.take()
                    if op == ':' and line.next() == ':':
                        line.take()
                    tokens.append(Token('Operator', line))

                elif line.next() in DIGIT_SYMBOLS:
                    while line.next() in NUMBER_SYMBOLS:
                        line.take()
                    taken = line.taken()
                    if taken[0] not in '0123456789':
                        raise LexerError(f'numbers must start with a digit {line.loc()}: "{taken}"')
                    if taken.count('.') > 1:
                        raise LexerError(f'numbers can have a maximum of one decimal point {line.loc()}: "{taken}"')
                    if taken[0] == '0':
                        if len(taken) > 1:
                            if taken[1] == 'b':
                                if len(taken) == 2:
                                    raise LexerError(f'invalid binary number {line.loc()}: "{taken}"')
                                for char in taken[2:]:
                                    if char not in "'01":
                                        raise LexerError(f'invalid binary number {line.loc()}: "{taken}"')
                            elif taken[1] == 'o':
                                if len(taken) == 2:
                                    raise LexerError(f'invalid octal number {line.loc()}: "{taken}"')
                                for char in taken[2:]:
                                    if char not in "'01234567":
                                        raise LexerError(f'invalid octal number {line.loc()}: "{taken}"')
                            elif taken[1] == 'x':
                                if len(taken) == 2:
                                    raise LexerError(f'invalid hexadecimal number {line.loc()}: "{taken}"')
                                for char in taken[2:]:
                                    if char not in "'0123456789ABCDEFabcdef":
                                        raise LexerError(f'invalid hexadecimal number {line.loc()}: "{taken}"')
                    elif 'e' in taken:
                        if taken.count('e') > 1 or taken.startswith('e') or taken.endswith('e'):
                            raise LexerError(f'invalid scientific number {line.loc()}: "{taken}"')
                        coef, exp = taken.split('e')
                        if '-' in coef or ('-' in exp and (not exp.startswith('-') or exp.count('-') > 1)):
                            raise LexerError(f'invalid scientific number {line.loc()}: "{taken}"')
                        for char in exp:
                            if char not in DIGIT_SYMBOLS + '-':
                                raise LexerError(f'invalid scientific number {line.loc()}: "{taken}"')
                    tokens.append(Token('Number', line))

                elif line.next() in PUNCTUATOR_SYMBOLS:
                    line.take()
                    tokens.append(Token('Punctuator', line))

                elif line.next() in IDENTIFIER_SYMBOLS:
                    while line.next() in IDENTIFIER_SYMBOLS:
                        line.take()
                    taken = line.taken()
                    if taken in LOGIC_KEYWORDS:
                        tokens.append(Token('Operator', line))
                    elif taken in SPECIAL_KEYWORDS:
                        tokens.append(Token('Special', line))
                    elif taken in TYPE_KEYWORDS:
                        tokens.append(Token('Type', line))
                    else:
                        tokens.append(Token('Identifier', line))

                else:
                    raise LexerError(
                        f'unexpected symbol {line.loc()}: "{line.next()}"'
                    )

            if tokens:
                tokens.append(Token('Punctuator', line))

    return tokens
