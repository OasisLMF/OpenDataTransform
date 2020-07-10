import re
import string

from hypothesis import given
from hypothesis.strategies import lists, sampled_from, text

from converter.transformers import run
from tests.transformer.strategies import floats, integers, strings


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


@given(pattern=text(alphabet=string.ascii_letters))
def test_regex_is_parsed_correctly(pattern):
    parsed = run({}, f"re'{pattern}'")

    assert isinstance(parsed, re.Pattern)
    assert parsed.pattern == pattern
    assert (parsed.flags & re.IGNORECASE) == 0


@given(pattern=text(alphabet=string.ascii_letters))
def test_case_insensitive_regex_is_parsed_correctly(pattern):
    parsed = run({}, f"ire'{pattern}'")

    assert isinstance(parsed, re.Pattern)
    assert parsed.pattern == pattern
    assert (parsed.flags & re.IGNORECASE) == re.IGNORECASE
