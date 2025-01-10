# c 2025-01-04
# m 2025-01-04

from abc import ABC, abstractmethod


class Node(ABC):
    @property
    def line(self):
        return self.nodes()[0].line

    @abstractmethod
    def nodes(self):
        pass

    def __repr__(self) -> str:
        return self.tree_repr()

    def tree_repr(self, prefix: str = '    '):
        string: str = type(self).__name__
        nodes = self.nodes()

        for i, node in enumerate(nodes):
            at_last:       bool = i == len(nodes) - 1
            symbol:        str  = '└─' if at_last else '├─'
            prefix_symbol: str  = '' if at_last else '│'

            node_string: str = node.tree_repr(f'{prefix}{prefix_symbol}    ')
            string += f'\n{prefix}{symbol} {node_string}'

        return string

    def mark(self) -> None:
        for node in self.nodes():
            node.mark()

    @classmethod
    @abstractmethod
    def construct(cls, parser):
        pass


class PrimaryNode(Node, ABC):
    def __init__(self, token):
        self.token = token

    def nodes(self) -> list:
        return [self.token]

    def tree_repr(self, prefix = '    '):
        return f'{type(self).__name__} ── {self.token}'


class BinaryNode(Node, ABC):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def nodes(self):
        return [self.left, self.op, self.right]

    @classmethod
    def construct_binary(cls, parser, make, part: Node, ops):
        node = part.construct(parser)

        while parser.next().has(*ops):
            op = parser.take()
            right = part.construct(parser)
            node = make(node, op, right)

        return node
