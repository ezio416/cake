from abc import ABC, abstractmethod


class Node(ABC):
    @property
    def line(self):
        return self.nodes()[0].line

    def __repr__(self) -> str:
        return self.tree_repr()

    def tree_repr(self, prefix: str = '\t') -> str:
        string = type(self).__name__
        nodes = self.nodes()

        for i, node in enumerate(nodes):
            at_last = (i == len(nodes) - 1)
            symbol = '└──' if at_last else '├──'
            prefix_symbol = '' if at_last else '│'

            node_string = node.tree_repr(f'{prefix}{prefix_symbol}\t')
            string += f'\n{prefix}{symbol} {node_string}'

        return string

    @abstractmethod
    def nodes(self) -> list[Node]:
        pass

    @classmethod
    @abstractmethod
    def construct(cls, parser):
        pass


class PrimaryNode(Node, ABC):
    def __init__(self, token):
        self.token = token

    def nodes(self):
        return [self.token]

    def tree_repr(self, prefix: str = '\t'):
        return f'{type(self).__name__} ── {self.token}'


class BinaryNode(Node, ABC):
    def __init__(self, left, op, right):
        self.left  = left
        self.op    = op
        self.right = right

    def nodes(self) -> list[Node]:
        return [self.left, self.op, self.right]

    @classmethod
    def construct_binary(cls, parser, make, part: Node, ops: list[str]):
        node = part.construct(parser)

        while parser.next().has(*ops):
            op = parser.take()
            right = part.construct(parser)
            node = make(node, op, right)

        return node
