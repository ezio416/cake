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

    def last_of_has(self, of: str, has: str) -> bool:
        return self.last.of_has(of, has) if self.last else False

    def take(self) -> Token:
        token = self.next
        if not (token.of('EOF')):
            self.index += 1
        return token

    def take_specific(self, of: str, has: str) -> Token | None:
        return self.take() if self.next.of_has(of, has) else None


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


# @dataclass
# class Accessor(Node):
#     parts: list[Identifier | Type]

#     def __init__(self, tokens: list[Token] = [], parent: Node = None):
#         super().__init__(tokens, parent=parent)

#         self.parts = []

#         for token in self.tokens:
#             if token.of('Identifier', 'Type'):
#                 self.name += token.string
#                 if token.of('Identifier'):
#                     self.parts.append(Identifier(token))
#                 else:
#                     self.parts.append(Type(token))
#             elif token.of('Operator') and token.has('.'):
#                 self.name += token.string
#             else:
#                 raise ParserError(token, 'unexpected token in accessor')


@dataclass
class Alias(Node):
    old: Type

    def __init__(self, old: Type, name: Token, parent: Node):
        if not old or not name:
            raise LanguageError('alias missing token')

        super().__init__(old, Identifier(name), parent)
        self.old = old

    def __repr__(self) -> str:
        return f'Alias["{self.old.name}" -> "{self.path}"]'


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
    name:  str
    token: Token | None

    def __init__(self, token: Token):
        if not token.of('Identifier'):
            raise ParserError(token, 'expected Identifier')
        self.token = token
        self.name  = token.string

    def __repr__(self) -> str:
        return f'Identifier["{self.name}"]'

    def __str__(self) -> str:
        return self.name


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
    unexpected:   list[Token]
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
        self.unexpected   = []
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
                elif next.has('mut'):
                    self.make_declaration()
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
                    self.unexpected.append(self.take())

            elif self.take_specific('Operator', '}'):
                pass

            # elif next.of('Identifier'):
            #     ...  # TODO declarations/functions

            else:
                self.unexpected.append(self.take())

        if self.unexpected:
            print(f'namespace "{self.name}" has {len(self.unexpected)} unexpected tokens')

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

        old: Type = None
        if self.next.of('Identifier', 'Type'):
            old = self.make_type()
        elif self.next.of_has('Operator', '<'):
            old = self.make_function_type()
        else:
            raise ParserError(self.next, 'unexpected token in alias')

        if self.next.of('Identifier'):
            new = self.take()
            if self.take_specific('Operator', ';'):
                self.aliases.append(Alias(old, new, self))
            else:
                raise ParserError(self.next, 'expected ";"')
        else:
            raise ParserError(self.next, 'expected identifier')

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

    def make_function_type(self) -> FunctionType:
        first = self.take()  # "<"

        return_type: Type = None

        if self.next.of('Type'):
            return_type = Type(self.take())
            if not self.take_specific('Operator', '>'):
                raise ParserError(self.next, 'expected ">"')
        elif self.next.of('Identifier'):
            return_type = self.make_type()
            self.take_specific('Operator', '>')
        else:
            raise ParserError(self.next, 'expected identifier or type')

        if self.take_specific('Operator', '<'):
            param_types: list[Type] = []
            while True:
                if self.next.of('Identifier', 'Type') or self.next.of_has('Operator', '@') or self.next.of_has('Special', 'mut'):
                    param_types.append(self.make_type())
                elif self.take_specific('Operator', ','):
                    continue
                elif self.take_specific('Operator', '>'):
                    break
                elif self.next.of('EOF'):
                    raise ParserError(self.next, 'unexpected EOF')
                else:
                    raise ParserError(self.next, 'expected type')
        else:
            raise ParserError(self.next, 'expected "<"')

        return FunctionType(first, return_type, param_types)

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

    def make_type(self) -> Type:
        held_type: Type = None
        tokens: list[Token] = []

        while True:
            if (mut := self.take_specific('Special', 'mut')):
                tokens.append(mut)
            elif (meta := self.take_specific('Operator', '@')):
                tokens.append(meta)
            elif (ref := self.take_specific('Operator', '&')):
                tokens.append(ref)
                break
            elif self.take_specific('Operator', '>'):
                break
            elif self.take_specific('Operator', ','):
                break
            elif self.next.of('Type'):
                tokens.append(self.take())
            elif self.next.of('Identifier'):
                if self.last.of('Identifier', 'Type'):
                    break
                tokens.append(self.take())
                if (dot := self.take_specific('Operator', '.')):
                    tokens.append(dot)
                    continue
                if self.take_specific('Operator', '<'):
                    held_type = self.make_type()
                    if not self.take_specific('Operator', '>'):
                        raise ParserError(self.next, 'expected ">"')
                if (ref := self.take_specific('Operator', '&')):
                    tokens.append(ref)
                break
            else:
                raise ParserError(self.next, 'expected type')

        if len(tokens) > 1:
            if tokens[0].of_has('Operator', '@') and tokens[-1].of_has('Operator', '&'):
                raise ParserError(tokens[0], 'metatypes are always references')
            for i, token in enumerate(tokens):
                if (i and (token.of_has('Operator', '@') or token.of_has('Special', 'mut')))\
                or (i < len(tokens) - 1 and token.of_has('Operator', '&')):
                    raise ParserError(token, 'unexpected token')
        elif tokens:
            if not tokens[0].of('Identifier', 'Type'):
                raise ParserError(tokens[0], 'unexpected token')

        return Type(tokens, held_type)

    def make_union(self):
        self.take()  # 'union'

        if self.next.of('Identifier'):
            union_name = self.take()
            params = []
            if self.take_specific('Operator', '<'):
                ids = set()
                types = set()
                while True:
                    held_type = self.make_type()
                    if (type_parts := held_type.tokens):
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
                            params.append(UnionParam(held_type, id))
                            self.take_specific('Operator', ',')
                            if self.take_specific('Operator', '>'):
                                break
                        else:
                            raise ParserError(self.next, 'expected identifier')
                    elif self.take_specific('Operator', '>'):
                        break
                if not self.last_of_has('Operator', '>'):
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
    held_type: Type | None
    mut:       bool
    tokens:    list[Token]

    def __init__(self, token: Token | list[Token], held_type: Type = None):
        self.held_type = held_type
        if type(token) is Token:
            if not token.of('Type') and not token.has('mut') and not token.of_has('Operator', '<'):
                raise ParserError(token, 'expected type')
            self.token  = token
            self.tokens = []
            self.name   = token.string
        else:
            self.token  = token[0]
            self.tokens = token
            self.name   = ''.join([t.string for t in self.tokens])

        self.mut = self.token.of_has('Special', 'mut')
        if self.mut:
            self.name = f'mut {self.name[3:]}'

        if self.held_type:
            ref = False
            if self.name.endswith('&'):
                ref = True
                self.name = self.name[:-1]
            self.name += f'<{self.held_type}>'
            if ref:
                self.name += '&'

    def __repr__(self) -> str:
        return f'Type["{self.name}"]'


@dataclass
class FunctionType(Type):
    param_types: list[Type]

    @property
    def return_type(self) -> Type | None:
        return self.held_type

    def __init__(self, first_token: Token, return_type: Type, param_types: list[Type] = []):
        super().__init__(first_token, return_type)
        self.held_type = return_type
        self.param_types = param_types

        self.name = f'<{self.return_type}><{', '.join([t.name for t in self.param_types])}>'

    def __repr__(self) -> str:
        return f'FunctionType["{self.return_type} ({', '.join([t.name for t in self.param_types])})"]'


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

        for p in self.params:
            if not p.used:
                raise ParserError(p.held_type.token, 'unused union parameter')

    def __repr__(self) -> str:
        return f'Union["{self.path}" <{', '.join([p.__repr__() for p in self.params])}> <{', '.join([e.__repr__() for e in self.elements])}>]'


@dataclass
class UnionElement(Node):
    param: UnionParam

    def __init__(self, name: Token, parent: Union, param: UnionParam = None):
        super().__init__([], Identifier(name), parent)
        self.param = param
        if self.param:
            self.param.element = self

    def __repr__(self) -> str:
        return f'{self.name}{f'({self.param.name})' if self.param else ''}'


@dataclass
class UnionParam(Node):
    element:   UnionElement | None
    held_type: Type
    used:      bool

    def __init__(self, held_type: Type, name: Token):
        super().__init__(held_type.tokens, Identifier(name))
        self.element   = None
        self.held_type = held_type
        self.used      = False

    def __repr__(self) -> str:
        return f'{self.held_type} {self.name}'
