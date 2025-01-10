# c 2025-01-02
# m 2025-01-04

class Token:
    def __init__(self, line, kind: str):
        self.line      = line
        self.kind: str = kind

        self.locale, self.string = line.new_locale()

        self.string = self.string or 'EOF'

    def __repr__(self) -> str:
        return f"{self.kind[0]}'{self.string}'"

    def has(self, *strings: str) -> bool:
        return self.string in strings

    def mark(self) -> None:
        self.line.mark(self)

    def of(self, *kinds: str) -> bool:
        return self.kind in kinds

    def tree_repr(self, _) -> str:
        return repr(self)
