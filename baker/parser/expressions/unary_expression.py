from .primary_expression import PrimaryExpression
from ..node import Node


class UnaryExpression(Node):
    def __init__(self, op, expression):
        self.op         = op
        self.expression = expression

    def nodes(self) -> list[Node]:
        return [self.op, self.expression]

    @classmethod
    def construct(cls, parser) -> Node:
        if parser.next().has('+', '-', '~'):
            op = parser.take()
            expression = UnaryExpression.construct(parser)
            return UnaryExpression(op, expression)

        return PrimaryExpression.construct(parser)
