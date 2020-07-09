from math import isnan


class NaNChecker:
    def __eq__(self, other):
        return isnan(other)
