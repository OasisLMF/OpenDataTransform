from converter.transformers import run


def test_pattern_is_string_that_isnt_in_string___result_is_false():
    assert run({}, "match('foo', 'bar')") is False


def test_pattern_is_substring___result_is_false():
    assert run({}, "match('foo bar bash', 'bar')") is False


def test_pattern_is_string_matching_full_string___result_is_false():
    assert run({}, "match('foo bar bash', 'foo bar bash')") is True


def test_pattern_is_regex_in_string_but_not_full_string___result_is_false():
    assert run({}, "match('foo bar foo bash', re'foo')") is False


def test_pattern_is_regex_in_string_matches_the_full_string___result_is_true():
    assert run({}, "match('foo bar foo bash', re'.*')") is True
