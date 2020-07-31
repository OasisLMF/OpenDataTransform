import re
from functools import partial
from operator import add, mul, sub
from operator import truediv as div
from typing import Any, Callable, Iterable, List, Pattern, TypedDict, Union

from lark import Transformer as _LarkTransformer
from lark import Tree
from lark import exceptions as lark_exceptions
from lark import v_args

from .errors import UnexpectedCharacters
from .grammar import parser


RowType = Any


class TransformerMapping(TypedDict, total=False):
    lookup: Callable[[RowType, str], Any]

    # math operators
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

    # string manipulations
    str_join: Callable[..., Any]
    str_replace: Callable[[RowType, Any, Pattern, str], Any]
    str_match: Callable[[RowType, Any, Pattern], Any]
    str_search: Callable[[RowType, Any, Pattern], Any]


class GroupWrapper:
    """
    Group operations preformed on a list of elements

    :param values: A list of the grouped values
    """

    def __init__(self, values):
        self.values = values

    def check_fn(self, checks: Iterable[Any]):
        """
        Checks the results of the operator. This should be a reduction of each
        result in the values list into a single value.

        :param checks: The results from the operator comparison

        :return: The reduced result
        """
        raise NotImplementedError()

    def eq_operator(self, lhs, rhs):
        """
        Checks the equality of elements

        :param lhs: The left hand side of the operator
        :param rhs: The right hand side of the operator

        :return: True if the elements are equal, False otherwise
        """
        return lhs == rhs

    def __eq__(self, other):
        """
        Checks if the group equals the other based on the `check_fn` and
        `eq_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(self.eq_operator(v, other) for v in self.values)

    def __ne__(self, other):
        """
        Checks if the group does not equal the other based on the `check_fn`
        and the inverse of the `eq_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(
            not self.eq_operator(v, other) for v in self.values
        )

    def gt_operator(self, lhs, rhs):
        """
        Checks the left hand side of the operator is greater than the right
        hand side

        :param lhs: The left hand side of the operator
        :param rhs: The right hand side of the operator

        :return: True if lhs > rhs, False otherwise
        """
        return lhs > rhs

    def __gt__(self, other):
        """
        Checks if the group is greater than the other based on the `check_fn`
        and the `gt_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(self.gt_operator(v, other) for v in self.values)

    def gte_operator(self, lhs, rhs):
        """
        Checks the left hand side of the operator is greater than or equal to
        the right hand side

        :param lhs: The left hand side of the operator
        :param rhs: The right hand side of the operator

        :return: True if lhs >= rhs, False otherwise
        """
        return lhs >= rhs

    def __ge__(self, other):
        """
        Checks if the group is greater than or equal to the other based on the
        `check_fn` and the `gte_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(self.gte_operator(v, other) for v in self.values)

    def lt_operator(self, lhs, rhs):
        """
        Checks the left hand side of the operator is less than the right
        hand side

        :param lhs: The left hand side of the operator
        :param rhs: The right hand side of the operator

        :return: True if lhs < rhs, False otherwise
        """
        return lhs < rhs

    def __lt__(self, other):
        """
        Checks if the group is less than the other based on the `check_fn`
        and the `lt_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(self.lt_operator(v, other) for v in self.values)

    def lte_operator(self, lhs, rhs):
        """
        Checks the left hand side of the operator is less than or equal to the
        right hand side

        :param lhs: The left hand side of the operator
        :param rhs: The right hand side of the operator

        :return: True if lhs > rhs, False otherwise
        """
        return lhs <= rhs

    def __le__(self, other):
        """
        Checks if the group is less than or equal to the other based on the `
        check_fn` and the `le_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(self.lte_operator(v, other) for v in self.values)

    def in_operator(self, lhs, rhs):
        """
        Checks the left hand side of the operator is contained in the right
        hand side

        :param lhs: The left hand side of the operator
        :param rhs: The right hand side of the operator

        :return: True if lhs in rhs, False otherwise
        """
        return lhs in rhs

    def is_in(self, other):
        """
        Checks if the group is in the other based on the `check_fn` and the
        `in_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(self.in_operator(v, other) for v in self.values)

    def not_in_operator(self, lhs, rhs):
        """
        Checks the left hand side of the operator is not contained in the right
        hand side

        :param lhs: The left hand side of the operator
        :param rhs: The right hand side of the operator

        :return: True if lhs not in rhs, False otherwise
        """
        return lhs not in rhs

    def is_not_in(self, other):
        """
        Checks if the group is not in the other based on the `check_fn` and the
        `not_in_operator`

        :param other: The value to check each element against

        :return: The reduced result
        """
        return self.check_fn(
            self.not_in_operator(v, other) for v in self.values
        )


class AnyWrapper(GroupWrapper):
    """
    Wraps the values and checks if any of their values return true when tested
    """

    def check_fn(self, checks):
        return any(checks)


class AllWrapper(GroupWrapper):
    """
    Wraps the values and checks if all of their values return true when tested
    """

    def check_fn(self, checks):
        return all(checks)


def default_in_transformer(row, lhs, rhs):
    """
    Performs the in check of the lhs in in the rhs. If the lhs has an `is_in`
    method this is used, if not the `in` operator is used.

    :param row: The row being checked (not used)
    :param lhs: The left hand side of the operator
    :param rhs: The right hand side of the operator

    :return: True if lhs is in right, False otherwise
    """
    if hasattr(lhs, "is_in"):
        return lhs.is_in(rhs)
    else:
        return lhs in rhs


def default_not_in_transformer(row, lhs, rhs):
    """
    Performs the in check of the lhs is not in the rhs. If the lhs has an
    `is_not_in` method this is used, if not the `not in` operator is used.

    :param row: The row being checked (not used)
    :param lhs: The left hand side of the operator
    :param rhs: The right hand side of the operator

    :return: True if lhs is not in right, False otherwise
    """
    if hasattr(lhs, "is_not_in"):
        return lhs.is_not_in(rhs)
    else:
        return lhs not in rhs


def default_replace(row, target, *pattern_repl):
    """
    Replaces the pattern in the target string with a given string. The pattern
    can be either a string or regular expression, if a regular expression is
    used groups can be used in the replacement string.

    :param row: The row being transformed (not used)
    :param target: The value to perform the replacement on
    :param pattern_repl: Any number of parameters that have pattern and
        replacement strings, there should be an even number of elements
        with the 1st, 3rd, 5th etc representing the patterns and teh 2nd,
        4th, 6th ets representing the corresponding replacements

    :return: The transformed object
    """
    result = target
    patterns = (p for i, p in enumerate(pattern_repl) if i % 2 == 0)
    repls = (r for i, r in enumerate(pattern_repl) if i % 2 != 0)

    for pattern, repl in zip(patterns, repls):
        if isinstance(pattern, str):
            result = str(result).replace(pattern, repl)
        else:
            result = pattern.sub(repl, str(result))

    return result


def default_match(row, target, pattern: Pattern):
    """
    Checks if a pattern matches the target. The pattern can be either a string
    or regular expression, if a string is used it is the same as
    `pattern == target`.

    :param row: The row being checked (not used)
    :param target: The value to perform the check on
    :param pattern: The pattern to find match the target

    :return: True if the pattern matches the pattern, False otherwise
    """
    if isinstance(pattern, str):
        return str(target) == pattern
    else:
        return bool(pattern.fullmatch(str(target)))


def default_search(row, target, pattern: Pattern):
    """
    Checks if a pattern is in the target. The pattern can be either a string
    or regular expression, if a string is used it is the same as
    `pattern in target`.

    :param row: The row being checked (not used)
    :param target: The value to perform the check on
    :param pattern: The pattern to find in the target

    :return: True if the pattern matches the pattern, False otherwise
    """
    if isinstance(pattern, str):
        return pattern in target
    else:
        return bool(pattern.search(target))


def default_join(row, join, *elements):
    """
    Joins a set of objects as strings

    :param row: The row being transformed (not used)
    :param join: The string used to join the elements
    :param elements: The elements to join

    :return: The joined string
    """
    return str(join).join(map(str, elements))


@v_args(inline=True)
class BaseTreeTransformer(_LarkTransformer):
    """
    Abstract implementation of the Tree transformer class
    """

    lookup: Callable[[RowType, str], Any]
    add: Callable[[RowType, Any, Any], Any]
    subtract: Callable[[RowType, Any, Any], Any]
    multiply: Callable[[RowType, Any, Any], Any]
    divide: Callable[[RowType, Any, Any], Any]
    eq: Callable[[RowType, Any, Any], Any]
    not_eq: Callable[[RowType, Any, Any], Any]
    is_in: Callable[[RowType, Any, Any], Any]
    not_in: Callable[[RowType, Any, Any], Any]
    gt: Callable[[RowType, Any, Any], Any]
    gte: Callable[[RowType, Any, Any], Any]
    lt: Callable[[RowType, Any, Any], Any]
    lte: Callable[[RowType, Any, Any], Any]
    logical_not: Callable[[RowType, Any, Any], Any]
    logical_or: Callable[[RowType, Any, Any], Any]
    logical_and: Callable[[RowType, Any, Any], Any]
    any: Callable[[RowType, List[Any]], GroupWrapper]
    all: Callable[[RowType, List[Any]], GroupWrapper]
    str_join: Callable[..., Any]
    str_replace: Callable[[RowType, Any, Pattern, Any], Any]
    str_match: Callable[[RowType, Any, Pattern, Any], Any]
    str_search: Callable[[RowType, Any, Pattern, Any], Any]

    array = v_args(inline=False)(list)
    string_escape_re = re.compile(r"`([`'])")

    def string(self, value=""):
        """
        Parses a string from the transformer language and performs any
        necessary escaping. `value` has a default value to account for the
        empty string case.

        :param value: The value to parse

        :return: The parsed value
        """
        # process any escape characters
        return self.string_escape_re.sub(r"\1", value)

    def regex(self, value=""):
        """
        Generates a regex from teh provided string

        :param value: The pattern

        :return: The regex object
        """
        return re.compile(self.string(value))

    def iregex(self, value=""):
        """
        Generates a case insensitive regex from teh provided string

        :param value: The pattern

        :return: The regex object
        """
        return re.compile(self.string(value), flags=re.IGNORECASE)

    def boolean(self, value):
        """
        Pareses a boolean from the transformer language.

        :param value: The value to parse

        :return: True if the value is "True", False otherwise
        """
        return value == "True"

    def null(self, value):
        """
        Pareses a null from the transformer language.

        :param value: The value to parse (ignored as its always Null)

        :return: None
        """
        return None

    def number(self, value):
        """
        Parses a number from the transformer language. First tries to parse an
        integer but on failure parses as a float.

        :param value: The value to parse

        :return: The parsed value
        """
        try:
            return int(value)
        except ValueError:
            return float(value)


def create_transformer_class(row, transformer_mapping):
    """
    Creates a transformer class from the provided mapping overrides.

    :param row: The row to transform
    :param transformer_mapping: The overrides for the transform functions

    :return: The new transformer class
    """
    transformer_mapping = {
        "lookup": lambda r, name: r[name],
        "add": lambda r, lhs, rhs: add(lhs, rhs),
        "subtract": lambda r, lhs, rhs: sub(lhs, rhs),
        "multiply": lambda r, lhs, rhs: mul(lhs, rhs),
        "divide": lambda r, lhs, rhs: div(lhs, rhs),
        "eq": lambda r, lhs, rhs: lhs == rhs,
        "not_eq": lambda r, lhs, rhs: lhs != rhs,
        "is_in": default_in_transformer,
        "not_in": default_not_in_transformer,
        "gt": lambda r, lhs, rhs: lhs > rhs,
        "gte": lambda r, lhs, rhs: lhs >= rhs,
        "lt": lambda r, lhs, rhs: lhs < rhs,
        "lte": lambda r, lhs, rhs: lhs <= rhs,
        "logical_or": lambda r, lhs, rhs: lhs or rhs,
        "logical_and": lambda r, lhs, rhs: lhs and rhs,
        "logical_not": lambda r, v: not v,
        "any": lambda r, v: AnyWrapper(v),
        "all": lambda r, v: AllWrapper(v),
        "str_join": default_join,
        "str_replace": default_replace,
        "str_match": default_match,
        "str_search": default_search,
        **(transformer_mapping or {}),
    }

    def mapped_function(name, *args, **kwargs):
        return transformer_mapping[name](row, *args, **kwargs)

    @v_args(inline=True)
    class TreeTransformer(BaseTreeTransformer):
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
        str_join = partial(mapped_function, "str_join")
        str_replace = partial(mapped_function, "str_replace")
        str_match = partial(mapped_function, "str_match")
        str_search = partial(mapped_function, "str_search")

    return TreeTransformer


def parse(expression: Union[str, Tree]) -> Tree:
    """
    Parse an expression from the transformation language

    :param expression: The expression to pass

    :return: The parsd expression tree
    """
    if not isinstance(expression, str):
        return expression

    try:
        return parser.parse(expression)
    except lark_exceptions.UnexpectedCharacters as e:
        raise UnexpectedCharacters(
            expression, expression[e.pos_in_stream], e.column
        )


def transform(
    row, tree: Tree, transformer_mapping: TransformerMapping = None,
):
    """
    Performs the transformation on the row

    :param row: The row to transform
    :param tree: The parsed tree for the expression
    :param transformer_mapping: Overrides for the transformer operations

    :return: The transformation result
    """
    transformer_class = create_transformer_class(row, transformer_mapping)
    transformer = transformer_class()

    return transformer.transform(tree)


def run(
    row,
    expression: Union[str, Tree],
    transformer_mapping: TransformerMapping = None,
):
    """
    Runs a transformation expression on a row

    :param row: The row to transform
    :param expression: The transformation to perform
    :param transformer_mapping: Overrides for the transformer operations

    :return: The transformed result
    """
    return transform(
        row, parse(expression), transformer_mapping=transformer_mapping
    )
