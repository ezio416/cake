# c 2025-01-07
# m 2025-01-09

from lexing.keywords import *
from lexing.token import Token
from .node import NodeMaker, ParserError


class Parser(NodeMaker):
    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)
        self.build()

    def build(self) -> None:
        next: Token | None = None

        while True:
            if (next := self.next()) is None:
                break

            if next.has('EOF'):
                self.skip()
                continue

            if next.of('Identifier'):
                self.nodes.append(self.make_function())

            elif next.of('Keyword'):
                if next.has('class'):
                    self.nodes.append(self.make_class())

                elif next.has('enum'):
                    self.nodes.append(self.make_enum())

                elif next.has('namespace'):
                    self.nodes.append(self.make_namespace())

                elif next.has('struct'):
                    self.nodes.append(self.make_struct())

                elif next.has(*PRIMITIVE_KEYWORDS) or next.string.startswith(('dec', 'flt', 'int', 'str')):
                    self.nodes.append(self.make_function())

                else:
                    raise ParserError(next, 'unexpected token')

            else:
                raise ParserError(next, 'unexpected token')

        for node in self.nodes:
            node.build()
