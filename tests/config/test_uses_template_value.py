from converter.config import Config


def test_not_present___result_is_false():
    conf = Config(overrides={})

    assert not conf.uses_template_value("transformations.acc.a")


def test_value_in_template_not_transformation____result_is_true():
    conf = Config(overrides={"template_transformation": {"a": "foo"}})

    assert conf.uses_template_value("transformations.acc.a")


def test_value_in_template_matching_transformation____result_is_true():
    conf = Config(
        overrides={
            "template_transformation": {"a": "foo"},
            "transformations": {"acc": {"a": "foo"}},
        }
    )

    assert conf.uses_template_value("transformations.acc.a")


def test_value_in_template_differs_from_transformation____result_is_false():
    conf = Config(
        overrides={
            "template_transformation": {"a": "foo"},
            "transformations": {"acc": {"a": "bar"}},
        }
    )

    assert not conf.uses_template_value("transformations.acc.a")


def test_value_not_in_template_present_in_transformation____result_is_false():
    conf = Config(
        overrides={
            "template_transformation": {"b": "boo"},
            "transformations": {"acc": {"a": "bar"}},
        }
    )

    assert not conf.uses_template_value("transformations.acc.a")
