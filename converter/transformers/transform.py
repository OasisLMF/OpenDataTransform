import re
from functools import partial
from operator import add, mul, sub
from operator import truediv as div
from typing import Any, Callable, TypedDict, Union

from lark import Transformer as _LarkTransformer
from lark import Tree, v_args

from .grammar import parser


RowType = Any


class TransformerMapping(TypedDict, total=False):
    lookup: Callable[[RowType, str], Any]

    # math opperators
    add: Callable[[RowType, Any, Any], Any]
    subtract: Callable[[RowType, Any, Any], Any]
    multiply: Callable[[RowType, Any, Any], Any]
    divide: Callable[[RowType, Any, Any], Any]

    # comparison operators
    eq: Callable[[RowType, Any, Any], Any]
    not_eq: Callable[[RowType, Any, Any], Any]
    is_in: Callable[[RowType, Any, Any], Any]
    not_in: Callable[[RowType, Any, Any], Any]
    gt: Callable[[RowType, Any, Any], Any]
    gte: Callable[[RowType, Any, Any], Any]
    lt: Callable[[RowType, Any, Any], Any]
    lte: Callable[[RowType, Any, Any], Any]
    logical_and: Callable[[RowType, Any, Any], Any]
    logical_or: Callable[[RowType, Any, Any], Any]
    logical_not: Callable[[RowType, Any], Any]


def parse(expression):
    return parser.parse(expression)


def create_transformer_class(row, transformer_mapping):
    transformer_mapping = {
        "lookup": lambda r, name: r[name],
        "add": lambda r, lhs, rhs: add(lhs, rhs),
        "subtract": lambda r, lhs, rhs: sub(lhs, rhs),
        "multiply": lambda r, lhs, rhs: mul(lhs, rhs),
        "divide": lambda r, lhs, rhs: div(lhs, rhs),
        "eq": lambda r, lhs, rhs: lhs == rhs,
        "not_eq": lambda r, lhs, rhs: lhs != rhs,
        "is_in": lambda r, lhs, rhs: lhs in rhs,
        "not_in": lambda r, lhs, rhs: lhs not in rhs,
        "gt": lambda r, lhs, rhs: lhs > rhs,
        "gte": lambda r, lhs, rhs: lhs >= rhs,
        "lt": lambda r, lhs, rhs: lhs < rhs,
        "lte": lambda r, lhs, rhs: lhs <= rhs,
        "logical_or": lambda r, lhs, rhs: lhs or rhs,
        "logical_and": lambda r, lhs, rhs: lhs and rhs,
        "logical_not": lambda r, v: not v,
        **(transformer_mapping or {}),
    }

    def mapped_function(name, *args, **kwargs):
        return transformer_mapping[name](row, *args, **kwargs)

    @v_args(inline=True)
    class TreeTransformer(_LarkTransformer):
        number = float
        array = v_args(inline=False)(list)
        string_escape_re = re.compile(r"`([`'])")

        def string(self, value=""):
            """
            `value` has a default value to account for the empty string case
            :param name:
            :return:
            """
            # process any escape characters
            return self.string_escape_re.sub(r"\1", value)

        def boolean(self, value):
            return value == "True"

        lookup = partial(mapped_function, "lookup")
        add = partial(mapped_function, "add")
        subtract = partial(mapped_function, "subtract")
        multiply = partial(mapped_function, "multiply")
        divide = partial(mapped_function, "divide")
        eq = partial(mapped_function, "eq")
        not_eq = partial(mapped_function, "not_eq")
        is_in = partial(mapped_function, "is_in")
        not_in = partial(mapped_function, "not_in")
        gt = partial(mapped_function, "gt")
        gte = partial(mapped_function, "gte")
        lt = partial(mapped_function, "lt")
        lte = partial(mapped_function, "lte")
        logical_not = partial(mapped_function, "logical_not")
        logical_or = partial(mapped_function, "logical_or")
        logical_and = partial(mapped_function, "logical_and")

    return TreeTransformer


def transform(row, tree, transformer_mapping):
    transformer_class = create_transformer_class(row, transformer_mapping)
    transformer = transformer_class()

    return transformer.transform(tree)


def run(
    row,
    expression: Union[str, Tree],
    transformer_mapping: TransformerMapping = None,
):
    if isinstance(expression, str):
        expression = parse(expression)

    return transform(row, expression, transformer_mapping)
