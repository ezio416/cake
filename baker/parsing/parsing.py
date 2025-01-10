# c 2025-01-07
# m 2025-01-09

from lexing.keywords import *
from lexing.token import Token
from .node import Node, NodeMaker, ParserError


class Parser(NodeMaker):
    def __init__(self, tokens: list[Token]):
        super().__init__(tokens)

        self.classes:    dict[Node] = {}
        self.enums:      dict[Node] = {}
        self.functions:  dict[Node] = {}
        self.namespaces: dict[Node] = {}
        self.structs:    dict[Node] = {}

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
            match node.kind[0]:
                case 'C':
                    if node.tokens[1].string in self.classes:
                        raise ParserError(node, 'class already defined')
                    self.classes[node.tokens[1].string] = node

                case 'E':
                    if node.tokens[1].string in self.enums:
                        raise ParserError(node, 'enum already defined')
                    self.enums[node.tokens[1].string] = node

                case 'F':
                    if node.tokens[1].string in self.functions:
                        raise ParserError(node, 'function already defined')
                    self.functions[node.tokens[1].string] = node

                case 'N':
                    if node.tokens[1].string in self.namespaces:
                        raise ParserError(node, 'namespace already defined')
                    self.namespaces[node.tokens[1].string] = node

                case 'S':
                    if node.tokens[1].string in self.structs:
                        raise ParserError(node, 'struct already defined')
                    self.structs[node.tokens[1].string] = node

                case _:
                    raise ParserError(node, 'unexpected token')

            node.build()
