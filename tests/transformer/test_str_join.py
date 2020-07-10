import pytest
from hypothesis import given
from hypothesis.strategies import lists, one_of

from converter.transformers import run
from converter.transformers.errors import UnexpectedCharacters
from tests.transformer.strategies import floats, integers, strings


def test_no_args_are_provided___error_is_raised():
    with pytest.raises(UnexpectedCharacters):
        run({}, "join()")


def test_no_strings_are_provided___result_is_empty():
    assert run({}, "join(', ')") == ""


@given(join=strings(), elements=lists(strings(), min_size=1))
def test_multiple_strings_are_provided___result_is_join_by_join_str(
    join, elements
):
    expected = join.join(elements)
    arg_elements = map(lambda o: f"'{o}'", elements)

    expr = f"join('{join}', {', '.join(arg_elements)})"
    assert run({}, expr) == expected


@given(
    join=strings(),
    elements=lists(one_of(strings(), integers(), floats()), min_size=1),
)
def test_multiple_objects_are_provided___result_is_join_by_join_str(
    join, elements
):
    expected = join.join(map(str, elements))
    arg_elements = map(
        lambda o: f"'{o}'" if isinstance(o, str) else str(o), elements,
    )

    expr = f"join('{join}', {', '.join(arg_elements)})"
    assert run({}, expr) == expected
