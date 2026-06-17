import os

import reader, lexer, parser, transpiler, writer


def main() -> None:
    test_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test')

    config = reader.read_config(test_folder)
    source = reader.read_source(test_folder)

    pass


if __name__ == '__main__':
    main()
