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

    def error(self, msg: str, token: Token = None):
        if not token:
            token = self.next
        raise ParserError(token, msg)

    def last_of_has(self, of: str, has: str) -> bool:
        return self.last.of_has(of, has) if self.last else False

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
                if self.last and self.last.of('Identifier', 'Type'):
                    break
                tokens.append(self.take())
                if (dot := self.take_specific('Operator', '.')):
                    tokens.append(dot)
                    continue
                if self.take_specific('Operator', '<'):
                    held_type = self.make_type()
                    if not self.take_specific('Operator', '>'):
                        self.error('expected ">"')
                if (ref := self.take_specific('Operator', '&')):
                    tokens.append(ref)
                break
            else:
                self.error('expected type')

        if len(tokens) > 1:
            if tokens[0].of_has('Operator', '@') and tokens[-1].of_has('Operator', '&'):
                self.error('metatypes are always references', tokens[0])
            for i, token in enumerate(tokens):
                if (i and (token.of_has('Operator', '@') or token.of_has('Special', 'mut')))\
                or (i < len(tokens) - 1 and token.of_has('Operator', '&')):
                    self.error('unexpected token', token)
        elif tokens:
            if not tokens[0].of('Identifier', 'Type'):
                self.error('unexpected token', tokens[0])

        return Type(tokens, held_type)

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
    members:     list[Member]
    methods:     list[Method]

    def __init__(self, tokens: list[Token], name: Identifier, parent: Namespace):
        super().__init__(tokens, name, parent)
        self.abstract    = False
        self.final       = False
        self.inheritance = []
        self.members     = []
        self.methods     = []

    def make_member(self, modifiers: list[Token]):
        member_type = self.make_type()

        if self.next.of('Identifier'):
            member_name = self.take()
        else:
            self.error('expected identifier')

        tokens: list[Token] = []

        if self.next.of_has('Operator', ';'):
            tokens.append(self.take())
        elif self.take_specific('Operator', '='):
            while True:
                tokens.append(self.take())
                if self.next.of('EOF'):
                    self.error('unexpected EOF')
                if self.next.of_has('Operator', ';'):
                    tokens.append(self.take())
                    break
        else:
            self.error('unexpected token in member')

        self.members.append(Member(modifiers, member_type, member_name, tokens[:-1], self))

    def make_method(self, modifiers: list[Token]):
        ...


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
        return f'Alias[ "{self.old.name}" -> "{self.path}" ]'


@dataclass
class Class(Inheritable):
    def __init__(self, tokens: list[Token], name: Token, parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)
        ...

    def __repr__(self):
        return f'Class[ ]'


@dataclass
class Declaration(Node):
    var_type: Type

    def __init__(self, tokens: list[Token], var_type: Type, name: Token, parent: Node):
        super().__init__(tokens, Identifier(name), parent)
        self.var_type = var_type

        ...  # TODO expression

    def __repr__(self) -> str:
        return f'Declaration[ {self.var_type} {self.name}{f' = {' '.join([t.string for t in self.tokens])}' if self.tokens else ''} ]'


@dataclass
class Enum(Node):
    elements: list[EnumElement]

    def __init__(self, elements: list[EnumElement], name: Token, parent: Namespace):
        super().__init__([], Identifier(name), parent)
        self.elements = elements
        for e in self.elements:
            e.parent = self

    def __repr__(self) -> str:
        return f'Enum[ {self.path} < {self.elements} > ]'


@dataclass
class EnumElement(Node):
    value: int

    def __init__(self, name: Token, value: int = 0):
        super().__init__(name=Identifier(name))
        self.value = value

    def __repr__(self) -> str:
        return f'EnumElement[ {self.name} = {self.value} ]'


@dataclass
class Function(Node):
    params:      list[Declaration]
    return_type: Type

    def __init__(self, return_type: Type, params: list[Declaration], name: Token = None, tokens: list[Token] = [], parent: Namespace = None):
        if name is not None:
            super().__init__(tokens, Identifier(name), parent)
        self.return_type = return_type

        self.params = params
        for p in self.params:
            p.parent = self

        ...  # TODO function body

    def __repr__(self) -> str:
        return f'Function[ {self.return_type} {self.name} < {', '.join([p.__repr__() for p in self.params])} > ]'


@dataclass
class Identifier:
    name:  str
    token: Token | None

    def __init__(self, token: Token):
        if not token.of('Identifier'):
            raise ParserError(token, 'expected identifier')
        self.token = token
        self.name  = token.string

    def __repr__(self) -> str:
        return f'Identifier[ {self.name} ]'

    def __str__(self) -> str:
        return self.name


@dataclass
class Interface(Inheritable):
    def __init__(self, tokens: list[Token], name: Token, parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)
        ...

    def __repr__(self) -> str:
        return f'Interface[ ]'


@dataclass
class Member(Declaration):
    modifiers: list[Token]

    def __init__(self, modifiers: list[Token], var_type: Type, name: Token, tokens: list[Token], parent: Inheritable):
        super().__init__(tokens, var_type, name, parent)
        self.modifiers = modifiers

        ...  # TODO expression

    def __repr__(self) -> str:
        return f'Member[ {f'< {' '.join([m.string for m in self.modifiers])} > ' if self.modifiers else ''}{self.var_type} {self.name} ]'


@dataclass
class Method(Member, Function):
    def __init__(
        self,
        modifiers:   list[Token],
        return_type: Type,
        name:        Token,
        params:      list[Declaration],
        tokens:      list[Token],
        parent:      Class | Interface
    ):
        super(Member, self).__init__(modifiers, None, name, tokens, parent)
        super(Function, self).__init__(return_type, params)

        ...  # TODO method body

    def __repr__(self) -> str:
        return f'Method[ {self.name} < {' '.join([m for m in self.modifiers])} >{
            super(Function, self).__repr__().replace('Function[', '')}'


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
                elif next.has('struct'):
                    self.make_struct()
                elif next.has('abstract', 'final'):
                    modifier = self.take()
                    match self.next.string:
                        # case 'class':
                        #     self.make_class()
                        #     pass
                        # case 'interface':
                        #     self.make_interface()
                        #     pass
                        case 'struct':
                            self.make_struct(modifier)
                        case _:
                            self.error('expected inheritable keyword')
                elif next.has('union'):
                    self.make_union()
                else:
                    self.unexpected.append(self.take())

            elif self.take_specific('Operator', '}'):
                pass

            elif next.of('Identifier', 'Type'):
                decl_type = self.make_type()
                if self.next.of('Identifier'):
                    name = self.take()
                    if self.take_specific('Operator', '('):
                        self.functions.append(self.make_function(decl_type, name))
                    else:
                        self.declarations.append(self.make_declaration(decl_type, name))
                else:
                    self.error('expected identifier')

            else:
                self.unexpected.append(self.take())

        if self.unexpected:
            print(f'namespace "{self.name}" has {len(self.unexpected)} unexpected tokens')

    def make_alias(self):
        self.take()  # 'alias'

        old: Type = None
        if self.next.of('Identifier', 'Type'):
            old = self.make_type()
        elif self.next.of_has('Operator', '<'):
            old = self.make_function_type()
        else:
            self.error('unexpected token in alias')

        if self.next.of('Identifier'):
            new = self.take()
            if self.take_specific('Operator', ';'):
                self.aliases.append(Alias(old, new, self))
            else:
                self.error('expected ";"')
        else:
            self.error('expected identifier')

    def make_block(self) -> list[Token]:
        if self.take_specific('Operator', '{'):
            stack = 1
            tokens = []
            while stack:
                next = self.next
                if next.of('EOF'):
                    self.error('unexpected EOF')
                if next.of('Operator'):
                    if next.has('{'):
                        stack += 1
                    elif next.has('}'):
                        stack -= 1
                tokens.append(self.take())
            return tokens
        else:
            self.error('expected "{"')

    def make_class(self):
        if self.next.of('Special') and self.next.has('abstract', 'final'):
            modifier = self.take()

        ...

    def make_declaration(self, decl_type: Type, name: Token) -> Declaration:
        tokens: list[Token] = []

        if self.next.of('Operator') and self.next.has(';', ',', ')'):
            if self.next.has(';', ','):
                self.take()
        elif self.take_specific('Operator', '='):
            while not self.next.of_has('Operator', ';'):
                tokens.append(self.take())
                if self.next.of('EOF'):
                    self.error('unexpected EOF')
        else:
            self.error('unexpected token in declaration')

        return Declaration(tokens, decl_type, name, self)

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
                            self.error('unexpected token in enum')
                    elif self.take_specific('Operator', '}'):
                        break
                    else:
                        self.error('unexpected token in enum')

                self.enums.append(Enum(elements, name, self))
                return

        self.error('bad enum definition')

    def make_function(self, return_type: Type, name: Token) -> Function:
        params = []

        if not self.take_specific('Operator', ')'):
            while True:
                if self.next.of('Identifier', 'Type'):
                    decl_type = self.make_type()
                    if self.next.of('Identifier'):
                        params.append(self.make_declaration(decl_type, self.take()))
                    else:
                        self.error('expected identifier')

                    if self.take_specific('Operator', ','):
                        continue
                    if self.take_specific('Operator', ')'):
                        break
                elif self.take_specific('Operator', ')'):
                    break
                else:
                    self.error('expected type')

        if self.take_specific('Operator', ';'):
            return Function(return_type, params, name, [], self)

        return Function(return_type, params, name, self.make_block(), self)

    def make_function_type(self) -> FunctionType:
        first = self.take()  # "<"

        return_type: Type = None

        if self.next.of('Type'):
            return_type = Type(self.take())
            if not self.take_specific('Operator', '>'):
                self.error('expected ">"')
        elif self.next.of('Identifier'):
            return_type = self.make_type()
            self.take_specific('Operator', '>')
        else:
            self.error('expected identifier or type')

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
                    self.error('unexpected EOF')
                else:
                    self.error('expected type')
        else:
            self.error('expected "<"')

        return FunctionType(first, return_type, param_types)

    def make_interface(self):
        ...

    def make_namespace(self):
        self.take()  # 'namespace'

        if self.next.of('Identifier'):
            name = self.take()
            self.namespaces.append(Namespace(
                self.make_block() + [Token('EOF', None)], Identifier(name), self
            ))
        else:
            self.error('expected identifier')

    def make_struct(self, modifier: Token = None):
        self.take()  # "struct"

        if self.next.of('Identifier'):
            struct_name = self.take()
            ...  # TODO inheritance
            self.structs.append(Struct(modifier, struct_name, self.make_block(), self))
        else:
            self.error('expected identifier')

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
                            self.error('expected identifier', type_parts[-1])
                        param_type = ''.join([t.string for t in type_parts])
                        if param_type in types:
                            self.error('duplicate union parameter type', type_parts)
                        types.add(param_type)
                        if self.next.of('Identifier'):
                            id = self.take()
                            if id.string in ids:
                                self.error('duplicate union parameter name', id)
                            ids.add(id.string)
                            params.append(UnionParam(held_type, id))
                            self.take_specific('Operator', ',')
                            if self.take_specific('Operator', '>'):
                                break
                        else:
                            self.error('expected identifier')
                    elif self.take_specific('Operator', '>'):
                        break
                if not self.last_of_has('Operator', '>'):
                    self.error('expected ">"', self.last)

            if self.take_specific('Operator', '{'):
                tokens = []
                while not self.take_specific('Operator', '}'):
                    if self.next.of('EOF'):
                        self.error('unexpected EOF')
                    tokens.append(self.take())
                self.unions.append(Union(params, tokens, union_name, self))
                return
            else:
                self.error('expected "{"')

        else:
            self.error('expected identifier')


@dataclass
class BareNamespace(Namespace):
    def __init__(self, name: Identifier | str, parent: Namespace = None):
        super().__init__([], name, parent)

    def __repr__(self) -> str:
        return f'BareNamespace[ ]'


@dataclass
class StdNamespace(BareNamespace):
    def __init__(self, parent: Namespace = None):
        super().__init__('std', parent)

    def __repr__(self) -> str:
        return f'StdNamespace[ ]'


@dataclass
class Struct(Inheritable):
    def __init__(self, modifier: Token, name: Token, tokens: list[Token], parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)

        if modifier:
            if modifier.of_has('Special', 'abstract'):
                self.abstract = True
            elif modifier.of_has('Special', 'final'):
                self.final = True
            else:
                self.error('unexpected modifier token in struct')

        while not self.take_specific('Operator', '}'):
            ...  # TODO overrides

            member_modifiers = []
            if self.next.of('Special'):
                if self.next.has('private', 'protected', 'final'):
                    member_modifiers.append(self.take())
                    if self.last.has('protected') and self.next.of_has('Special', 'final'):
                        member_modifiers.append(self.take())
                else:
                    self.error('unexpected keyword')

            if self.next.of('Identifier', 'Type'):
                self.make_member(member_modifiers)
            elif self.take_specific('Operator', ';'):
                pass
            else:
                self.error('expected type')

    def __repr__(self) -> str:
        mod = 'abstract' if self.abstract else 'final' if self.final else ''
        return f'Struct[ {f'{mod} ' if mod else ''}{
            self.name} < {', '.join([m.__repr__() for m in self.members])} > ]'


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
        return f'Type[ {self.name} ]'


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
        return f'FunctionType[ {self.return_type} < {', '.join([t.name for t in self.param_types])} > ]'


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
                                    self.error('union parameter already used', held)
                                p.used = True
                                self.elements.append(UnionElement(element_name, self, p))
                                break
                        if not found:
                            self.error('union parameter not found', held)
                        if not self.take_specific('Operator', ')'):
                            self.error('expected ")"')
                        self.take_specific('Operator', ',')
                    else:
                        self.error('expected identifier')

        for p in self.params:
            if not p.used:
                self.error('unused union parameter', p.held_type.token)

    def __repr__(self) -> str:
        return f'Union[ {self.path} < {', '.join([p.__repr__() for p in self.params])} > < {', '.join([e.__repr__() for e in self.elements])} > ]'


@dataclass
class UnionElement(Node):
    param: UnionParam

    def __init__(self, name: Token, parent: Union, param: UnionParam = None):
        super().__init__([], Identifier(name), parent)
        self.param = param
        if self.param:
            self.param.element = self

    def __repr__(self) -> str:
        return f'UnionElement[ {self.name}{f'< {self.param.name} >' if self.param else ''} ]'


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
        return f'UnionParam[ {self.held_type} {self.name} ]'
