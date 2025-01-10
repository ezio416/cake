# c 2025-01-04
# m 2025-01-04

from math import ceil, floor

from ..node import Node, PrimaryNode


class PrimaryExpression(Node):
    def __init__(self, left, expression, right):
        self.left       = left
        self.expression = expression
        self.right      = right

    def nodes(self) -> list:
        return [self.left, self.expression, self.right]

    @classmethod
    def construct(cls, parser):
        next = parser.next()
        if not next.has(*'<[{(|_^'):
            return Number.construct(parser)

        left = parser.take()
        expression = parser.expression.construct(parser)

        if left.has('<'):
            right = parser.expecting_has('>')
        elif left.has('['):
            right = parser.expecting_has(']')
        elif left.has('{'):
            right = parser.expecting_has('}')
        elif left.has('('):
            right = parser.expecting_has(')')
        else:
            right = parser.expecting_has(left.string)

        return PrimaryExpression(left, expression, right)


class Number(PrimaryNode):
    @classmethod
    def construct(cls, parser):
        return Number(parser.expecting_of('Number'))


class Identifier(PrimaryNode):
    @classmethod
    def construct(cls, parser):
        return Identifier(parser.expecting_of('Identifier'))
