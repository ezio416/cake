from abc import ABC
from dataclasses import dataclass
import os

from ..lexer import Token
from ..util import LanguageError, debug_header


@dataclass
class Node(ABC):
    index:  int
    name:   Identifier | str
    parent: Node | None
    tokens: list[Token]

    @property
    def path(self) -> str:
        if self.name == 'global':
            return 'global'
        if not self.parent:
            return f'global.{self.name}'
        return f'{self.parent.path}.{self.name}'

    def __init__(self, tokens: list[Token] = [], name: Identifier | str = '', parent: Node = None):
        self.tokens = tokens
        self.name   = name
        self.parent = parent

        self.index  = 0

    def next(self) -> Token:
        return self.tokens[self.index]

    def take(self) -> Token:
        token = self.next()
        if not (token.of('Punctuator') and token.has('EOF')):
            self.index += 1
        return token

    def take_specific(self, of: str, has: str) -> tuple[Token]:
        if self.next().of(of) and self.next().has(has):
            return self.take(),
        return ()


@dataclass
class Inheritable(Node, ABC):
    abstract:    bool
    final:       bool
    inheritance: list[Inheritable]

    def __init__(self, tokens: list[Token], name: Identifier, parent: Namespace):
        super().__init__(tokens, name, parent)
        self.abstract    = False
        self.final       = False
        self.inheritance = []


@dataclass
class Accessor(Node):
    parts: list[Identifier | Type]

    def __init__(self, tokens: list[Token] = [], parent: Node = None):
        super().__init__(tokens, parent=parent)

        self.parts = []

        for token in self.tokens:
            if token.of('Identifier', 'Type'):
                self.name += token.string
                if token.of('Identifier'):
                    self.parts.append(Identifier(token))
                else:
                    self.parts.append(Type(token))
            elif token.of('Operator') and token.has('.'):
                self.name += token.string
            else:
                raise ParserError(token, 'unexpected token in accessor')


@dataclass
class Alias(Node):
    old: Accessor

    def __init__(self, old: list[Token], name: Token, parent: Node):
        if not old or not name:
            raise LanguageError('alias missing token')

        super().__init__(old, Identifier(name), parent)
        self.old = Accessor(old, parent.parent)

    def __repr__(self) -> str:
        return f'Alias["{self.old.path}" -> "{self.path}"]'


@dataclass
class Class(Inheritable):
    def __init__(self, tokens: list[Token], name: Token, parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)
        ...


@dataclass
class Declaration(Node):
    def __init__(self, tokens: list[Token], name: Token, parent: Node):
        super().__init__(tokens, Identifier(name), parent)
        ...


@dataclass
class Enum(Node):
    elements: list[EnumElement]

    def __init__(self, elements: list[EnumElement], name: Token, parent: Namespace):
        super().__init__([], Identifier(name), parent)
        self.elements = elements
        for e in self.elements:
            e.parent = self

    def __repr__(self) -> str:
        return f'Enum["{self.path}" {self.elements}]'


@dataclass
class EnumElement(Node):
    value: int

    def __init__(self, name: Token, value: int = 0):
        super().__init__(name=Identifier(name))
        self.value = value

    def __repr__(self) -> str:
        return f'{self.name}={self.value}'


@dataclass
class Function(Node):
    def __init__(self, tokens: list[Token], name: Token, parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)
        ...


@dataclass
class Identifier:
    token: Token

    def __init__(self, token: Token):
        if not token.of('Identifier'):
            raise ParserError(token, 'expected Identifier')
        self.token = token

    def __repr__(self) -> str:
        return self.token.string

    def __str__(self) -> str:
        return self.token.string


@dataclass
class Interface(Inheritable):
    def __init__(self, tokens: list[Token], name: Token, parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)
        ...


@dataclass
class Member(Node):
    def __init__(self, tokens: list[Token], name: Token, parent: Class | Struct):
        super().__init__(tokens, Identifier(name), parent)
        ...


@dataclass
class Method(Node):
    def __init__(self, tokens: list[Token], name: Token, parent: Class | Interface):
        super().__init__(tokens, Identifier(name), parent)
        ...


@dataclass
class Namespace(Node):
    aliases:      list[Alias]
    classes:      list[Class]
    declarations: list[Declaration]
    enums:        list[Enum]
    functions:    list[Function]
    interfaces:   list[Interface]
    namespaces:   list[Namespace]
    structs:      list[Struct]

    def __init__(self, tokens: list[Token], name: Identifier | str, parent: Namespace = None):
        super().__init__(tokens, name, parent)

        self.aliases      = []
        self.classes      = []
        self.declarations = []
        self.enums        = []
        self.functions    = []
        self.interfaces   = []
        self.namespaces   = []
        self.structs      = []

        if self.name == 'global':
            self.namespaces.append(StdNamespace(self))

        if not self.tokens:
            return

        while not ((next := self.next()).of('Punctuator') and next.has('EOF')):
            if next.of('Special'):
                if next.has('alias'):
                    self.make_alias()
                # elif next.has('class'):
                #     self.make_class()
                elif next.has('enum'):
                    self.make_enum()
                # elif next.has('interface'):
                #     self.make_interface()
                elif next.has('namespace'):
                    self.make_namespace()
                # elif next.has('struct'):
                #     self.make_struct()
                # elif next.has('abstract', 'final'):
                #     self.take()
                #     match self.next().string:
                #         case 'class':
                #             self.make_class()
                #             pass
                #         case 'interface':
                #             self.make_interface()
                #             pass
                #         case 'struct':
                #             self.make_struct()
                #             pass
                else:
                    print(self.take().loc(), 'warning: unexpected special keyword')

            else:
                print(self.take().loc(), 'warning: unexpected token')

    def __getitem__(self, key: str) -> Node | None:
        for a in self.aliases:
            if key == a.name:
                return a
        for c in self.classes:
            if key == c.name:
                return c
        for d in self.declarations:
            if key == d.name:
                return d
        for e in self.enums:
            if key == e.name:
                return e
        for f in self.functions:
            if key == f.name:
                return f
        for i in self.interfaces:
            if key == i.name:
                return i
        for n in self.namespaces:
            if key == n.name:
                return n
        for s in self.structs:
            if key == s.name:
                return s
        return None

    def make_alias(self):
        self.take()  # 'alias'

        old = []
        if self.next().of('Identifier', 'Type'):
            old = self.take()
            if self.next().of('Identifier'):
                new = self.take()
                if self.take_specific('Punctuator', ';'):
                    self.aliases.append(Alias([old], new, self))
                    return

        raise ParserError(self.next(), 'bad alias statement')

    def make_class(self):
        if self.next().of('Special') and self.next().has('abstract', 'final'):
            modifier = self.take()

        if self.next().of('Special') and self.next().has('class'):
            self.take()

        ...

    def make_declaration(self):
        ...

    def make_enum(self):
        self.take()  # 'enum'

        if self.next().of('Identifier'):
            name = self.take()
            if self.take_specific('Punctuator', '{'):
                elements: list[EnumElement] = []
                prev_value = -1
                while True:
                    if (next := self.next()).of('Identifier'):
                        element_name = self.take()
                        if self.take_specific('Punctuator', ','):
                            elements.append(EnumElement(element_name))
                            prev_value += 1
                        elif self.take_specific('Punctuator', '}'):
                            elements.append(EnumElement(element_name))
                            break
                        elif self.take_specific('Operator', '='):
                            if self.next().of('Number'):
                                value = int(self.take().string)
                                prev_value = value
                                elements.append(EnumElement(element_name, value))
                            self.take_specific('Punctuator', ',')
                        else:
                            raise ParserError(next, 'unexpected token in enum')
                    elif self.take_specific('Punctuator', '}'):
                        break
                    else:
                        raise ParserError(next, 'unexpected token in enum')

                self.enums.append(Enum(elements, name, self))
                return

        raise ParserError(self.next(), 'bad enum definition')

    def make_function(self):
        ...

    def make_interface(self):
        ...

    def make_namespace(self):
        self.take()  # 'namespace'

        if self.next().of('Identifier'):
            name = self.take()
            if self.take_specific('Puntuator', '{'):
                stack = 1
                tokens = []
                while stack:
                    next = self.next()
                    if next.of('Punctuator'):
                        if next.has('EOF'):
                            raise ParserError(next, 'unexpected EOF')
                        elif next.has('{'):
                            stack += 1
                        elif next.has('}'):
                            stack -= 1
                    tokens.append(self.take())
                self.namespaces.append(Namespace(tokens + [Token('Punctuator', None)], Identifier(name), self))

    def make_struct(self):
        ...


class BareNamespace(Namespace):
    def __init__(self, name: Identifier | str, parent: Namespace = None):
        super().__init__([], name, parent)


@dataclass
class StdNamespace(BareNamespace):
    def __init__(self, parent: Namespace = None):
        super().__init__('std', parent)


@dataclass
class Struct(Inheritable):
    def __init__(self, tokens: list[Token], name: Identifier, parent: Namespace):
        super().__init__(tokens, name, parent)
        ...


@dataclass
class Parser:
    global_ns:  Namespace
    output_dir: str
    tokens:     list[Token]
    tree:       Node

    def __init__(self, tokens: list[Token], output_dir: str = ''):
        self.tokens     = tokens
        self.output_dir = output_dir

        self.tree = None

    # def expecting_has(self, *strings: str) -> Token:
    #     if self.next().has(*strings):
    #         return self.take()

    #     raise ParserError(self.next().line.loc(), f'expecting has {strings}')

    # def expecting_of(self, *kinds: str) -> Token:
    #     if self.next().of(*kinds):
    #         return self.take()

    #     raise ParserError(self.next().line.loc(), f'expecting of {kinds}')

    def id_exists(self, id: str) -> bool:
        for a in self.global_ns.aliases:
            if a.name == id:
                return True
        for e in self.global_ns.enums:
            if e.name == id:
                return True
        return False

    def next(self) -> Token:
        return self.tokens[self.index]

    def parse(self) -> None:
        print(f'parsing {len(self.tokens)} tokens')
        self.global_ns = Namespace(self.tokens, 'global')

    def take(self) -> Token:
        token = self.next()
        self.index += 1
        return token

    def write_debug(self) -> None:
        if not self.output_dir:
            raise LanguageError('no output folder given')

        with open(os.path.join(self.output_dir, '3_parser.cakedebug'), 'w', newline='\n') as f:
            f.write(debug_header('step 3: parser'))
            # f.write(f'tree:\n\t{self.tree}\n')

            f.write('aliases:\n')
            for a in self.global_ns.aliases:
                f.write(f'\t{repr(a)}\n')

            f.write('enums:\n')
            for e in self.global_ns.enums:
                f.write(f'\t{repr(e)}\n')


class ParserError(LanguageError):
    def __init__(self, token: Token, *args):
        super().__init__(f'{token.loc()} | {token} | {' '.join(args)}')


@dataclass
class Type(Identifier):
    def __init__(self, token: Token):
        if not token.of('Type'):
            raise ParserError(token, 'expected Type')
        self.token = token
        self.name = token.string
