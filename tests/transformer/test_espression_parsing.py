from hypothesis import given

from converter.transformers import run
from converter.transformers.transform import parse
from tests.transformer.strategies import floats, integers, strings


def test_parsing_expression_twice_gives_the_same_result():
    assert parse("a + b") == parse(parse("a + b"))


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
