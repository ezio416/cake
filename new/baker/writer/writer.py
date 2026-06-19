import os

import transpiler


__all__ = [
    'WriterError'
]


OUTPUT_FILE_NAME = 'main.cake.c'


class WriterError(Exception):
    pass
