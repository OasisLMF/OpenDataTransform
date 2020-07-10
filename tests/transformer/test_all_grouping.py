from converter.transformers import run


def test_values_are_all_equal___all_is_result_is_true():
    assert bool(run({}, "all [1, 1] is 1")) is True


def test_values_are_not_all_equal___all_is_result_is_false():
    assert run({}, "all [1, 0.9, 0.8] is 0.9") is False


def test_values_are_not_all_equal___all_is_not_result_is_true():
    assert run({}, "all [1, 0.8] is not 0.9") is True


def test_some_values_are_equal___all_is_not_result_is_false():
    assert run({}, "all [1.1, 1, 0.9] is not 1") is False


def test_all_is_lt_rhs___all_lt_result_is_true():
    assert run({}, "all [0.9, 0.8] lt 1") is True


def test_some_values_are_equal___all_lt_result_is_false():
    assert run({}, "all [1, 0.9, 0.8] lt 1") is False


def test_some_values_are_gt_rhs___all_lt_result_is_false():
    assert run({}, "all [1.1, 0.9, 0.8] lt 1") is False


def test_all_values_are_lt_rhs___all_lte_result_is_true():
    assert run({}, "all [0.9, 0.8] lte 1") is True


def test_some_values_are_equal___all_lte_result_is_true():
    assert run({}, "all [1, 0.9, 0.8] lte 1") is True


def test_some_value_are_gt_rhs___all_lte_result_is_false():
    assert run({}, "all [1.1, 1, 0.9] lte 1") is False


def test_all_values_are_gt_rhs___all_gt_result_is_true():
    assert run({}, "all [1, 1.1] gt 0.9") is True


def test_some_values_are_equal___all_gt_result_is_false():
    assert run({}, "all [1, 1.1, 1.2] gt 1") is False


def test_some_values_are_lt_rhs___all_gt_result_is_false():
    assert run({}, "all [1, 1.2] gt 1.1") is False


def test_all_values_are_gt_rhs___all_gte_result_is_true():
    assert run({}, "all [1, 1.1, 1.2] gte 0.9") is True


def test_some_values_are_equal___all_gte_result_is_true():
    assert run({}, "all [1, 1.1, 1.2] gte 1") is True


def test_some_values_are_lt_rhs___all_gte_result_is_false():
    assert run({}, "all [1, 1.2, 1.3] gte 1.1") is False


def test_all_lhs_is_in_rhs___all_is_in_result_is_true():
    assert run({}, "all [1, 2, 3] is in [0, 1, 2, 3, 4]") is True


def test_some_values_are_not_in_rhs___all_is_in_result_is_false():
    assert run({}, "all [1, 2, 3] is in [0, 2, 3, 4]") is False


def test_all_lhs_is_not_in_rhs___all_is_not_in_result_is_true():
    assert run({}, "all [1, 3] is not in [0, 2, 4]") is True


def test_some_values_are_in_rhs___all_is_not_in_result_is_false():
    assert run({}, "all [1, 2, 3] is not in [0, 2, 4]") is False
