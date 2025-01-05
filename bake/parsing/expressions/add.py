# c 2025-01-04
# m 2025-01-04

from .multiply import MultiplicativeExpression
from ..node import BinaryNode


class AdditiveExpression(BinaryNode):
    @classmethod
    def construct(cls, parser):
        return cls.construct_binary(parser, cls, MultiplicativeExpression, ['+', '-'])

    def interpret(self):
        left = self.left.interpret()
        right = self.right.interpret()

        return left - right if self.op.has('-') else left + right
