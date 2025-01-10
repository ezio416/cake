# c 2025-01-07
# m 2025-01-09

from lexing.lexing import LexerError
from lexing.token import Token


class ParserError(LexerError):
    def __init__(self, component, message: str):
        super().__init__(component, message, component.locale[0])


class NodeMaker():
    def __init__(self, tokens: list[Token]):
        self.tokens: list[Token] = tokens
        self.locale: list[int]   = [0, 0]
        self.nodes:  list[Node]  = []

    def build(self) -> None:
        print('build NodeMaker')

        for node in self.nodes:
            node.build()

    def finished(self) -> bool:
        return self.locale[1] >= len(self.tokens)

    def ignore(self) -> None:
        self.locale[0] = self.locale[1]

    def make_class(self):
        self.take()

        next: Token = self.next()
        if next is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.of('Identifier'):
            raise ParserError(next, 'expected identifier')
        self.take()

        if (next := self.next()) is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.of('Punctuator') or not next.has('{'):
            raise ParserError(next, 'expected "{"')
        self.take()
        open_brace: int = 1
        open_brack: int = 0
        open_paren: int = 0

        while open_brace:
            if (next := self.next()) is None:
                raise ParserError(self.taken()[0], 'dangling class')

            if next.has('EOF'):
                raise ParserError(next, 'unexpected end of file')

            if next.has('class'):
                raise ParserError(next, 'nested classes are not supported')

            if next.of('Punctuator'):
                if next.has('{'):
                    open_brace += 1
                elif next.has('}'):
                    open_brace -= 1
                elif next.has('['):
                    open_brack += 1
                elif next.has(']'):
                    open_brack -= 1
                elif next.has('('):
                    open_paren += 1
                elif next.has(')'):
                    open_paren -= 1

            self.take()  # need logic for everything in a class

        if open_brack:
            for token in reversed(self.taken()):
                if token.has('['):
                    raise ParserError(token, 'dangling brackets')
            raise ParserError(self.taken()[0], 'dangling brackets')

        if open_paren:
            for token in reversed(self.taken()):
                if token.has('('):
                    raise ParserError(token, 'dangling parentheses')
            raise ParserError(self.taken()[0], 'dangling parentheses')

        return Class(self.new_locale())

    def make_conditional(self):
        pass

    def make_enum(self):
        self.take()

        next: Token = self.next()
        if next is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.of('Identifier'):
            raise ParserError(next, 'expected identifier')
        self.take()

        if (next := self.next()) is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.of('Punctuator') or not next.has('{'):
            raise ParserError(next, 'expected "{"')
        self.take()
        open_brace: int = 1

        while open_brace:
            if (next := self.next()) is None:
                raise ParserError(self.taken()[0], 'dangling enum')

            if next.has('EOF'):
                raise ParserError(next, 'unexpected end of file')

            if next.has('enum'):
                raise ParserError(next, 'nested enums are not supported')

            if next.of('Operator') and not next.has('='):
                raise ParserError(next, 'operators are not supported')

            if next.of('Punctuator'):
                if next.has('}'):
                    open_brace -= 1
                elif next.has(',', '='):
                    pass
                else:
                    raise ParserError(next, 'unexpected symbol in enum')

            self.take()  # need logic for everything in an enum

        return Enum(self.new_locale())

    def make_expression(self):
        pass

    def make_expression_primary(self):
        pass

    def make_expression_unary(self):
        pass

    def make_function(self):
        self.take()

        next: Token = self.next()
        if next is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.of('Identifier'):
            raise ParserError(next, 'expected identifier')
        self.take()

        if (next := self.next()) is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if next.has('=', ';'):
            raise ParserError(next, 'globals are not allowed')
        if not next.has('('):
            raise ParserError(next, 'expected "("')
        self.take()

        while True:
            if (next := self.next()) is None or next.has('EOF'):
                raise ParserError(self.taken()[0], 'unexpected end of file')
            self.take()
            if next.has(')'):
                break

        if (next := self.next()) is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if next.has(';'):
            raise ParserError(next, 'function definition required')
        if not next.has('{'):
            raise ParserError(next, 'expected "{"')
        self.take()
        open_brace: int = 1
        open_brack: int = 0
        open_paren: int = 0

        while open_brace:
            if (next := self.next()) is None:
                raise ParserError(self.taken()[0], 'dangling function')

            if next.has('EOF'):
                raise ParserError(next, 'unexpected end of file')

            if next.of('Punctuator'):
                if next.has('{'):
                    open_brace += 1
                elif next.has('}'):
                    open_brace -= 1
                elif next.has('['):
                    open_brack += 1
                elif next.has(']'):
                    open_brack -= 1
                elif next.has('('):
                    open_paren += 1
                elif next.has(')'):
                    open_paren -= 1

            self.take()  # need logic for everything in a function

        if open_brack:
            for token in reversed(self.taken()):
                if token.has('['):
                    raise ParserError(token, 'dangling brackets')
            raise ParserError(self.taken()[0], 'dangling brackets')

        if open_paren:
            for token in reversed(self.taken()):
                if token.has('('):
                    raise ParserError(token, 'dangling parentheses')
            raise ParserError(self.taken()[0], 'dangling parentheses')

        return Function(self.new_locale())

    def make_namespace(self):
        self.take()

        next: Token = self.next()
        if next is None or next.has('EOF'):
            raise ParserError(next, 'unexpected end of file')
        if not next.of('Identifier'):
            raise ParserError(next, 'expected identifier')
        self.take()

        if (next := self.next()) is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.has('{'):
            raise ParserError(next, 'expected "{"')
        self.take()
        open_brace: int = 1
        open_brack: int = 0
        open_paren: int = 0

        while open_brace:
            if (next := self.next()) is None:
                raise ParserError(self.taken()[0], 'dangling namespace')

            if next.has('EOF'):
                raise ParserError(next, 'unexpected end of file')

            if next.has('namespace'):
                raise ParserError(next, 'nested namespaces are not supported')

            if next.of('Punctuator'):
                if next.has('{'):
                    open_brace += 1
                elif next.has('}'):
                    open_brace -= 1
                elif next.has('['):
                    open_brack += 1
                elif next.has(']'):
                    open_brack -= 1
                elif next.has('('):
                    open_paren += 1
                elif next.has(')'):
                    open_paren -= 1

            self.take()  # need logic for everything in a namespace

        if open_brack:
            for token in reversed(self.taken()):
                if token.has('['):
                    raise ParserError(token, 'dangling brackets')
            raise ParserError(self.taken()[0], 'dangling brackets')

        if open_paren:
            for token in reversed(self.taken()):
                if token.has('('):
                    raise ParserError(token, 'dangling parentheses')
            raise ParserError(self.taken()[0], 'dangling parentheses')

        return Namespace(self.new_locale())

    def make_statement(self):
        self.take()

        while True:
            next: Token = self.next()
            if next is None or next.has('EOF'):
                raise ParserError(self.taken()[0], 'unexpected end of file')
            if next.has(';'):
                break

        node = Node('Statement', self.new_locale())
        return node

    def make_struct(self):
        self.take()

        next: Token = self.next()
        if next is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.of('Identifier'):
            raise ParserError(next, 'expected identifier')
        self.take()

        if (next := self.next()) is None or next.has('EOF'):
            raise ParserError(self.taken()[0], 'unexpected end of file')
        if not next.of('Punctuator') or not next.has('{'):
            raise ParserError(next, 'expected "{"')
        self.take()
        open_brace: int = 1
        open_brack: int = 0
        open_paren: int = 0

        while open_brace:
            if (next := self.next()) is None:
                raise ParserError(self.taken()[0], 'dangling struct')

            if next.has('EOF'):
                raise ParserError(next, 'unexpected end of file')

            if next.has('struct'):
                raise ParserError(next, 'nested structs are not supported')

            if next.of('Punctuator'):
                if next.has('{'):
                    open_brace += 1
                elif next.has('}'):
                    open_brace -= 1
                elif next.has('['):
                    open_brack += 1
                elif next.has(']'):
                    open_brack -= 1
                elif next.has('('):
                    open_paren += 1
                elif next.has(')'):
                    open_paren -= 1

            self.take()  # need logic for everything in a struct

        if open_brack:
            for token in reversed(self.taken()):
                if token.has('['):
                    raise ParserError(token, 'dangling brackets')
            raise ParserError(self.taken()[0], 'dangling brackets')

        if open_paren:
            for token in reversed(self.taken()):
                if token.has('('):
                    raise ParserError(token, 'dangling parentheses')
            raise ParserError(self.taken()[0], 'dangling parentheses')

        return Struct(self.new_locale())

    def new_locale(self) -> tuple[list[int], list[Token]]:
        locale: list[int]   = self.locale.copy()
        taken:  list[Token] = self.taken()
        self.ignore()
        return locale, taken

    def next(self) -> Token | None:
        return None if self.finished() else self.tokens[self.locale[1]]

    def skip(self) -> None:
        self.take()
        self.ignore()

    def take(self) -> Token:
        token: Token = self.next()
        self.locale[1] += 0 if self.finished() else 1
        return token

    def taken(self) -> list[Token]:
        return self.tokens[self.locale[0]:self.locale[1]] if len(self.tokens) else []


class Node(NodeMaker):
    def __init__(self, kind: str, locale: tuple[list[int], list[Token]]):
        super().__init__(locale[1])
        self.kind: str       = kind
        self.pos:  list[int] = locale[0]

        if len(kind) < 3:
            raise ValueError(f'kind is too short: {kind}')

    def __repr__(self) -> str:
        # return f"{self.kind[:3].upper()}'{self.tokens[1].string}'"
        return f"{type(self).__name__} '{self.tokens[1].string}'"


class Class(Node):
    def __init__(self, locale: tuple[list[int], list[Token]]):
        super().__init__('Class', locale)

    def build(self) -> None:
        print('build class')

        for node in self.nodes:
            node.build()


class Enum(Node):
    def __init__(self, locale: tuple[list[int], list[Token]]):
        super().__init__('Enum', locale)

    def build(self) -> None:  # just validation
        for _ in range(3):  # "enum", identifier, "{"
            self.skip()

        next: Token | None = None
        while not (next := self.next()).has('}'):
            if not len(self.taken()):
                self.take()
            else:
                match self.taken()[-1].kind[0]:  # previous token
                    case 'I':  # identifier
                        if not next.has(*',='):
                            raise ParserError(next, 'expected "," or "="')
                        self.take()

                    case 'N':  # number
                        if not next.has(','):
                            raise ParserError(next, 'expected ","')
                        self.take()

                    case 'O':  # operator: "="
                        if not next.of('Number'):
                            raise ParserError(next, 'expected number')
                        if '.' in next.string:
                            raise ParserError(next, 'floating point numbers are not supported')
                        self.take()

                    case 'P':  # punctuator: ","
                        if not next.of('Identifier'):
                            raise ParserError(next, 'expected identifier')
                        self.take()

                    case _:
                        raise ParserError(next, 'unexpected token')


class Function(Node):
    def __init__(self, locale: tuple[list[int], list[Token]]):
        super().__init__('Function', locale)

    def build(self) -> None:
        print('build function')

        for node in self.nodes:
            node.build()


class Namespace(Node):
    def __init__(self, locale: tuple[list[int], list[Token]]):
        super().__init__('Namespace', locale)

    def build(self) -> None:
        print('build namespace')

        for node in self.nodes:
            node.build()


class Struct(Node):
    def __init__(self, locale: tuple[list[int], list[Token]]):
        super().__init__('Struct', locale)

    def build(self) -> None:
        print('build struct')

        for node in self.nodes:
            node.build()
