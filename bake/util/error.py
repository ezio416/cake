# c 2025-01-02
# m 2025-01-04

class LanguageError(RuntimeError):
    def __init__(self, component, message: str):
        component.mark()
        self.line = component.line
        self.message: str = message

    def __str__(self) -> str:
        return f'{self.line.get_marks()}\n{type(self).__name__}: {self.message}'
