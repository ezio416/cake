from dataclasses import dataclass
import os

from .reader import Line, SourceFile
from .util import LanguageError, debug_header


DIGIT_SYMBOLS      = '0123456789'
IDENTIFIER_SYMBOLS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
LOGIC_KEYWORDS     = 'and', 'nand', 'nor', 'not', 'nox', 'or', 'xor'
NUMBER_SYMBOLS     = "'-.0123456789ABCDEFabcdefox"
OPERATOR_SYMBOLS   = '!$%&*+-./:<=>?^|~'
PUNCTUATOR_SYMBOLS = r'"(),;[]{}'
SPECIAL_KEYWORDS   = 'abstract', 'as', 'async', 'await', 'break', 'case', 'cast', 'catch', 'class', 'continue',\
    'default', 'do', 'else', 'enum', 'escape', 'extern', 'false', 'final', 'finally', 'for', 'from', 'funcdef',\
    'global', 'if', 'import', 'in', 'interface', 'is', 'mixin', 'mut', 'namespace', 'nonlocal', 'of', 'override',\
    'private', 'protected', 'return', 'static', 'struct', 'super', 'switch', 'this', 'throw', 'true', 'try', 'typedef',\
    'union', 'while', 'with', 'yield'
TYPE_KEYWORDS      = 'auto', 'bool', 'char', 'f32', 'f64', 'i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64', 'void'
UNUSED_SYMBOLS     = '#@`'


@dataclass
class Lexer:
    files: list[SourceFile]
    tokens: list[Token]

    def __init__(self, files: list[SourceFile], output_dir: str = ''):
        self.files      = files
        self.output_dir = output_dir

    def lex(self) -> None:
        self.tokens = []

        for file in self.files:
            file.tokens = []

            print(f'lexing "{file.path}"')

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
                        for char in '!%&*+-/<=>^|':  # TODO <<= >>=
                            if op == char and line.next() in char + '=':
                                line.take()
                                break
                        if op == ':' and line.next() == ':':
                            line.take()
                        self.tokens.append(Token('Operator', line))
                        file.tokens.append(self.tokens[-1])

                    elif line.next() in DIGIT_SYMBOLS:
                        while line.next() in NUMBER_SYMBOLS:
                            line.take()
                        taken = line.taken()
                        if taken[0] not in DIGIT_SYMBOLS:
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
                        self.tokens.append(Token('Number', line))
                        file.tokens.append(self.tokens[-1])

                    elif line.next() in PUNCTUATOR_SYMBOLS:
                        line.take()
                        self.tokens.append(Token('Punctuator', line))
                        file.tokens.append(self.tokens[-1])

                    elif line.next() in IDENTIFIER_SYMBOLS:
                        while line.next() in IDENTIFIER_SYMBOLS:
                            line.take()
                        taken = line.taken()
                        if taken in LOGIC_KEYWORDS:
                            self.tokens.append(Token('Operator', line))
                            file.tokens.append(self.tokens[-1])
                        elif taken in SPECIAL_KEYWORDS:
                            self.tokens.append(Token('Special', line))
                            file.tokens.append(self.tokens[-1])
                        elif taken in TYPE_KEYWORDS:
                            self.tokens.append(Token('Type', line))
                            file.tokens.append(self.tokens[-1])
                        else:
                            self.tokens.append(Token('Identifier', line))
                            file.tokens.append(self.tokens[-1])

                    else:
                        raise LexerError(
                            f'unexpected symbol {line.loc()}: "{line.next()}"'
                        )

            self.tokens.append(Token('Punctuator', line))
            file.tokens.append(self.tokens[-1])

    def write_debug(self) -> None:
        if not self.output_dir:
            raise LexerError('no output folder given')

        with open(os.path.join(self.output_dir, '2_lexer.cakedebug'), 'w', newline='\n') as f:
            f.write(debug_header(f'step 2: lexer'))
            f.write('tokens:\n')
            for file in self.files:
                f.write(f'    "{file.path}":\n')
                for token in file.tokens:
                    f.write(f'        {token}\n')


class LexerError(LanguageError):
    pass


@dataclass
class Token:
    kind:   str
    line:   Line
    locale: list[int]
    string: str

    def __init__(self, kind: str, line: Line):
        self.kind = kind
        self.line = line
        self.locale, self.string = line.new_locale()

        self.string = self.string or 'EOF'

    def __repr__(self) -> str:
        return f"{self.kind[0]}'{self.string}'"

    def has(self, *strings) -> bool:
        return self.string in strings

    def loc(self) -> str:
        return f'("{self.line.file.path}", line {self.line.num}, column {self.locale[0] + 1})'

    def of(self, *kinds) -> bool:
        return self.kind in kinds

    def tree_repr(self, _) -> str:
        return repr(self)
