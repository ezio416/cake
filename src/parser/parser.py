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
    def last(self) -> Token:  # TODO remove lookbehind
        return self.tokens[self.index - 1] if self.index > 0 else None

    @property
    def next(self) -> Token:
        return self.tokens[self.index]

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

    def take(self) -> Token:
        token = self.next
        if not (token.of('EOF')):
            self.index += 1
        return token

    def take_specific(self, of: str, has: str) -> Token:
        if self.next.of(of) and self.next.has(has):
            return self.take()


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
    unions:       list[Union]

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
        self.unions       = []

        if self.name == 'global':
            self.namespaces.append(StdNamespace(self))

        if not self.tokens:
            return

        while not ((next := self.next).of('EOF')):
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
                elif next.has('union'):
                    self.make_union()
                else:
                    token = self.take()
                    print(token.loc(), f'warning: unexpected special keyword: {token}')

            else:
                token = self.take()
                print(token.loc(), f'warning: unexpected token: {token}')

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
        if self.next.of('Identifier', 'Type'):
            old = self.take()
            if self.next.of('Identifier'):
                new = self.take()
                if self.take_specific('Operator', ';'):
                    self.aliases.append(Alias([old], new, self))
                    return

        raise ParserError(self.next, 'bad alias statement')

    def make_class(self):
        if self.next.of('Special') and self.next.has('abstract', 'final'):
            modifier = self.take()

        ...

    def make_declaration(self):
        ...

    def make_enum(self):
        self.take()  # 'enum'

        if self.next.of('Identifier'):
            name = self.take()
            if self.take_specific('Operator', '{'):
                elements: list[EnumElement] = []
                prev_value = -1
                while True:
                    if (next := self.next).of('Identifier'):
                        element_name = self.take()
                        if self.take_specific('Operator', ','):
                            elements.append(EnumElement(element_name))
                            prev_value += 1
                        elif self.take_specific('Operator', '}'):
                            elements.append(EnumElement(element_name))
                            break
                        elif self.take_specific('Operator', '='):
                            if self.next.of('Number'):
                                value = int(self.take().string)
                                prev_value = value
                                elements.append(EnumElement(element_name, value))
                            self.take_specific('Operator', ',')
                        else:
                            raise ParserError(next, 'unexpected token in enum')
                    elif self.take_specific('Operator', '}'):
                        break
                    else:
                        raise ParserError(next, 'unexpected token in enum')

                self.enums.append(Enum(elements, name, self))
                return

        raise ParserError(self.next, 'bad enum definition')

    def make_function(self):
        ...

    def make_interface(self):
        ...

    def make_namespace(self):
        self.take()  # 'namespace'

        if self.next.of('Identifier'):
            name = self.take()
            if self.take_specific('Operator', '{'):
                stack = 1
                tokens = []
                while stack:
                    next = self.next
                    if next.of('EOF'):
                        raise ParserError(next, 'unexpected EOF')
                    if next.of('Operator'):
                        if next.has('{'):
                            stack += 1
                        elif next.has('}'):
                            stack -= 1
                    tokens.append(self.take())
                self.namespaces.append(Namespace(tokens + [Token('EOF', None)], Identifier(name), self))
        else:
            raise ParserError(self.next, 'expected identifier')

    def make_struct(self):
        ...

    def make_union(self):
        self.take()  # 'union'

        if self.next.of('Identifier'):
            union_name = self.take()
            params = []
            if self.take_specific('Operator', '<'):
                ids = set()
                types = set()
                while True:
                    type_parts: list[Token] = []
                    if (metatype := self.take_specific('Operator', '@')):
                        type_parts.append(metatype)
                    while True:
                        if self.next.of('Identifier', 'Type'):
                            type_parts.append(self.take())
                            if (dot := self.take_specific('Operator', '.')):
                                type_parts.append(dot)
                            else:
                                break
                        else:
                            break
                    if type_parts:
                        if type_parts[-1].has('.'):
                            raise ParserError(type_parts[-1], 'expected identifier')
                        param_type = ''.join([n.string for n in type_parts])
                        if param_type in types:
                            raise ParserError(type_parts, 'duplicate union parameter type')
                        types.add(param_type)
                        if self.next.of('Identifier'):
                            id = self.take()
                            if id.string in ids:
                                raise ParserError(id, 'duplicate union parameter name')
                            ids.add(id.string)
                            params.append(UnionParam(type_parts, id))
                            self.take_specific('Operator', ',')
                        else:
                            raise ParserError(self.next, 'expected identifier')
                    elif self.take_specific('Operator', '>'):
                        break
                if not self.last.of('Operator') or not self.last.has('>'):
                    raise ParserError(self.last, 'expected ">"')

            if self.take_specific('Operator', '{'):
                tokens = []
                while not self.take_specific('Operator', '}'):
                    if self.next.of('EOF'):
                        raise ParserError(self.next, 'unexpected EOF')
                    tokens.append(self.take())
                self.unions.append(Union(params, tokens, union_name, self))
                return
            else:
                raise ParserError(self.next, 'expected "{"')

        raise ParserError(self.next, 'bad union definition')


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
        ...  # TODO second pass

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
    def __init__(self, token: Token | list[Token], *args):
        if type(token) is Token:
            super().__init__(f'{token.loc()} | {token} | {' '.join(args)}')
        else:
            super().__init__(f'{token[0].loc()} | {' '.join(token)} | {' '.join(args)}')


@dataclass
class Type(Identifier):
    def __init__(self, token: Token):
        if not token.of('Type'):
            raise ParserError(token, 'expected Type')
        self.token = token
        self.name = token.string


@dataclass
class Union(Node):
    elements: list[UnionElement]
    params:   list[UnionParam]

    def __init__(self, params: list[UnionParam], tokens: list[Token], name: Token, parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)
        self.params = params
        for p in self.params:
            p.parent = self

        self.elements = []

        if not self.tokens:
            return

        self.tokens.append(Token('EOF', None))

        while not self.next.of('EOF'):
            if self.next.of('Identifier'):
                element_name = self.take()
                if self.next.of('EOF'):
                    self.elements.append(UnionElement(element_name, self))
                    return
                if self.take_specific('Operator', ','):
                    self.elements.append(UnionElement(element_name, self))
                elif self.take_specific('Operator', '('):
                    if self.next.of('Identifier'):
                        held = self.take()
                        found = False
                        for p in self.params:
                            if held.string == str(p.name):
                                found = True
                                if p.used:
                                    raise ParserError(held, 'union parameter already used')
                                p.used = True
                                self.elements.append(UnionElement(element_name, self, p))
                                break
                        if not found:
                            raise ParserError(held, 'union parameter not found')
                        if not self.take_specific('Operator', ')'):
                            raise ParserError(self.next, 'expected ")"')
                        self.take_specific('Operator', ',')
                    else:
                        raise ParserError(self.next, 'expected identifier')

        pass

    def __repr__(self) -> str:
        return f'Union["{self.path}" <{', '.join([p.__repr__() for p in self.params])}> <{', '.join([e.__repr__() for e in self.elements])}>]'


@dataclass
class UnionElement(Node):
    param: UnionParam

    def __init__(self, name: Token, parent: Union, param: UnionParam = None):
        super().__init__([], Identifier(name), parent)
        self.param = param

    def __repr__(self) -> str:
        return f'{self.name}{f'({self.param.name})' if self.param else ''}'


@dataclass
class UnionParam(Node):
    element: UnionElement
    used:    bool

    def __init__(self, tokens: list[Token], name: Token):
        super().__init__(tokens, Identifier(name))
        self.used = False

    def __repr__(self) -> str:
        return f'{''.join([t.string for t in self.tokens])} {self.name}'
