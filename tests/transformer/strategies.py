from hypothesis.strategies import characters
from hypothesis.strategies import floats as _floats
from hypothesis.strategies import integers as _integers
from hypothesis.strategies import text


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
