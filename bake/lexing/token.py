# c 2025-01-02
# m 2025-01-04

class Token:
    def __init__(self, line, kind: str):
        self.line      = line
        self.kind: str = kind

        self.locale, self.text = line.new_locale()

        self.text = self.text or 'EOF'

    def __repr__(self) -> str:
        return f"{self.kind[0]}'{self.text}'"

    def mark(self) -> None:
        self.line.mark(self)
