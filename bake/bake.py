# c 2025-01-02
# m 2025-01-02

import json
import os


code: list[str] = []
proj: dict      = {}


def read(path: str) -> list[str]:
    global code, proj
    code = []
    raw: list[str] = []

    os.chdir(path)

    for _, _, files in os.walk('.'):
        for file in files:
            if file == 'cake.json':
                with open(f'{path}/{file}') as f:
                    proj = json.load(f)

            elif file.endswith('.cake'):
                with open(f'{path}/{file}') as f:
                    for line in f:
                        raw.append(line)

    for line in raw:
        if line in ('', '\n'):
            continue

        if line.endswith('\n'):
            line = line[:-1]

        code.append(line.strip())


def main() -> None:
    dir: str = f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace('\\', '/')}/example'
    read(dir)

    pass


if __name__ == '__main__':
    main()
