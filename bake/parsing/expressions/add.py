# c 2025-01-04
# m 2025-01-04

from .multiply import MultiplicativeExpression
from ..node import BinaryNode


class AdditiveExpression(BinaryNode):
    @classmethod
    def construct(cls, parser):
        return cls.construct_binary(parser, cls, MultiplicativeExpression, ['+', '-'])
