import re
from operator import add, mul, sub
from operator import truediv as div
from typing import Any, Callable, TypedDict

from lark import Transformer as _LarkTransformer
from lark import v_args

from .grammar import parser


RowType = Any


class TransformerMapping(TypedDict):
    lookup: Callable[[RowType, str], Any]
    add: Callable[[Any, Any], Any]
    subtract: Callable[[Any, Any], Any]
    multiply: Callable[[Any, Any], Any]
    divide: Callable[[Any, Any], Any]


@v_args(inline=True)
class TreeTransformer(_LarkTransformer):
    float = float
    integer = int
    string_escape_re = re.compile(r"`([`'])")

    def __init__(self, row, transformer_mapping):
        super().__init__()

        self.row = row
        self.transformer_mapping = transformer_mapping

    def negative(self, value):
        return -value

    def string(self, value=""):
        """
        `value` has a default value to account for the empty string case
        :param name:
        :return:
        """
        # process any escape characters
        return self.string_escape_re.sub(r"\1", value)

    def lookup(self, name):
        return self.transformer_mapping["lookup"](self.row, name)

    def add(self, lhs, rhs):
        return self.transformer_mapping["add"](lhs, rhs)

    def subtract(self, lhs, rhs):
        return self.transformer_mapping["subtract"](lhs, rhs)

    def multiply(self, lhs, rhs):
        return self.transformer_mapping["multiply"](lhs, rhs)

    def divide(self, lhs, rhs):
        return self.transformer_mapping["divide"](lhs, rhs)


def run(
    row, expression: str, transformer_mapping: TransformerMapping = None,
):
    transformer = TreeTransformer(
        row,
        {
            "lookup": lambda r, name: r[name],
            "add": add,
            "subtract": sub,
            "multiply": mul,
            "divide": div,
            **(transformer_mapping or {}),
        },
    )
    tree = parser.parse(expression)
    return transformer.transform(tree)
