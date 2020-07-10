from converter.transformers import run


def test_values_are_all_equal___any_is_result_is_true():
    assert run({}, "any [1, 1] is 1") is True


def test_some_values_are_not_all_equal___any_is_result_is_true():
    assert run({}, "any [1, 0.9, 0.8] is 0.9") is True


def test_all_values_are_not_all_equal___any_is_result_is_false():
    assert run({}, "any [1, 0.8] is 0.9") is False


def test_all_values_are_not_all_equal___any_is_not_result_is_true():
    assert run({}, "any [1, 0.8] is not 0.9") is True


def test_some_values_are_equal___any_is_not_result_is_true():
    assert run({}, "any [1.1, 1, 0.9] is not 1") is True


def test_all_values_are_equal___any_is_not_result_is_false():
    assert run({}, "any [1, 1] is not 1") is False


def test_all_values_are_lt_rhs___any_lt_result_is_true():
    assert run({}, "any [0.9, 0.8] lt 1") is True


def test_some_values_are_lt___any_lt_result_is_true():
    assert run({}, "any [1.1, 1, 0.9] lt 1") is True


def test_all_values_are_gte___any_lt_result_is_false():
    assert run({}, "any [1.1, 1] lt 1") is False


def test_some_values_are_lt_rhs___any_lte_result_is_true():
    assert run({}, "any [1.1, 0.9] lte 1") is True


def test_some_values_are_eq_rhs___any_lte_result_is_true():
    assert run({}, "any [1, 0.9] lte 1") is True


def test_all_values_are_gt_rhs___all_lte_result_is_false():
    assert run({}, "any [1.1, 1.2] lte 1") is False


def test_some_values_are_gt_rhs___any_gt_result_is_true():
    assert run({}, "any [0.8, 1.1] gt 0.9") is True


def test_all_values_are_equal___any_gt_result_is_false():
    assert run({}, "any [1, 1] gt 1") is False


def test_all_values_are_lt_rhs___any_gt_result_is_false():
    assert run({}, "any [1, 0.9] gt 1.1") is False


def test_some_values_are_gt_rhs___any_gte_result_is_true():
    assert run({}, "any [1, 0.8] gte 0.9") is True


def test_some_values_are_equal___any_gte_result_is_true():
    assert run({}, "any [1, 0.9] gte 1") is True


def test_all_values_are_lt_rhs___any_gte_result_is_false():
    assert run({}, "any [1, 0.9] gte 1.1") is False


def test_some_lhs_is_in_rhs___any_is_in_result_is_true():
    assert run({}, "any [1, 2, 3] is in [0, 1, 4]") is True


def test_all_values_are_not_in_rhs___any_is_in_result_is_false():
    assert run({}, "any [0, 1, 5, 6] is in [2, 3, 4]") is False


def test_some_lhs_is_not_in_rhs___any_is_not_in_result_is_true():
    assert run({}, "any [1, 2] is not in [0, 2, 4]") is True


def test_all_values_are_in_rhs___any_is_not_in_result_is_false():
    assert run({}, "any [2, 4] is not in [0, 1, 2, 3, 4]") is False
