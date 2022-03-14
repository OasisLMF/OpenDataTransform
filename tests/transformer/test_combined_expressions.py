from hypothesis import given, settings

from converter.transformers import run
from tests.transformer.strategies import integers


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_addition_order(a, b, c):
    expected = a + (b * c)
    assert run({}, f"{a} + {b} * {c}") == expected
    assert run({}, f"{c} * {b} + {a}") == expected


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_addition_order_with_brackets(a, b, c):
    expected = (a + b) * c
    assert run({}, f"({a} + {b}) * {c}") == expected
    assert run({}, f"{c} * ({b} + {a})") == expected


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_subtraction_order(a, b, c):
    expected = a - (b * c)
    assert run({}, f"{a} - {b} * {c}") == expected


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers())
def test_multiplication_and_subtraction_order_with_brackets(a, b, c):
    expected = (a - b) * c
    assert run({}, f"({a} - {b}) * {c}") == expected
    assert run({}, f"{c} * ({a} - {b})") == expected


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_addition_order(a, b, c):
    expected = a + (b / c)
    assert run({}, f"{a} + {b} / {c}") == expected
    assert run({}, f"{b} / {c} + {a}") == expected


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_addition_order_with_brackets(a, b, c):
    expected = (a + b) / c
    assert run({}, f"({a} + {b}) / {c}") == expected


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_subtraction_order(a, b, c):
    expected = a - (b / c)
    assert run({}, f"{a} - {b} / {c}") == expected


@settings(deadline=None)
@given(a=integers(), b=integers(), c=integers().filter(lambda v: v != 0))
def test_division_and_subtraction_order_with_brackets(a, b, c):
    expected = (a - b) / c
    assert run({}, f"({a} - {b}) / {c}") == expected
