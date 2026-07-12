from .unary_expression import UnaryExpression
from ..node import BinaryNode, Node


class ExponentialExpression(BinaryNode):
    @classmethod
    def construct(cls, parser) -> Node:
        node = UnaryExpression.construct(parser)

        if not parser.next().has('**'):
            return node

        op = parser.take()
        right = ExponentialExpression.construct(parser)
        return ExponentialExpression(node, op, right)
