from converter.transformers import run


def test_pattern_isnt_in_string___string_is_unchanged():
    assert run({}, "replace('foo', 'bar', 'boo')") == "foo"


def test_pattern_is_string_in_string___string_is_changed():
    assert (
        run({}, "replace('foo bar foo bash', 'foo', 'boo')")
        == "boo bar boo bash"
    )


def test_pattern_is_regex_in_string___string_is_changed():
    assert (
        run({}, r"replace('foo bar doo bash', re'(.)oo', '\1aa')")
        == "faa bar daa bash"
    )
