# c 2025-01-02
# m 2025-01-02

import json
import os


def main() -> None:
    dir: str       = f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace('\\', '/')}/example'
    raw: list[str] = []

    os.chdir(dir)

    for _, _, files in os.walk('.'):
        for file in files:
            if not file.endswith('.cake'):
                continue

            with open(f'{dir}/{file}') as f:
                for line in f:
                    raw.append(line)

    code: list[str] = []

    for line in raw:
        if line not in ('', '\n'):
            if line.endswith('\r'):
                line = line[:-1]
            if line.endswith('\n'):
                line = line[:-1]

            code.append(line.strip())

    pass


if __name__ == '__main__':
    main()
