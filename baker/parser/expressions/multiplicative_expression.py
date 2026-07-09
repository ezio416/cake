from .exponential_expression import ExponentialExpression
from ..node import BinaryNode, Node


class MultiplicativeExpression(BinaryNode):
    @classmethod
    def construct(cls, parser) -> Node:
        return cls.construct_binary(parser, cls, ExponentialExpression, ['*', '/', '%'])
