from hypothesis.strategies import sampled_from

from converter.runner import DaskRunner, EagerRunner, ModinRunner, PandasRunner


def runners():
    return sampled_from([PandasRunner, ModinRunner, EagerRunner, DaskRunner])
    # return sampled_from([ModinRunner])
