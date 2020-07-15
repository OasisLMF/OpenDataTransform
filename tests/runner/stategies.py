from hypothesis.strategies import sampled_from

from converter.runner import EagerRunner, ModinRunner, PandasRunner


def runners():
    return sampled_from([PandasRunner, ModinRunner, EagerRunner])
