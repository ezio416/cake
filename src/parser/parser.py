from abc import ABC
from dataclasses import dataclass
import os
from typing import Never

from ..lexer import Token
from ..util import LanguageError, debug_header


SYM_BAR   = '\u2502  '       # "│   "
SYM_L     = '\u2514\u2500 '  # "└── "
SYM_SPACE = '   '
SYM_T     = '\u251C\u2500 '  # "├── "


@dataclass
class Node(ABC):
    index:  int
    name:   Identifier | str
    parent: Node | None
    tokens: list[Token]

    @property
    def last(self) -> Token:
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

    @property
    def token(self) -> Token | None:
        return self.tokens[0] if self.tokens else None

    def __init__(self, tokens: list[Token] = [], name: Identifier | str = '', parent: Node = None):
        self.tokens = tokens
        self.name   = name
        self.parent = parent

        self.index  = 0

    def error(self, msg: str, token: Token = None) -> Never:
        if not token:
            token = self.next
        raise ParserError(token, msg)

    def expect(self, of: str = '', has: str = '') -> Token:
        if of and not self.next.of(of):
            self.error(f'expected {of}{f' "{has}"' if has else ''}')
        if has and not self.next.has(has):
            self.error(f'expected "{has}"')
        return self.take()

    def last_of_has(self, of: str, has: str) -> bool:
        return self.last.of_has(of, has) if self.last else False

    def make_alias(self) -> Alias:
        self.take()  # "alias"

        old: Type = None
        if self.next.type_starter(False):
            old = self.make_type()
        elif self.next.of_has('Operator', '<'):
            old = self.make_function_type()
        else:
            self.error('unexpected token in alias')

        new = self.expect('Identifier')
        self.expect('Operator', ';')

        return Alias(old, new, self)

    def make_block(self) -> Block:
        return self.make_stack(Block, '{', '}')

    def make_declaration(self, decl_type: Type = None, name: Token = None) -> Declaration:
        if not decl_type:
            decl_type = self.make_type()
        if not name:
            name = self.expect('Identifier')
        tokens: list[Token] = []

        if self.next.of('Operator') and self.next.has(';', ',', ')'):
            if self.next.has(';', ','):
                self.take()
        elif self.take_specific('Operator', '='):
            while not self.next.of_has('Operator', ';'):
                tokens.append(self.take())
                if self.next.of('EOF'):
                    self.error('unexpected EOF')
            self.expect('Operator', ';')
        else:
            self.error('unexpected token in declaration')

        return Declaration(decl_type, name, tokens, self)

    def make_function_type(self) -> FunctionType:
        first = self.take()  # "<"

        return_type: Type = None

        if self.next.of('Type'):
            return_type = Type(self.take())
            self.expect('Operator', '>')
        elif self.next.of('Identifier'):
            return_type = self.make_type()
            self.take_specific('Operator', '>')
        else:
            self.error('expected identifier or type')

        self.expect('Operator', '<')
        param_types: list[Type] = []
        while True:
            if self.next.type_starter() or self.next.of_has('Operator', '@'):
                param_types.append(self.make_type())
            elif self.take_specific('Operator', ','):
                continue
            elif self.take_specific('Operator', '>'):
                break
            elif self.next.of('EOF'):
                self.error('unexpected EOF')
            else:
                self.error('expected type')

        return FunctionType(first, return_type, param_types)

    def make_paren(self) -> Paren:
        return self.make_stack(Paren, '(', ')')

    def make_stack(self, kind: type, open: str, close: str) -> Node | list[Token]:
        self.expect('Operator', open)

        stack = 1
        tokens = []
        while stack:
            next = self.next
            if next.of('EOF'):
                self.error('unexpected EOF')
            if next.of('Operator'):
                if next.has(open):
                    stack += 1
                elif next.has(close):
                    stack -= 1
            tokens.append(self.take())

        return kind(tokens, self) if kind else tokens

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
                self.take_specific('Operator', ',')
                break
            elif self.take_specific('Operator', '>'):
                self.take_specific('Operator', ',')
                break
            elif self.take_specific('Operator', ','):
                break
            elif self.next.of('Type'):
                tokens.append(self.take())
                if (ref := self.take_specific('Operator', '&')):
                    tokens.append(ref)
                break
            elif self.next.of('Identifier'):
                if self.last and self.last.type_starter(False):
                    break
                tokens.append(self.take())
                if (dot := self.take_specific('Operator', '.')):
                    tokens.append(dot)
                    continue
                if (left := self.take_specific('Operator', '<')):
                    tokens.append(left)
                    held_type = self.make_type()
                    tokens += held_type.tokens
                    tokens.append(self.expect('Operator', '>'))
                if (ref := self.take_specific('Operator', '&')):
                    tokens.append(ref)
                self.take_specific('Operator', ',')
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
            if not tokens[0].type_starter(False):
                self.error('unexpected token', tokens[0])

        return Type(tokens, held_type)

    def parse(self, parser: Parser):
        if self.__class__.__name__ not in parser.unimpl:
            parser.unimpl.add(self.__class__.__name__)
            print(f'warning: 2nd pass not implemented for {self.__class__.__name__}')

    def peek(self, ahead: int = 1) -> Token:
        if self.index + ahead - 1 >= len(self.tokens):
            return Token('EOF', None)

        return self.tokens[self.index + ahead - 1]

    def take(self) -> Token:
        token = self.next
        if not (token.of('EOF')):
            self.index += 1
        return token

    def take_specific(self, of: str, has: str) -> Token | None:
        return self.take() if self.next.of_has(of, has) else None

    def tree(self, prepend: str) -> str:
        return f'*{self.__class__.__name__}'


class Expression(Node, ABC):
    def __init__(self, tokens: list[Token], parent: Node):
        Node.__init__(self, tokens, '$expr', parent)

        ...  # expression

    def __repr__(self) -> str:
        tokens = ' '.join([t.string for t in self.tokens])
        return f'{self.__class__.__name__}[{tokens}]'


@dataclass
class Alias(Node):
    old: Type

    def __init__(self, old: Type, name: Token, parent: Node):
        if not old or not name:
            raise LanguageError('alias missing token')

        super().__init__(old, Identifier(name), parent)
        self.old = old

    def __repr__(self) -> str:
        return f'Alias[{self.old.name} {self.path}]'

    def parse(self, parser: Parser):
        self.old.parse(parser, self.path)

    def tree(self, prepend: str) -> str:
        return f'Alias "{self.path}"\n{prepend}{SYM_L}{
            self.old.tree(prepend + SYM_SPACE)}'


@dataclass
class Namespace(Node):
    aliases:       list[Alias]
    classes:       list[Class]
    declarations:  list[Declaration]
    enums:         list[Enum]
    functions:     list[Function]
    interfaces:    list[Interface]
    namespaces:    list[Namespace]
    nodes:         dict[str, Node]
    ordered_nodes: dict[str, Node]
    structs:       list[Struct]
    unions:        list[Union]

    def __init__(self, tokens: list[Token], name: Identifier | str, parent: Namespace = None):
        super().__init__(tokens, name, parent)

        self.aliases       = []
        self.classes       = []
        self.declarations  = []
        self.enums         = []
        self.functions     = []
        self.interfaces    = []
        self.nodes         = {}
        self.ordered_nodes = {}
        self.namespaces    = []
        self.structs       = []
        self.unions        = []

        if self.name == 'global':
            self.namespaces.append(StdNamespace(self))
            self.add_node(self.namespaces[-1])

        if not self.tokens:
            return

        while not ((next := self.next).of('EOF')):
            if next.of('Special'):
                match next.string:
                    case 'alias':
                        self.aliases.append(self.make_alias())
                        self.add_node(self.aliases[-1])
                    case 'enum':      self.make_enum()
                    case 'mut':
                        self.declarations.append(self.make_declaration())
                        self.add_node(self.declarations[-1])
                    case 'namespace': self.make_namespace()
                    case 'union':     self.make_union()
                    case _:
                        if next.has('class', 'interface', 'struct'):
                            self.make_inheritable()
                        elif next.has('abstract', 'final'):
                            modifier = self.take()
                            if self.next.of('Special') and self.next.has('class', 'interface', 'struct'):
                                self.make_inheritable(modifier)
                            else:
                                self.error('expected inheritable keyword')
                        else:
                            self.error('unexpected keyword')

            elif self.take_specific('Operator', '}'):
                pass

            elif next.type_starter(False):
                decl_type = self.make_type()
                name = self.expect('Identifier')
                if self.take_specific('Operator', '('):
                    self.functions.append(self.make_function(decl_type, name))
                    self.add_node(self.functions[-1])
                    if self.functions[-1].block:
                        for n in self.functions[-1].block.nodes:
                            self.add_node(n)
                    for p in self.functions[-1].params:
                        self.add_node(p)
                else:
                    self.declarations.append(self.make_declaration(decl_type, name))
                    self.add_node(self.declarations[-1])

            else:
                self.error('unexpected token')

        self.ordered_nodes = {k: v for k, v in sorted(self.nodes.items(), key=lambda x: x[0].lower())}

    def __repr__(self) -> str:
        return f'Namespace[{self.name}]'  # TODO ns repr

    def add_node(self, node: Node) -> None:
        path = node.path[len(self.path) + 1:]
        if path.endswith('.'):
            return
        if path in self.nodes:
            raise LanguageError(f'duplicate name: {node.path}')  # TODO lang error
        self.nodes[path] = node

    def make_enum(self):
        self.take()  # "enum"

        name = self.expect('Identifier')
        self.expect('Operator', '{')
        elements = []
        value = -1
        while True:
            if self.next.of('Identifier'):
                element_name = self.take()
                if self.take_specific('Operator', ','):
                    value += 1
                    elements.append(EnumElement(element_name, value))
                elif self.take_specific('Operator', '}'):
                    elements.append(EnumElement(element_name, value + 1))
                    break
                elif self.take_specific('Operator', '='):
                    if self.next.of('Number'):
                        value = int(self.take().string)
                        elements.append(EnumElement(element_name, value, self.last))
                    self.take_specific('Operator', ',')
                else:
                    self.error('unexpected token in enum')
            elif self.take_specific('Operator', '}'):
                break
            else:
                self.error('unexpected token in enum')

        self.enums.append(Enum(elements, name, self))
        self.add_node(self.enums[-1])
        for e in self.enums[-1].elements:
            self.add_node(e)

    def make_function(self, return_type: Type, name: Token) -> Function:
        params = []

        while not self.take_specific('Operator', ')'):
            if self.next.type_starter(False):
                params.append(self.make_declaration())

                if self.take_specific('Operator', ','):
                    continue
            else:
                self.error('expected type')

        return Function(
            return_type,
            name,
            params,
            [] if self.take_specific('Operator', ';') else self.make_block().tokens,
            self
        )

    def make_inheritable(self, modifier: Token = None):
        arr = list[Inheritable]
        cls = None

        match self.take().string:
            case 'class':
                arr = self.classes
                cls = Class
            case 'interface':
                arr = self.interfaces
                cls = Interface
            case 'struct':
                arr = self.structs
                cls = Struct

        arr.append(cls(
            modifier,
            self.expect('Identifier'),
            self.make_inheritance(),
            self.make_block().tokens,
            self
        ))
        self.add_node(arr[-1])
        for m in arr[-1].members:
            self.add_node(m)
        for m in arr[-1].methods:
            self.add_node(m)
            for n in m.block.nodes:
                self.add_node(n)
        for m in arr[-1].override_members:
            self.add_node(m)
        for m in arr[-1].override_methods:
            self.add_node(m)
            for n in m.block.nodes:
                self.add_node(n)

    def make_inheritance(self) -> list[Type]:
        ret = []

        if not self.take_specific('Operator', ':'):
            return ret

        while True:
            if self.next.type_starter(False):
                ret.append(self.make_type())
                if self.next.of_has('Operator', '{'):
                    break
            else:
                self.error('expected inheritable path')

        return ret

    def make_namespace(self):
        self.take()  # "namespace"

        name = self.expect('Identifier')
        self.namespaces.append(Namespace(
            self.make_block().tokens + [Token('EOF', None)], Identifier(name), self
        ))
        self.add_node(self.namespaces[-1])
        for n in self.namespaces[-1].nodes.values():
            self.add_node(n)

    def make_union(self):
        self.take()  # "union"

        name = self.expect('Identifier')
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
                    id = self.expect('Identifier')
                    if id.string in ids:
                        self.error('duplicate union parameter name', id)
                    ids.add(id.string)
                    params.append(Declaration(held_type, id, [], None))
                    self.take_specific('Operator', ',')
                    if self.take_specific('Operator', '>'):
                        break
                elif self.take_specific('Operator', '>'):
                    break
            if not self.last_of_has('Operator', '>'):
                self.error('expected ">"', self.last)

        self.expect('Operator', '{')
        tokens = []
        while not self.take_specific('Operator', '}'):
            if self.next.of('EOF'):
                self.error('unexpected EOF')
            tokens.append(self.take())

        self.unions.append(Union(params, tokens, name, self))
        self.add_node(self.unions[-1])
        for p in self.unions[-1].params:
            self.add_node(p)

    def parse(self, parser: Parser):
        for node in self.nodes.values():
            node.parse(parser)

    def tree(self, prepend: str) -> str:
        ret = f'Namespace "{self.path}"'

        last = self.unions\
            or self.structs\
            or self.namespaces\
            or self.interfaces\
            or self.functions\
            or self.enums\
            or self.declarations\
            or self.classes\
            or self.aliases
        last_index = len(last) - 1

        for arr in (
            self.aliases,
            self.classes,
            self.declarations,
            self.enums,
            self.functions,
            self.interfaces,
            self.namespaces,
            self.structs,
            self.unions
        ):
            for i, node in enumerate(arr):
                ret += f'\n{prepend}'
                if arr is last and i == last_index:
                    ret += f'{SYM_L}{node.tree(prepend + SYM_SPACE)}'
                else:
                    ret += f'{SYM_T}{node.tree(prepend + SYM_BAR)}'

        return ret


class BareNamespace(Namespace):
    def __init__(self, name: Identifier | str, parent: Namespace = None):
        super().__init__([], name, parent)

    def __repr__(self) -> str:
        return f'BareNamespace[]'  # TODO bare ns repr


@dataclass
class Block(Node):
    nodes: list[Node]

    def __init__(self, tokens: list[Token], parent: Node):
        super().__init__(tokens, '$block', parent)
        self.nodes = []

        if isinstance(parent, (Inheritable, Namespace)):
            return

        while not self.take_specific('Operator', '}'):
            next = self.next

            if next.of('Special'):
                match next.string:
                    case 'alias':    self.nodes.append(self.make_alias())
                    case 'break':    self.make_break()
                    case 'continue': self.make_continue()
                    case 'del':      self.make_del()
                    case 'do':       self.make_do()
                    case 'for':      self.make_for()
                    case 'if':       self.make_if()
                    case 'mut':      self.nodes.append(self.make_declaration())
                    case 'return':   self.make_return()
                    case 'switch':   self.make_switch()
                    case 'try':      self.make_try()
                    case 'while':    self.make_while()
                    case 'with':     self.make_with()
                    case _:          self.error('unexpected keyword')

            elif next.of('Identifier'):
                index = self.index
                try:
                    self.nodes.append(self.make_declaration())
                except ParserError:
                    self.index = index
                    ...  # make accessor

            elif next.type_starter(False):
                self.nodes.append(self.make_declaration())

            elif next.of_has('Operator', '{'):
                self.nodes.append(self.make_block())

            elif self.take_specific('Operator', ';'):
                pass

            else:
                self.error('unexpected token')

    def __repr__(self) -> str:
        nodes = ' '.join([repr(n) for n in self.nodes])
        return f'Block[{nodes}]'

    def make_break(self):
        self.take()  # "break"

        tokens = []
        while not self.take_specific('Operator', ';'):
            tokens.append(self.take())
        self.nodes.append(Break(tokens, self))

    def make_continue(self):
        self.take()  # "continue"

        tokens = []
        while not self.take_specific('Operator', ';'):
            tokens.append(self.take())
        self.nodes.append(Continue(tokens, self))

    def make_del(self):
        self.take()  # "del"

        name = self.expect('Identifier')
        self.expect('Operator', ';')
        self.nodes.append(Del(name, self))

    def make_do(self):
        self.take()  # "do"

        block = self.make_block()
        while_expr = None
        if self.next.of_has('Special', 'while'):
            index = self.index
            self.take()  # "while"
            while_expr = self.make_paren()
            if not self.take_specific('Operator', ';'):
                self.index = index
                while_expr = None
        self.nodes.append(Do(block, while_expr, self))

    def make_for(self):
        self.take()  # "for"

        self.nodes.append(For(self.make_paren(), self.make_block(), self))

    def make_if(self):
        self.take()  # "if"

        expr = self.make_paren()
        block = self.make_block()
        else_ifs = []
        else_block = None
        while self.take_specific('Special', 'else'):
            if self.take_specific('Special', 'if'):
                else_ifs.append(If(self.make_paren(), self.make_block()))
                continue
            else_block = self.make_block()
        self.nodes.append(If(expr, block, else_ifs, else_block, self))

    def make_return(self):
        self.take()  # "return"

        tokens = []
        while not self.take_specific('Operator', ';'):
            tokens.append(self.take())
        self.nodes.append(Return(tokens, self))

    def make_switch(self):
        self.take()  # "switch"

        self.nodes.append(Switch(self.make_paren(), self.make_stack(None, '{', '}'), self))

    def make_try(self):
        self.take()  # "try"

        self.nodes.append(Try(
            self.make_block().tokens,
            self.make_block().tokens if self.take_specific('Special', 'catch') else [],
            self.make_block().tokens if self.take_specific('Special', 'finally') else [],
            self
        ))

    def make_while(self):
        self.take()  # "while"

        self.nodes.append(While(self.make_paren(), self.make_block(), self))

    def make_with(self):
        self.take()  # "with"

        expr = self.make_paren()
        id = None
        if self.take_specific('Special', 'as'):
            id = self.expect('Identifier')
        self.nodes.append(With(expr, id, self.make_block(), self))


class Statement(Node, ABC):
    def __init__(self, tokens: list[Token], parent: Node):
        Node.__init__(self, tokens, parent=parent)

    def __repr__(self) -> str:
        tokens = ' '.join([t.string for t in self.tokens])
        return f'{self.__class__.__name__}[{tokens}]'


@dataclass
class SimpleStatement(Statement):
    expr: Expression | None

    def __init__(self, tokens: list[Token], parent: Block):
        super().__init__(tokens, parent)
        self.expr = Expression(tokens, self) if tokens else None

    def __repr__(self) -> str:
        expr = repr(self.expr) if self.expr else ''
        return f'{self.__class__.__name__}[{expr}]'


class Break(SimpleStatement):
    def __init__(self, tokens: list[Token], parent: Block):
        super().__init__(tokens, parent)


@dataclass
class Inheritable(Node, ABC):
    abstract:          bool
    final:             bool
    inheritance:       list[Type]
    inheritance_nodes: dict[str, Inheritable]
    members:           list[Member]
    methods:           list[Method]
    modifier:          Token
    override_members:  list[Member]
    override_methods:  list[Method]

    def __init__(self, modifier: Token, name: Token, inheritance: list[Type], tokens: list[Token], parent: Namespace):
        Node.__init__(self, tokens, Identifier(name), parent)
        self.abstract          = False
        self.final             = False
        self.inheritance       = inheritance
        self.inheritance_nodes = {}
        self.members           = []
        self.methods           = []
        self.override_members  = []
        self.override_methods  = []

        if modifier:
            if modifier.of_has('Special', 'abstract'):
                self.abstract = True
            elif modifier.of_has('Special', 'final'):
                self.final = True
            else:
                self.error('unexpected modifier token')

    def make_member(self, modifiers: list[Token]) -> Member:
        member_type = self.make_type()
        name = self.expect('Identifier')

        tokens = []

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

        return Member(modifiers, member_type, name, tokens[:-1], self)

    def make_method(self, modifiers: list[Token]) -> Method:
        return_type = self.make_type()
        name = self.expect('Identifier')

        params = []

        self.expect('Operator', '(')

        if not self.take_specific('Operator', ')'):
            while True:
                if self.next.type_starter():
                    params.append(self.make_declaration())

                    if self.take_specific('Operator', ','):
                        continue
                    if self.take_specific('Operator', ')'):
                        break
                elif self.take_specific('Operator', ')'):
                    break
                else:
                    self.error('expected type')

        return Method(
            modifiers,
            return_type,
            name,
            params,
            [] if self.take_specific('Operator', ';') else self.make_block().tokens,
            self
        )

    def tree(self, prepend: str) -> str:
        ret = f'{self.__class__.__name__} "{self.name}"'

        has_others = self.inheritance or self.members or self.override_members or self.methods or self.override_methods
        if self.abstract or self.final:
            ret += f'\n{prepend}{SYM_T if has_others else SYM_L}{'abstract' if self.abstract else 'final'}'

        has_others = self.members or self.override_members or self.methods or self.override_methods
        inner_prepend = prepend + (SYM_BAR if has_others else SYM_SPACE)
        if self.inheritance_nodes:
            ret += f'\n{prepend}{SYM_T if has_others else SYM_L}inheritance'
            for i, (_, n) in enumerate(self.inheritance_nodes.items()):
                middle = i < len(self.inheritance_nodes) - 1
                ret += f'\n{inner_prepend}{SYM_T if middle else SYM_L}{
                    n.tree(inner_prepend + (SYM_BAR if middle else SYM_SPACE))}'

        has_others = self.override_members or self.methods or self.override_methods
        inner_prepend = prepend + (SYM_BAR if has_others else SYM_SPACE)
        if self.members:
            ret += f'\n{prepend}{SYM_T if has_others else SYM_L}members'
            for i, m in enumerate(self.members):
                middle = i < len(self.members) - 1
                ret += f'\n{inner_prepend}{SYM_T if middle else SYM_L}{
                    m.tree(inner_prepend + (SYM_BAR if middle else SYM_SPACE))}'

        has_others = self.methods or self.override_methods
        inner_prepend = prepend + (SYM_BAR if has_others else SYM_SPACE)
        if self.override_members:
            ret += f'\n{prepend}{SYM_T if has_others else SYM_L}override members'
            for i, m in enumerate(self.override_members):
                middle = i < len(self.override_members) - 1
                ret += f'\n{inner_prepend}{SYM_T if middle else SYM_L}{
                    m.tree(inner_prepend + (SYM_BAR if middle else SYM_SPACE))}'

        has_others = self.override_methods
        inner_prepend = prepend + (SYM_BAR if has_others else SYM_SPACE)
        if self.methods:
            ret += f'\n{prepend}{SYM_T if has_others else SYM_L}methods'
            for i, m in enumerate(self.methods):
                middle = i < len(self.methods) - 1
                ret += f'\n{inner_prepend}{SYM_T if middle else SYM_L}{
                    m.tree(SYM_BAR if middle else SYM_SPACE)}'

        inner_prepend = prepend + SYM_SPACE
        if self.override_methods:
            ret += f'\n{prepend}{SYM_L}override methods'
            for i, m in enumerate(self.override_methods):
                ret += f'\n{inner_prepend}{SYM_T if i < len(self.override_methods) - 1 else SYM_L}{
                    m.tree(SYM_BAR if i < len(self.override_methods) - 1 else SYM_SPACE)}'

        return ret


class Class(Inheritable):
    def __init__(self, modifier: Token, name: Token, inheritance: list[Token], tokens: list[Token], parent: Namespace):
        super().__init__(modifier, name, inheritance, tokens, parent)

        def inner(members: list[Member], methods: list[Method]):
            while not self.take_specific('Operator', '}'):
                mods = []
                if self.next.of('Special'):
                    if self.next.has('private', 'protected', 'final'):
                        mods.append(self.take())
                        if self.last.has('protected') and self.next.of_has('Special', 'final'):
                            mods.append(self.take())
                    elif not self.next.has('mut'):
                        self.error('unexpected keyword')

                if self.next.type_starter():
                    index = self.index
                    self.make_type()
                    self.expect('Identifier')
                    if self.take_specific('Operator', '('):
                        self.index = index
                        methods.append(self.make_method(mods))
                    else:
                        self.index = index
                        members.append(self.make_member(mods))
                elif self.take_specific('Operator', ';'):
                    pass
                else:
                    self.error('expected type')

        if self.take_specific('Special', 'override'):
            self.expect('Operator', '{')
            inner(self.override_members, self.override_methods)

        inner(self.members, self.methods)

    def __repr__(self) -> str:
        mod = 'abstract ' if self.abstract else 'final ' if self.final else ''
        inheritance = f' : {f', '.join([repr(i) for i in self.inheritance])}' if self.inheritance else ''
        members = ', '.join([repr(m) for m in self.members])
        methods = ', '.join([repr(m) for m in self.methods])
        return f'Class[{mod}{self.name}{inheritance} <{members}> <{methods}>]'


class Continue(SimpleStatement):
    def __init__(self, tokens: list[Token], parent: Block):
        super().__init__(tokens, parent)


@dataclass
class Declaration(Node):
    expr:     Expression | None
    node:     Node | None
    var_type: Type

    def __init__(self, var_type: Type, name: Token, tokens: list[Token], parent: Node):
        Node.__init__(self, tokens, Identifier(name), parent)
        self.expr     = Expression(tokens, self) if tokens else None
        self.node     = None
        self.var_type = var_type

        if not self.expr and self.var_type and self.var_type.name == 'auto':
            self.error('unable to infer auto type', self.var_type.token)

    def __repr__(self) -> str:
        expr = f' <{self.expr}>' if self.expr else ''
        return f'Declaration[{self.var_type} {self.name}{expr}]'

    def parse(self, parser: Parser):
        self.var_type.parse(parser)
        ...

    def tree(self, prepend: str) -> str:
        ret = f'Declaration "{self.path}"'

        ret += f'\n{prepend}{SYM_T if self.expr else SYM_L}'
        _prepend = prepend + (SYM_BAR if self.expr else SYM_SPACE)
        if self.node:
            ret += self.node.tree(_prepend)
        else:
            ret += self.var_type.tree(_prepend)

        if self.expr:
            ret += f'\n{prepend}{SYM_L}{self.expr.tree(prepend + SYM_SPACE)}'

        return ret


class Del(Statement):
    def __init__(self, id: Token, parent: Block):
        super().__init__([id], parent)

    def __repr__(self) -> str:
        return f'Del[{self.token.string if self.token else ''}]'


@dataclass
class Do(Statement):
    block:      Block
    while_expr: Paren | None

    def __init__(self, block: Block, while_expr: Paren = None, parent: Block = None):
        super().__init__([], parent)
        self.block      = block
        self.while_expr = while_expr

    def __repr__(self) -> str:
        while_expr = f' While[{repr(self.while_expr)}]' if self.while_expr else ''
        return f'Do[{repr(self.block)}{while_expr}]'


@dataclass
class Enum(Node):
    elements: list[EnumElement]

    def __init__(self, elements: list[EnumElement], name: Token, parent: Namespace):
        super().__init__(name=Identifier(name), parent=parent)
        self.elements = elements

        values = set()
        for e in self.elements:
            e.parent = self
            if e.value in values:
                self.error('duplicate enum value', e.token)
            values.add(e.value)

    def __repr__(self) -> str:
        return f'Enum[{self.path} <{self.elements}>]'

    def tree(self, prepend: str) -> str:
        ret = f'Enum "{self.path}"'

        for i, e in enumerate(self.elements):
            ret += f'\n{prepend}{SYM_T if i < len(self.elements) - 1 else SYM_L}{e.name}({e.value})'

        return ret


@dataclass
class EnumElement(Node):
    value: int

    def __init__(self, name: Token, value: int = 0, token: Token = None):
        super().__init__([token] if token else [], Identifier(name))
        self.value = value

    def __repr__(self) -> str:
        return f'EnumElement[{self.name} = {self.value}]'


@dataclass
class ParenStatement(Statement):
    expr:  Paren
    block: Block

    def __init__(self, expr: Paren, block: Block, parent: Block | Switch):
        super().__init__([], parent)
        self.expr  = expr
        self.block = block

    def __repr__(self) -> str:
        expr = repr(self.expr) if self.expr else ''
        block = repr(self.block) if self.block else ''
        space = ' ' if expr and block else ''
        return f'{self.__class__.__name__}[{expr}{space}{block}]'


@dataclass
class For(ParenStatement):
    it_type: Type
    it_id:   Token
    it_expr: Expression

    def __init__(self, expr: Paren, block: Block, parent: Block):
        super().__init__(expr, block, parent)

        self.tokens = expr.tokens
        self.it_type = self.make_type()
        self.it_id = self.expect('Identifier')
        self.expect('Special', 'in')
        self.it_expr = Expression(self.tokens[self.index:-1], self)


@dataclass
class Function(Node):
    block:       Block
    params:      list[Declaration]
    return_type: Type

    def __init__(
        self,
        return_type: Type,
        name:        Token,
        params:      list[Declaration],
        tokens:      list[Token] = [],
        parent:      Namespace   = None
    ):
        self.return_type = return_type
        if name is not None:
            super().__init__(tokens, Identifier(name), parent)
        self.params = params
        for p in self.params:
            p.parent = self
        self.tokens = tokens
        self.block = Block(tokens, self)
        self.parent = self.parent or parent

    def __repr__(self) -> str:
        params = f' <{', '.join([repr(p) for p in self.params])}>' if self.params else ''
        return f'Function[{self.return_type} {self.name}{params} {repr(self.block)}]'


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
        return f'Identifier[{self.name}]'

    def __str__(self) -> str:
        return self.name


@dataclass
class Type(Identifier):
    held_type: Type | None
    mut:       bool
    node:      Node | None
    primitive: bool
    tokens:    list[Token]

    def __init__(self, token: Token | list[Token], held_type: Type = None):
        self.held_type = held_type
        if type(token) is Token:
            self.token  = token
            self.tokens = []
            self.name   = token.string
        else:
            self.token  = token[0]
            self.tokens = token
            self.name   = ''.join([t.string for t in self.tokens])

        if not self.token.type_starter()\
            and not self.token.of_has('Operator', '@')\
            and not self.token.of_has('Operator', '<'):
            raise ParserError(self.token, 'expected type')

        self.mut = self.token.of_has('Special', 'mut')
        if self.mut:
            if len(self.tokens) == 1:
                raise ParserError(self.token, 'expected type after "mut" keyword')
            self.name = f'mut {self.name[3:]}'

        self.node = None

        self.primitive = False
        for token in self.tokens:
            if token.of('Type'):
                self.primitive = True
                break

    def __repr__(self) -> str:
        return f'Type[{self.name}]'

    def parse(self, parser: Parser, path: str = ''):
        if self.primitive:
            if self.held_type:
                raise ParserError('primitives cannot hold other types', self.held_type.tokens)
            return

        if self.held_type:
            self.held_type.parse(parser)

        name = self.name
        if name.startswith('mut '):
            name = name[4:]
        if name.startswith('global.'):
            name = name[7:]
        if name.startswith('@'):
            name = name[1:]
        if name.endswith('&'):
            name = name[:-1]

        parts = [t.string for t in self.tokens]

        if name in parser.global_ns.nodes:
            self.node = parser.global_ns.nodes[name]

    def tree(self, prepend: str) -> str:
        return self.node.tree(prepend) if self.node else self.name


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
        self.primitive = False

        self.name = f'<{self.return_type}><{', '.join([t.name for t in self.param_types])}>'

    def __repr__(self) -> str:
        return f'FunctionType[{self.name}]'


@dataclass
class If(ParenStatement):
    else_ifs:   list[If]
    else_block: Block | None

    def __init__(
        self,
        expr:       Paren,
        block:      Block,
        else_ifs:   list[If] = [],
        else_block: Block    = None,
        parent:     Block    = None
    ):
        super().__init__(expr, block, parent)
        self.else_ifs = else_ifs
        for e in else_ifs:
            e.parent = self
        self.else_block = else_block

    def __repr__(self) -> str:
        else_ifs = f' Else[{' '.join([repr(e) for e in self.else_ifs])}]' if self.else_ifs else ''
        else_block = f' Else[{repr(self.else_block)}]' if self.else_block else ''
        return f'If[{repr(self.expr)} {repr(self.block)}{else_ifs}{else_block}]'


class Interface(Inheritable):
    def __init__(self, modifier: Token, name: Token, inheritance: list[Token], tokens: list[Token], parent: Namespace):
        super().__init__(modifier, name, inheritance, tokens, parent)

        def inner(methods: list[Method]):
            while not self.take_specific('Operator', '}'):
                mods = []
                if self.next.of('Special'):
                    if self.next.has('private', 'protected', 'final'):
                        mods.append(self.take())
                        if self.last.has('protected') and self.next.of_has('Special', 'final'):
                            mods.append(self.take())
                    else:
                        self.error('unexpected keyword')

                if self.next.type_starter():
                    methods.append(self.make_method(mods))
                elif self.take_specific('Operator', ';'):
                    pass
                else:
                    self.error('expected type')

        if self.take_specific('Special', 'override'):
            self.expect('Operator', '{')
            inner(self.override_methods)

        inner(self.methods)

    def __repr__(self) -> str:
        mod = 'abstract ' if self.abstract else 'final ' if self.final else ''
        inheritance = f' : {f', '.join([repr(i) for i in self.inheritance])}' if self.inheritance else ''
        methods = ', '.join([repr(m) for m in self.methods])
        return f'Interface[{mod}{self.name}{inheritance} <{methods}>]'


@dataclass
class Member(Declaration):
    final:     Token | None
    modifiers: list[Token]
    private:   Token | None
    protected: Token | None

    def __init__(
        self,
        modifiers: list[Token],
        var_type:  Type,
        name:      Token,
        tokens:    list[Token],
        parent:    Inheritable
    ):
        super().__init__(var_type, name, tokens, parent)
        self.modifiers = modifiers

        self.final     = None
        self.private   = None
        self.protected = None
        for m in self.modifiers:
            if m.has('final'):
                self.final = m
            elif m.has('private'):
                self.private = m
            elif m.has('protected'):
                self.protected = m

    def __repr__(self) -> str:
        modifiers = f'<{' '.join([m.string for m in self.modifiers])}> ' if self.modifiers else ''
        return f'Member[{modifiers}{self.var_type} {self.name}]'


@dataclass
class Method(Member, Function):
    abstract: bool

    def __init__(
        self,
        modifiers:   list[Token],
        return_type: Type,
        name:        Token,
        params:      list[Declaration],
        tokens:      list[Token],
        parent:      Class | Interface
    ):
        Member.__init__(self, modifiers, None, name, [], parent)
        Function.__init__(self, return_type, None, params, tokens)

        self.abstract = not self.tokens

        if self.abstract:
            if self.final:
                self.error('abstract methods cannot be final', self.final)
            if self.private:
                self.error('abstract methods cannot be private', self.private)

    def __repr__(self) -> str:
        modifiers = f'<{' '.join([m.string for m in self.modifiers])}> ' if self.modifiers else ''
        return f'Method[{modifiers}{Function.__repr__(self).replace('Function[', '')}'

    def parse(self, parser: Parser):
        Function.parse(self, parser)

    def tree(self, prepend: str) -> str:
        return Function.tree(self, prepend)


class Paren(Expression):
    def __init__(self, tokens: list[Token], parent: Node):
        super().__init__(tokens, parent)


@dataclass
class Parser:
    global_ns:  Namespace
    output_dir: str
    tokens:     list[Token]
    unimpl:     set[str]

    def __init__(self, tokens: list[Token], output_dir: str = ''):
        self.tokens     = tokens
        self.output_dir = output_dir
        self.unimpl     = set()

    def next(self) -> Token:
        return self.tokens[self.index]

    def parse(self) -> None:
        print(f'parsing {len(self.tokens)} tokens in "global"')
        self.global_ns = Namespace(self.tokens, 'global')
        self.global_ns.parse(self)  # 2nd+ passes

    def take(self) -> Token:
        token = self.next()
        self.index += 1
        return token

    def write_debug(self) -> None:
        if not self.output_dir:
            raise LanguageError('no output folder given')

        with open(
            os.path.join(self.output_dir, '3_parser.cakedebug'),
            'w',
            encoding='utf-8',
            newline='\n'
        ) as f:
            f.write(debug_header('step 3: parser'))

            f.write('functions:\n')
            for fn in self.global_ns.functions:
                f.write(f'\t{repr(fn)}\n')

            f.write('-' * 50 + '\n')
            tree = self.global_ns.tree('')
            f.write(tree + '\n')


class ParserError(LanguageError):
    def __init__(self, token: Token | list[Token], *args):
        locale = []
        tokens = ''
        if type(token) is Token:
            locale = token.locale.copy()
            tokens = str(token)
        else:
            locale = [token[0].locale[0], token[-1].locale[1]]
            tokens = ' '.join([str(t) for t in token])
            token = token[0]

        line = token.line.string
        indent = 0
        for char in line:
            if char.isspace():
                indent += 1
            else:
                break
        locale[0] -= indent
        locale[1] -= indent
        line = line.lstrip(' ').rstrip('\n').rstrip('\r')
        marks = '~' * locale[0] + '^' * (locale[1] - locale[0])
        super().__init__(f'{token.loc()} | {tokens} | {' '.join(args)}\n  {line}\n  {marks}')


class Return(SimpleStatement):
    def __init__(self, tokens: list[Token], parent: Block):
        super().__init__(tokens, parent)


class StdNamespace(BareNamespace):
    def __init__(self, parent: Namespace):
        super().__init__('std', parent)

    def __repr__(self) -> str:
        return f'StdNamespace[]'  # TODO std ns repr


class Struct(Inheritable):
    def __init__(self, modifier: Token, name: Token, inheritance: list[Token], tokens: list[Token], parent: Namespace):
        super().__init__(modifier, name, inheritance, tokens, parent)

        def inner(members: list[Member]):
            while not self.take_specific('Operator', '}'):
                mods = []
                if self.next.of('Special'):
                    if self.next.has('private', 'protected', 'final'):
                        mods.append(self.take())
                        if self.last.has('protected') and self.next.of_has('Special', 'final'):
                            mods.append(self.take())
                    else:
                        self.error('unexpected keyword')

                if self.next.type_starter():
                    members.append(self.make_member(mods))
                elif self.take_specific('Operator', ';'):
                    pass
                else:
                    self.error('expected type')

        if self.take_specific('Special', 'override'):
            self.expect('Operator', '{')
            inner(self.override_members)

        inner(self.members)

    def __repr__(self) -> str:
        mod = 'abstract ' if self.abstract else 'final ' if self.final else ''
        inheritance = f' : {f', '.join([repr(i) for i in self.inheritance])}' if self.inheritance else ''
        members = ', '.join([repr(m) for m in self.members])
        return f'Struct[{mod}{self.name}{inheritance} <{members}>]'


@dataclass
class Switch(ParenStatement):
    cases: list[SwitchCase]

    def __init__(self, expr: Paren, tokens: list[Token], parent: Block):
        super().__init__(expr, None, parent)
        self.tokens = tokens

        self.cases = []
        while not self.take_specific('Operator', '}'):
            if self.take_specific('Special', 'case'):
                self.cases.append(SwitchCase(self.make_paren(), self.make_block(), self))
            elif self.take_specific('Special', 'default'):
                self.cases.append(SwitchCase(None, self.make_block(), self))
                self.expect('Operator', '}')
                break
            else:
                self.error('unexpected token in switch')

    def __repr__(self) -> str:
        return f'Switch[{' '.join([repr(c) for c in self.cases])}]'


class SwitchCase(ParenStatement):
    def __init__(self, expr: Paren, block: Block, parent: Switch):
        super().__init__(expr, block, parent)


@dataclass
class Try(Statement):
    block:         Block
    catch_block:   Block | None
    finally_block: Block | None

    def __init__(self, block: list[Token], catch_block: list[Token], finally_block: list[Token], parent: Block):
        super().__init__(block + catch_block + finally_block, parent)
        self.block         = Block(block, self)
        self.catch_block   = Block(catch_block, self) if catch_block else None
        self.finally_block = Block(finally_block, self) if finally_block else None

    def __repr__(self) -> str:
        catch_block = f' Catch[{repr(self.catch_block)}]' if self.catch_block else ''
        finally_block = f' Finally[{repr(self.finally_block)}]' if self.finally_block else ''
        return f'Try[{repr(self.block)}{catch_block}{finally_block}]'


@dataclass
class Union(Node):
    elements: list[UnionElement]
    params:   list[Declaration]

    def __init__(self, params: list[Declaration], tokens: list[Token], name: Token, parent: Namespace):
        super().__init__(tokens, Identifier(name), parent)
        self.params = params
        for p in self.params:
            p.parent = self

        self.elements = []

        if not self.tokens:
            return

        self.tokens.append(Token('EOF', None))

        used = set()

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
                            if held.string == (name := str(p.name)):
                                found = True
                                if name in used:
                                    self.error('union parameter already used', held)
                                used.add(name)
                                self.elements.append(UnionElement(element_name, self, p))
                                break
                        if not found:
                            self.error('union parameter not found', held)
                        self.expect('Operator', ')')
                        self.take_specific('Operator', ',')
                    else:
                        self.error('expected identifier')

        for p in self.params:
            if str(p.name) not in used:
                self.error('unused union parameter', p.var_type.token)

    def __repr__(self) -> str:
        params = ', '.join([repr(p) for p in self.params])
        elements = ', '.join([repr(e) for e in self.elements])
        return f'Union[{self.path} <{params}> <{elements}>]'

    def parse(self, parser: Parser):
        for p in self.params:
            p.parse(parser)

    def tree(self, prepend: str) -> str:
        ret = f'Union "{self.path}"'

        if self.params:
            ret += f'\n{prepend}{SYM_T if self.elements else SYM_L}params'
            for i, p in enumerate(self.params):
                _prepend = prepend + (SYM_BAR if self.elements else SYM_SPACE)
                middle = i < len(self.params) - 1
                ret += f'\n{_prepend}{SYM_T if middle else SYM_L}{
                    p.var_type.tree(_prepend + (SYM_BAR if middle else SYM_SPACE))}'

        if self.elements:
            ret += f'\n{prepend}{SYM_L}elements'
            for i, e in enumerate(self.elements):
                middle = i < len(self.elements) - 1
                ret += f'\n{prepend}{SYM_SPACE}{SYM_T if middle else SYM_L}{
                    e.name}{f'({e.param.name})' if e.param else ''}'

        return ret


@dataclass
class UnionElement(Node):
    param: Declaration

    def __init__(self, name: Token, parent: Union, param: Declaration = None):
        super().__init__(name=Identifier(name), parent=parent)
        self.param = param

    def __repr__(self) -> str:
        param = f'<{self.param.name}>' if self.param else ''
        return f'UnionElement[{self.name}{param}]'


class While(ParenStatement):
    def __init__(self, expr: Paren, block: Block, parent: Block):
        super().__init__(expr, block, parent)


@dataclass
class With(ParenStatement):
    id: Identifier | None

    def __init__(self, expr: ParenStatement, id: Token | None, block: Block, parent: Block):
        super().__init__(expr, block, parent)
        self.id = Identifier(id) if id else None

    def __repr__(self) -> str:
        id = f' as {self.id}' if self.id else ''
        return f'With[{repr(self.expr)}{id} {repr(self.block)}]'
