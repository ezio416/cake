# c 2025-01-04
# m 2025-01-04

from abc import ABC

from .add import AdditiveExpression
from ..node import Node


class Expression(Node, ABC):
    @classmethod
    def construct(cls, parser):
        return AdditiveExpression.construct(parser)
