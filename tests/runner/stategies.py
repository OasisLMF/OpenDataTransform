from hypothesis.strategies import sampled_from

from converter.runner import ModinRunner, PandasRunner


def runners():
    return sampled_from([PandasRunner, ModinRunner])
