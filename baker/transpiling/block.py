# c 2025-01-07
# m 2025-01-10

from util.error import LanguageError


class TranspilerError(LanguageError):
    def __init__(self, component, message):
        super().__init__(component, message)


class Block:
    def __init__(self, node):
        self.node       = node
        self.c:    str  = ''
        self.h:    str  = ''

        match node.kind[0]:
            case 'E':
                self.t_enum()
            case _:
                pass

    def t_enum(self) -> None:  # header only
        self.h += f'typedef enum {{\n'

        for token in self.node.tokens[3:]:
            match token.kind[0]:
                case 'I':
                    self.h += '    ' + token.string
                case 'N':
                    self.h += token.string
                case 'O':
                    self.h += ' ' + token.string + ' '
                case 'P':
                    if token.has('}'):
                        break
                    self.h += token.string + '\n'
                case _:
                    raise TranspilerError(token, 'unexpected token')

        self.h = f'{self.h.rstrip(',\n')}\n}} {self.node.tokens[1].string};'
