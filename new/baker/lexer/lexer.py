from dataclasses import dataclass
# from enum import Enum

import reader


__all__ = [
    'LexerError',
    'Token',
    # 'TokenType',
    'tokenize'
]


class LexerError(Exception):
    pass


@dataclass
class Token:
    line:   reader.Line
    locale: list[int]
    text:   str
    # type:   TokenType
    type:   str

    def __init__(self, line: reader.Line):
        self.line = line
        ...


# class TokenType(Enum):
#     DATA_TYPE  = 0
#     IDENTIFIER = 1
#     PUNCTUATOR = 2
#     RETURN     = 3


def tokenize(source: list[reader.SourceFile]) -> list[Token]:
    ret: list[Token] = []

    for file in source:
        for line in file.lines:
            # for char in line.text:
            #     if char.isalpha():
            #         ...

            #     else:
            #         raise LexerError(
            #             f'unexpected character at {file.path},{line.lineno},{line.locale[0]}: "{char}"'
            #         )

            ...
            pass

    return ret
