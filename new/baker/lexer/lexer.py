from dataclasses import dataclass

import reader


__all__ = [
    'LexerError',
    'Token'
]


class LexerError(Exception):
    pass


@dataclass
class Token:
    ...

    def __init__(self):
        pass
