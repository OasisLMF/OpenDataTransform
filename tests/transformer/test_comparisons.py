from converter.transformers import run


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


def test_value_is_multiple_chained_comparisons_without_brackets():
    assert run({}, "True and True and False") is False
