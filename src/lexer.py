from dataclasses import dataclass
import os

from .reader import Line, SourceFile
from .util import LanguageError, debug_header


DIGIT_SYMBOLS      = '0123456789'
IDENTIFIER_SYMBOLS = '$0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
LOGIC_KEYWORDS     = 'and', 'nand', 'nor', 'not', 'or', 'xnor', 'xor'
NUMBER_SYMBOLS     = "'-.0123456789ABCDEFabcdefox"
OPERATOR_SYMBOLS   = '!#%&*+-./:<=>?@^|'
PUNCTUATOR_SYMBOLS = r'"\'(),;[]{}'
SPECIAL_KEYWORDS   = 'abstract', 'actually', 'alias', 'as', 'async', 'await', 'break', 'case', 'cast', 'catch',\
    'class', 'continue', 'default', 'del', 'do', 'else', 'enum', 'extern', 'false', 'final', 'finally', 'for', 'from',\
    'if', 'import', 'in', 'interface', 'is', 'mut', 'namespace', 'of', 'override', 'private', 'property', 'protected',\
    'return', 'static', 'struct', 'super', 'switch', 'this', 'throw', 'true', 'try', 'union', 'while', 'with', 'yield'
TYPE_KEYWORDS      = 'auto', 'bool', 'char', 'f32', 'f64', 'i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64', 'void'
UNUSED_SYMBOLS     = '`~'


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
                def check_number(num: str):
                    if num[0] not in DIGIT_SYMBOLS:
                        raise LexerError(f'numbers must start with a digit {line.loc()}: "{num}"')

                    if num.count('.') > 1:
                        raise LexerError(f'numbers can have a maximum of one decimal point {line.loc()}: "{num}"')

                    if num[0] == '0':
                        if len(num) > 1:
                            if num[1] == 'b':
                                if len(num) == 2:
                                    raise LexerError(f'invalid binary number {line.loc()}: "{num}"')
                                for char in num[2:]:
                                    if char not in "'01":
                                        raise LexerError(f'invalid binary number {line.loc()}: "{num}"')
                            elif num[1] == 'o':
                                if len(num) == 2:
                                    raise LexerError(f'invalid octal number {line.loc()}: "{num}"')
                                for char in num[2:]:
                                    if char not in "'01234567":
                                        raise LexerError(f'invalid octal number {line.loc()}: "{num}"')
                            elif num[1] == 'x':
                                if len(num) == 2:
                                    raise LexerError(f'invalid hexadecimal number {line.loc()}: "{num}"')
                                for char in num[2:]:
                                    if char not in "'0123456789ABCDEFabcdef":
                                        raise LexerError(f'invalid hexadecimal number {line.loc()}: "{num}"')

                    elif 'e' in num:
                        if num.count('e') > 1 or num.startswith('e') or num.endswith('e'):
                            raise LexerError(f'invalid scientific number {line.loc()}: "{num}"')
                        coef, exp = num.split('e')
                        if '-' in coef or ('-' in exp and (not exp.startswith('-') or exp.count('-') > 1)):
                            raise LexerError(f'invalid scientific number {line.loc()}: "{num}"')
                        for char in exp:
                            if char not in DIGIT_SYMBOLS + '-':
                                raise LexerError(f'invalid scientific number {line.loc()}: "{num}"')

                def make_string() -> bool:
                    if line.take() != '"':
                        return False

                    while line.next().isascii():
                        if line.next() == '\\':
                            line.take()
                            if line.next() in '"bfnrtv':
                                line.take()
                            elif line.next() == 'U':
                                line.take()
                                for _ in range(8):
                                    if line.next().lower() in '0123456789abcdef':
                                        line.take()
                                    else:
                                        break
                            elif line.next() == 'u':
                                line.take()
                                for _ in range(4):
                                    if line.next().lower() in '0123456789abcdef':
                                        line.take()
                                    else:
                                        break
                            elif line.next() == 'x':
                                line.take()
                                for _ in range(2):
                                    if line.next().lower() in '0123456789abcdef':
                                        line.take()
                                    else:
                                        break
                            elif line.next() in '01234567':
                                line.take()
                                for _ in range(2):
                                    if line.next() in '01234567':
                                        line.take()
                                    else:
                                        break
                            else:
                                raise LexerError(
                                    f'unexpected escape sequence in string literal {line.loc()}: "{line.next()}"'
                                )
                        elif line.next() == '"':
                            line.take()
                            break
                        elif line.finished():
                            raise LexerError(f'unterminated string literal {line.loc()}: {line.taken()}')
                        else:
                            line.take()

                    if not line.taken().endswith('"'):
                        raise LexerError(f'unterminated string literal {line.loc()}: {line.taken()}')

                    self.tokens.append(Token('String', line))
                    file.tokens.append(self.tokens[-1])

                    return True

                while not line.finished():
                    line.ignore_spaces()

                    if line.finished():
                        break

                    if line.next() in OPERATOR_SYMBOLS:
                        op = line.take()
                        if op == '#' and not make_string():
                            raise LexerError(
                                f'unexpected symbol in string literal {line.loc()}: "{line.taken()[-1]}"'
                            )
                        if op == '/' and line.next() == '/':
                            line.take()
                            line.ignore()
                            line.ignore_spaces()
                            while not line.finished():
                                line.comment += line.take()
                            break
                        if op == '.' and line.next() == '.':
                            line.take()
                            if line.next() == '.':
                                line.take()
                                self.tokens.append(Token('Ellipses', line))
                                file.tokens.append(self.tokens[-1])
                                continue
                            elif line.next() == '=':
                                line.take()
                        else:
                            took = False
                            if op == '!':
                                if line.next() in '&^|':
                                    line.take()
                                    if line.next() == '=':
                                        line.take()
                                        took = True
                            if op in '!%/=' and line.next() == '=':
                                line.take()
                                took = True
                            if not took:
                                for char in '&*+-^|':
                                    if op == char:
                                        if line.next() == '=':
                                            line.take()
                                        elif line.next() == char:
                                            line.take()
                                            if op in '&*^|' and line.next() == '=':
                                                line.take()
                                        break

                        self.tokens.append(Token('Operator', line))
                        file.tokens.append(self.tokens[-1])

                    elif line.next() in DIGIT_SYMBOLS:
                        while line.next() in NUMBER_SYMBOLS:
                            line.take()
                            if line.taken().endswith('..'):
                                line.untake(2)
                                check_number(line.taken())
                                self.tokens.append(Token('Number', line))
                                file.tokens.append(self.tokens[-1])
                                line.take()
                                line.take()
                                if line.next() == '=':
                                    line.take()
                                self.tokens.append(Token('Operator', line))
                                file.tokens.append(self.tokens[-1])
                                while line.next() in NUMBER_SYMBOLS:
                                    line.take()
                                break

                        check_number(line.taken()[0])

                        self.tokens.append(Token('Number', line))
                        file.tokens.append(self.tokens[-1])

                    elif line.next() in PUNCTUATOR_SYMBOLS:
                        if not make_string():
                            self.tokens.append(Token('Operator', line))
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
                            dollars = taken.count('$')
                            if dollars > 1:
                                raise LexerError(f'too many of "$" in identifier {line.loc()}: "{line.next()}"')
                            if dollars and not taken.startswith('$'):
                                raise LexerError(f'special identifier must start with "$" {line.loc()}: "{line.next()}"')
                            self.tokens.append(Token('Identifier', line))
                            file.tokens.append(self.tokens[-1])

                    else:
                        raise LexerError(
                            f'unexpected symbol {line.loc()}: "{line.next()}"'
                        )

            self.tokens.append(Token('EOF', line))
            file.tokens.append(self.tokens[-1])

    def write_debug(self) -> None:
        if not self.output_dir:
            raise LexerError('no output folder given')

        with open(os.path.join(self.output_dir, '2_lexer.cakedebug'), 'w', newline='\n') as f:
            f.write(debug_header('step 2: lexer'))
            f.write('tokens:\n')
            for file in self.files:
                f.write(f'\t"{file.path}":\n')
                for token in file.tokens:
                    f.write(f'\t\t{token}\n')


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
        if self.line:
            self.locale, self.string = line.new_locale()
            self.string = self.string or 'EOF'
        else:
            self.string = 'EOF'

    def __repr__(self) -> str:
        return f"{self.kind[0]}'{self.string}'"

    def has(self, *strings: str) -> bool:
        return self.string in strings

    def loc(self) -> str:
        return f'"{self.line.file.path}", line {self.line.num}, column {self.locale[0] + 1}'

    def of(self, *kinds: str) -> bool:
        return self.kind in kinds

    def of_has(self, of: str, has: str) -> bool:
        return self.of(of) and self.has(has)

    def type_starter(self, mut: bool = True) -> bool:
        return self.of('Identifier', 'Type') or mut and self.of_has('Special', 'mut')

    def tree_repr(self, _) -> str:
        return repr(self)
