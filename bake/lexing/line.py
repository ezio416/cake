# c 2025-01-04
# m 2025-01-04

class Line:
    def __init__(self, filename: str, lineno: int, text: str):
        self.filename: str = filename
        self.lineno:   int = lineno

        self.text: str = text
        if self.text.endswith('\n'):
            self.text = self.text[:-1]

        self.locale: list[int]  = [0, 0]
        self.marked: list[int]  = [len(self.text), -1]

    def __repr__(self) -> str:
        return f'{type(self)} {self.filename} {self.lineno}'

    def finished(self) -> bool:
        return self.locale[1] >= len(self.text)

    def get_marks(self) -> str:
        marks: str = '  '

        for i in range(len(self.text) + 1):
            between = self.marked[0] <= i < self.marked[1]
            marks += '^' if between or self.marked[0] == i else ' '

        return marks

    def ignore(self) -> None:
        self.locale[0] = self.locale[1]

    def mark(self, token) -> None:
        self.marked[0] = min(self.marked[0], token.locale[0])
        self.marked[1] = max(self.marked[1], token.locale[1])

    def new_locale(self) -> tuple[list[int], str]:
        locale: list[int] = self.locale.copy()
        taken:  str       = self.taken()
        self.ignore()
        return locale, taken

    def next(self) -> str:
        return 'EOF' if self.finished() else self.text[self.locale[1]]

    def take(self) -> str:
        symbol: str = self.next()
        self.locale[1] += 0 if self.finished() else 1
        return symbol

    def taken(self) -> str:
        return self.text[self.locale[0]:self.locale[1]]
