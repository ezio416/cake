# c 2025-01-04
# m 2025-01-04

from .unary import UnaryExpression
from ..node import BinaryNode


class ExponentialExpression(BinaryNode):
    @classmethod
    def construct(cls, parser):
        node = UnaryExpression.construct(parser)

        if not parser.next().has('**'):
            return node

        op = parser.take()
        right = ExponentialExpression.construct(parser)
        return ExponentialExpression(node, op, right)
