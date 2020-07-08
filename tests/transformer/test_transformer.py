from hypothesis import given
from hypothesis.strategies import characters
from hypothesis.strategies import floats as _floats
from hypothesis.strategies import integers as _integers
from hypothesis.strategies import lists, sampled_from, text

from converter.transformers import run


def floats():
    """
    Helper function to generate parsable floats, we exclude inf, nan and
    negative. Negatives are tested explicitly.
    """
    return _floats(min_value=0, allow_infinity=False, allow_nan=False)


def integers():
    """
    Helper function to generate parsable integers, we exclude negative
    as these are tested explicitly.
    """
    # limit to 1000000 to prevent ints being expressed in e notation losing
    # precision
    return _integers(min_value=0, max_value=1000000)


def strings():
    """
    Helper for generating parsable strings excluding ' and ` as they
    needs to be escaped and are tested explicitly
    """
    return text(
        alphabet=characters(
            blacklist_categories=("Cs",), blacklist_characters=("'", "`"),
        )
    )


#
# Value parsing
#


@given(floats())
def test_float_parsing(value):
    assert run({}, f"{value}") == float(f"{value}")


@given(floats())
def test_negative_float_parsing(value):
    assert run({}, f"-{value}") == -float(f"{value}")


@given(floats())
def test_e_notation_float_parsing(value):
    assert run({}, f"{value:.15e}") == float(f"{value:.15e}")


@given(floats())
def test_negative_e_notation_float_parsing(value):
    assert run({}, f"-{value:.15e}") == -float(f"{value:.15e}")


@given(integers())
def test_int_parsing(value):
    assert run({}, f"{value}") == value


@given(integers())
def test_negative_int_parsing(value):
    assert run({}, f"-{value}") == -value


@given(strings())
def test_string_parsing(value):
    assert run({}, f"'{value}'") == value


@given(char=sampled_from("`'"))
def test_string_parsing___escape_character_is_escapeable(char):
    assert run({}, f"'```{char}``'") == f"`{char}`"


@given(lhs=strings(), rhs=strings())
def test_string_with_escaped_single_quote_parsing(lhs, rhs):
    assert run({}, rf"'{lhs}`'{rhs}'") == rf"{lhs}'{rhs}"


@given(strings())
def test_column_name_returns_row_column_value(value):
    assert run({"foo": value}, "foo") == value


@given(name=strings(), value=strings())
def test_lookup_function_returns_row_column_value(name, value):
    assert run({name: value}, f"lookup('{name}')") == value


@given(name_lhs=strings(), name_rhs=strings(), value=strings())
def test_lookup_function_with_escaped_quote_returns_row_column_value(
    name_lhs, name_rhs, value
):
    assert (
        run(
            {f"{name_lhs}'{name_rhs}": value},
            rf"lookup('{name_lhs}`'{name_rhs}')",
        )
        == value
    )


def test_true_is_parsed_correctly():
    assert run({}, "True") is True


def test_false_is_parsed_correctly():
    assert run({}, "False") is False


@given(values=lists(integers()))
def test_list_is_parsed_correctly(values):
    assert run({}, f"[{', '.join(map(str, values))}]") == values


#
# expression parsing
#


@given(lhs=floats(), rhs=floats())
def test_float_addition(lhs, rhs):
    assert run({}, f"{lhs} + {rhs}") == lhs + rhs


@given(lhs=integers(), rhs=integers())
def test_int_addition(lhs, rhs):
    assert run({}, f"{lhs} + {rhs}") == lhs + rhs


@given(lhs=strings(), rhs=strings())
def test_string_addition(lhs, rhs):
    assert run({}, f"'{lhs}' + '{rhs}'") == lhs + rhs


@given(lhs=floats(), rhs=floats())
def test_float_subtraction(lhs, rhs):
    assert run({}, f"{lhs} - {rhs}") == lhs - rhs


@given(lhs=integers(), rhs=integers())
def test_int_subtraction(lhs, rhs):
    assert run({}, f"{lhs} - {rhs}") == lhs - rhs


@given(lhs=floats(), rhs=floats())
def test_float_multiplication(lhs, rhs):
    assert run({}, f"{lhs} * {rhs}") == lhs * rhs


@given(lhs=integers(), rhs=integers())
def test_int_multiplication(lhs, rhs):
    assert run({}, f"{lhs} * {rhs}") == lhs * rhs


@given(lhs=floats(), rhs=floats().filter(lambda v: v != 0))
def test_float_division(lhs, rhs):
    assert run({}, f"{lhs} / {rhs}") == lhs / rhs


@given(lhs=integers(), rhs=integers().filter(lambda v: v != 0))
def test_int_division(lhs, rhs):
    assert run({}, f"{lhs} / {rhs}") == lhs / rhs


#
# combined expressions
#


@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_addition_order(a, b, c):
    expected = a + (b * c)
    assert run({}, f"{a} + {b} * {c}") == expected
    assert run({}, f"{c} * {b} + {a}") == expected


@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_addition_order_with_brackets(a, b, c):
    expected = (a + b) * c
    assert run({}, f"({a} + {b}) * {c}") == expected
    assert run({}, f"{c} * ({b} + {a})") == expected


@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_subtraction_order(a, b, c):
    expected = a - (b * c)
    assert run({}, f"{a} - {b} * {c}") == expected


@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_subtraction_order_with_brackets(a, b, c):
    expected = (a - b) * c
    assert run({}, f"({a} - {b}) * {c}") == expected
    assert run({}, f"{c} * ({a} - {b})") == expected


@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_addition_order(a, b, c):
    expected = a + (b / c)
    assert run({}, f"{a} + {b} / {c}") == expected
    assert run({}, f"{b} / {c} + {a}") == expected


@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_addition_order_with_brackets(a, b, c):
    expected = (a + b) / c
    assert run({}, f"({a} + {b}) / {c}") == expected


@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_subtraction_order(a, b, c):
    expected = a - (b / c)
    assert run({}, f"{a} - {b} / {c}") == expected


@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_subtraction_order_with_brackets(a, b, c):
    expected = (a - b) / c
    assert run({}, f"({a} - {b}) / {c}") == expected


#
# Comparisons
#


def test_values_are_equal___is_result_is_true():
    assert run({}, "1 is 1") is True


def test_values_are_not_equal___is_result_is_false():
    assert run({}, "1 is 0.9") is False
    assert run({}, "1 is 1.1") is False


def test_values_are_not_equal___is_not_result_is_true():
    assert run({}, "1 is not 0.9") is True
    assert run({}, "1 is not 1.1") is True


def test_values_are_equal___is_not_result_is_false():
    assert run({}, "1 is not 1") is False


def test_lhs_is_lt_rhs___lt_result_is_true():
    assert run({}, "0.9 lt 1") is True


def test_values_are_equal___lt_result_is_false():
    assert run({}, "1 lt 1") is False


def test_lhs_is_gt_rhs___lt_result_is_false():
    assert run({}, "1.1 lt 1") is False


def test_lhs_is_lt_rhs___lte_result_is_true():
    assert run({}, "0.9 lte 1") is True


def test_values_are_equal___lte_result_is_true():
    assert run({}, "1 lte 1") is True


def test_lhs_is_gt_rhs___lte_result_is_false():
    assert run({}, "1.1 lte 1") is False


def test_lhs_is_gt_rhs___gt_result_is_true():
    assert run({}, "1 gt 0.9") is True


def test_values_are_equal___gt_result_is_false():
    assert run({}, "1 gt 1") is False


def test_lhs_is_lt_rhs___gt_result_is_false():
    assert run({}, "1 gt 1.1") is False


def test_lhs_is_gt_rhs___gte_result_is_true():
    assert run({}, "1 gte 0.9") is True


def test_values_are_equal___gte_result_is_false():
    assert run({}, "1 gte 1") is True


def test_lhs_is_lt_rhs___gte_result_is_false():
    assert run({}, "1 gte 1.1") is False


def test_lhs_is_in_rhs___is_in_result_is_true():
    assert run({}, "1 is in [0, 1, 2, 3, 4]") is True


def test_lhs_is_not_in_rhs___is_in_result_is_false():
    assert run({}, "1 is in [0, 2, 3, 4]") is False


def test_lhs_is_not_in_rhs___is_not_in_result_is_true():
    assert run({}, "1 is not in [0, 2, 3, 4]") is True


def test_lhs_is_in_rhs___is_not_in_result_is_false():
    assert run({}, "1 is not in [0, 1, 2, 3, 4]") is False


def test_lhs_and_rhs_are_true___or_result_is_true():
    assert run({}, "True or True") is True


def test_lhs_is_false_and_rhs_is_true___or_result_is_true():
    assert run({}, "False or True") is True


def test_rhs_is_false_and_lhs_is_true___or_result_is_true():
    assert run({}, "True or False") is True


def test_lhs_and_rhs_are_false___or_result_is_false():
    assert run({}, "False or False") is False


def test_lhs_and_rhs_are_true___and_result_is_true():
    assert run({}, "True and True") is True


def test_lhs_is_false_and_rhs_is_true___and_result_is_false():
    assert run({}, "False and True") is False


def test_rhs_is_false_and_lhs_is_true___and_result_is_false():
    assert run({}, "True and False") is False


def test_lhs_and_rhs_are_false___and_result_is_false():
    assert run({}, "False and False") is False


def test_value_is_false___not_result_is_true():
    assert run({}, "not False") is True


def test_value_is_true___not_result_is_false():
    assert run({}, "not True") is False
