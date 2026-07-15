from dataclasses import dataclass
import os

from .expressions.expression import Expression
from .node import Node
from ..lexer import Token
from ..util import LanguageError, debug_header


@dataclass
class Accessor:
    parts:  list[Identifier | Type]
    name:   str
    scope:  str
    tokens: list[Token]

    @property
    def path(self) -> str:
        return f'{self.scope}.{'.'.join(self.parts)}'

    def __init__(self, tokens: list[Token], scope: str = ''):
        self.tokens = tokens
        self.scope = scope

        self.parts = []
        self.name  = ''

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
                raise ParserError(token.loc(), 'unexpected token in accessor')


@dataclass
class Alias:
    new:   Identifier
    old:   Accessor
    scope: str

    @property
    def path(self) -> str:
        return f'{self.scope}.{self.new}'

    def __init__(self, old: list[Token], new: Token, scope: str = ''):
        if not old or not new:
            raise ParserError('alias missing token')

        self.old   = Accessor(old)
        self.new   = Identifier(new)
        self.scope = scope

    def __repr__(self) -> str:
        return f'Alias["{self.old.name}" -> "{self.path}"]'


@dataclass
class Class:
    ...

    def __init__(self):
        ...


@dataclass
class Declaration:
    ...

    def __init__(self):
        ...


@dataclass
class Enum:
    elements: list[EnumElement]
    name:     Identifier
    scope:    str

    @property
    def path(self) -> str:
        return f'{self.scope}.{self.name}'

    def __init__(self, name: Token, elements: list[EnumElement], scope: str = ''):
        self.name     = Identifier(name)
        self.elements = elements
        self.scope    = scope

    def __repr__(self) -> str:
        return f'Enum["{self.path}" {self.elements}]'


@dataclass
class EnumElement:
    name:  Identifier
    value: int

    @property
    def path(self) -> str:
        return f'{self.scope}.{self.name}'

    def __init__(self, name: Token, value: int = 0, scope: str = ''):
        self.name  = Identifier(name)
        self.value = value
        self.scope = scope

    def __repr__(self) -> str:
        return f'{self.name}={self.value}'


@dataclass
class Function:
    ...

    def __init__(self):
        ...


@dataclass
class Identifier:
    token: Token

    def __init__(self, token: Token):
        if token.of('Identifier'):
            self.token = token
        else:
            raise ParserError(token.loc(), 'expected Identifier')

    def __repr__(self) -> str:
        return self.token.string

    def __str__(self) -> str:
        return self.token.string


@dataclass
class Interface:
    name: Identifier

    def __init__(self):
        ...


@dataclass
class Namespace:
    aliases:      list[Alias]
    classes:      list[Class]
    declarations: list[Declaration]
    enums:        list[Enum]
    functions:    list[Function]
    interfaces:   list[Interface]
    namespaces:   list[Namespace]
    structs:      list[Struct]

    def __init__(self):
        ...


@dataclass
class Struct:
    name:  Identifier
    scope: str

    def __init__(self):
        ...


@dataclass
class Parser:
    global_ns:  Namespace
    index:      int
    output_dir: str
    scope:      list[str]
    tokens:     list[Token]
    tree:       Node

    @property
    def expression(self):
        return Expression

    def __init__(self, tokens: list[Token], output_dir: str = ''):
        self.tokens     = tokens
        self.output_dir = output_dir

        self.tree = None

    def expecting_has(self, *strings: str) -> Token:
        if self.next().has(*strings):
            return self.take()

        raise ParserError(self.next().line.loc(), f'expecting has {strings}')

    def expecting_of(self, *kinds: str) -> Token:
        if self.next().of(*kinds):
            return self.take()

        raise ParserError(self.next().line.loc(), f'expecting of {kinds}')

    def id_exists(self, id: str) -> bool:
        for a in self.aliases:
            if a.new.string == id:
                return True
        for e in self.enums:
            if e.name == id:
                return True
        return False

    def make_alias(self):
        self.take()  # 'alias'

        old = []
        if self.next().of('Identifier', 'Type'):
            old = self.take()
            if self.next().of('Identifier'):
                new = self.take()
                if self.next().has(';'):
                    self.take()  # ';'
                    self.aliases.append(Alias([old], new, '.'.join(self.scope)))
                    return

        raise ParserError(self.next().loc(), 'bad alias statement')

    def make_class(self):
        if self.next().of('Special') and self.next().has('abstract', 'final'):
            modifier = self.take()

        if self.next().of('Special') and self.next().has('class'):
            self.take()

    def make_declaration(self):
        ...

    def make_enum(self):
        self.take()  # 'enum'

        if self.next().of('Identifier'):
            name = self.take()
            if self.next().has('{'):
                self.take()  # '{'
                elements: list[EnumElement] = []
                prev_value = -1
                while True:
                    if self.next().of('Identifier'):
                        element_name = self.take()
                        if self.next().of('Punctuator'):
                            if self.next().has(',', '}'):
                                if self.next().has(','):
                                    self.take()  # ','
                                prev_value += 1
                                elements.append(EnumElement(element_name, prev_value, '.'.join(self.scope + [name.string])))
                                if self.next().has('}'):
                                    self.take()  # '}'
                                    break
                        elif self.next().of('Operator') and self.next().has('='):
                            self.take()  # '='
                            if self.next().of('Number'):
                                value = int(self.take().string)
                                prev_value = value
                                elements.append(EnumElement(element_name, value, '.'.join(self.scope + [name.string])))
                            if self.next().of('Punctuator') and self.next().has(','):
                                self.take()  # ','
                    elif self.next().of('Punctuator') and self.next().has('}'):
                        self.take()  # '}'
                        break
                    else:
                        next = self.next()
                        raise ParserError(next.loc(), 'unexpected error')

                seen = set()
                for element in elements:
                    if element.value in seen:
                        raise ParserError(element.name.token.loc(), f'duplicate enum value: {element.value}')
                    seen.add(element.value)

                self.enums.append(Enum(name, elements, '.'.join(self.scope)))
                return

        raise ParserError(self.next().loc(), 'bad enum definition')

    def make_function(self):
        ...

    def make_interface(self):
        ...

    def make_namespace(self):
        ...

    def make_struct(self):
        ...

    def next(self) -> Token:
        return self.tokens[self.index]

    def parse(self) -> None:
        print(f'parsing {len(self.tokens)} tokens')

        self.aliases      = []
        self.classes      = []
        self.declarations = []
        self.enums        = []
        self.functions    = []
        self.interfaces   = []
        self.namespaces   = []
        self.structs      = []

        self.index = 0
        self.scope = ['']

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
                # elif next.has('namespace'):
                #     self.make_namespace()
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
                    print(self.take().loc(), 'warning: unexpected token')
            # elif next.of('Identifier', 'Type'):
            #     kind = self.take()
            #     if self.next().of('Operator') and self.next().has('$'):
            #         special = self.take()
            #     if self.next().of('Identifier'):
            #         name = self.take()
            else:
                print(self.take().loc(), 'warning: unexpected token')

    def take(self) -> Token:
        token = self.next()
        self.index += 1
        return token

    def write_debug(self) -> None:
        if not self.output_dir:
            raise ParserError('no output folder given')

        with open(os.path.join(self.output_dir, '3_parser.cakedebug'), 'w', newline='\n') as f:
            f.write(debug_header('step 3: parser'))
            # f.write(f'tree:\n\t{self.tree}\n')

            f.write('aliases:\n')
            for a in self.aliases:
                f.write(f'\t{repr(a)}\n')

            f.write('enums:\n')
            for e in self.enums:
                f.write(f'\t{repr(e)}\n')


class ParserError(LanguageError):
    pass


@dataclass
class Type:
    token: Token

    def __init__(self, token: Token):
        if token.of('Type'):
            self.token = token
        else:
            raise ParserError(token.loc(), 'expected Type')
