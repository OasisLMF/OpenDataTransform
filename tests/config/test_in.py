from converter.config import Config


def test_tpl_present___has_template_is_false():
    assert not Config(overrides={}).has_template


def test_tpl_present___has_template_is_true():
    assert not Config(
        overrides={"transformation_template": {"acc": {"foo": "bar"}}}
    ).has_acc


def test_acc_not_present___has_acc_is_false():
    assert not Config(overrides={}).has_acc


def test_acc_present___has_acc_is_true():
    assert Config(
        overrides={"transformations": {"acc": {"foo": "bar"}}}
    ).has_acc


def test_loc_not_present___has_loc_is_false():
    assert not Config(overrides={}).has_loc


def test_loc_present___has_loc_is_true():
    assert Config(
        overrides={"transformations": {"loc": {"foo": "bar"}}}
    ).has_loc


def test_ri_not_present___has_ri_is_false():
    assert not Config(overrides={}).has_ri


def test_ri_present___has_ri_is_true():
    assert Config(overrides={"transformations": {"ri": {"foo": "bar"}}}).has_ri
