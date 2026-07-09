from ..node import Node, PrimaryNode


class Number(PrimaryNode):
    @classmethod
    def construct(cls, parser) -> Number:
        return Number(parser.expecting_of('Number'))


class PrimaryExpression(Node):
    def __init__(self, left, expression, right):
        self.left       = left
        self.expression = expression
        self.right      = right

    def nodes(self) -> list[Node]:
        return [self.left, self.expression, self.right]

    @classmethod
    def construct(cls, parser) -> Node:
        if not parser.next().has('(', '|', '_', '^'):
            return Number.construct(parser)

        left = parser.take()
        expression = parser.expression.construct(parser)
        right = parser.expecting_has(')' if left.has('(') else left.string)

        return PrimaryExpression(left, expression, right)
