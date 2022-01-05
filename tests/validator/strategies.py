from hypothesis.strategies import sampled_from

from converter.validator.pandas import PandasValidator


def validator_classes():
    return sampled_from(
        [
            PandasValidator,
        ]
    )
