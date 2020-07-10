import re
from functools import partial
from operator import add, mul, sub
from operator import truediv as div
from typing import Any, Callable, Iterable, List, TypedDict, Union

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

    # groupings
    all: Callable[[RowType, List[Any]], Any]
    any: Callable[[RowType, List[Any]], Any]


class GroupWrapper:
    check_fn: Callable[[Iterable[Any]], Any]

    def __init__(self, values):
        self.values = values

    def eq_operator(self, lhs, rhs):
        return lhs == rhs

    def __eq__(self, other):
        return self.check_fn(self.eq_operator(v, other) for v in self.values)

    def __ne__(self, other):
        return self.check_fn(
            not self.eq_operator(v, other) for v in self.values
        )

    def gt_operator(self, lhs, rhs):
        return lhs > rhs

    def __gt__(self, other):
        return self.check_fn(self.gt_operator(v, other) for v in self.values)

    def gte_operator(self, lhs, rhs):
        return lhs >= rhs

    def __ge__(self, other):
        return self.check_fn(self.gte_operator(v, other) for v in self.values)

    def lt_operator(self, lhs, rhs):
        return lhs < rhs

    def __lt__(self, other):
        return self.check_fn(self.lt_operator(v, other) for v in self.values)

    def lte_operator(self, lhs, rhs):
        return lhs <= rhs

    def __le__(self, other):
        return self.check_fn(self.lte_operator(v, other) for v in self.values)

    def in_operator(self, a, b):
        return a in b

    def is_in(self, other):
        return self.check_fn(self.in_operator(v, other) for v in self.values)

    def not_in_operator(self, a, b):
        return a not in b

    def is_not_in(self, other):
        return self.check_fn(
            self.not_in_operator(v, other) for v in self.values
        )


class AnyWrapper(GroupWrapper):
    check_fn = any


class AllWrapper(GroupWrapper):
    check_fn = all


def parse(expression):
    return parser.parse(expression)


def default_in_transformer(lhs, rhs):
    if hasattr(lhs, "is_in"):
        return lhs.is_in(rhs)
    else:
        return lhs in rhs


def default_not_in_transformer(lhs, rhs):
    if hasattr(lhs, "is_not_in"):
        return lhs.is_not_in(rhs)
    else:
        return lhs not in rhs


def create_transformer_class(row, transformer_mapping):
    transformer_mapping = {
        "lookup": lambda r, name: r[name],
        "add": lambda r, lhs, rhs: add(lhs, rhs),
        "subtract": lambda r, lhs, rhs: sub(lhs, rhs),
        "multiply": lambda r, lhs, rhs: mul(lhs, rhs),
        "divide": lambda r, lhs, rhs: div(lhs, rhs),
        "eq": lambda r, lhs, rhs: lhs == rhs,
        "not_eq": lambda r, lhs, rhs: lhs != rhs,
        "is_in": lambda r, lhs, rhs: default_in_transformer(lhs, rhs),
        "not_in": lambda r, lhs, rhs: default_not_in_transformer(lhs, rhs),
        "gt": lambda r, lhs, rhs: lhs > rhs,
        "gte": lambda r, lhs, rhs: lhs >= rhs,
        "lt": lambda r, lhs, rhs: lhs < rhs,
        "lte": lambda r, lhs, rhs: lhs <= rhs,
        "logical_or": lambda r, lhs, rhs: lhs or rhs,
        "logical_and": lambda r, lhs, rhs: lhs and rhs,
        "logical_not": lambda r, v: not v,
        "any": lambda r, v: AnyWrapper(v),
        "all": lambda r, v: AllWrapper(v),
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
        any = partial(mapped_function, "any")
        all = partial(mapped_function, "all")

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
