from itertools import product
from typing import List, Union, Iterable

import pandas as pd
from pandas.core.groupby.generic import DataFrameGroupBy

from converter.validator.base import BaseValidator, ValidationResult, ValidatorConfigEntry


class PandasValidator(BaseValidator):
    def run_entry(self, data: pd.DataFrame, entry: ValidatorConfigEntry) -> List[ValidationResult]:
        fields = set(
            entry.fields +
            (entry.group_by or [])
        )

        if not fields:
            fields = [data.columns[0]]

        return super().run_entry(data[fields], entry)

    def group_data(self, data: pd.DataFrame, group_by: List[str], entry: ValidatorConfigEntry) -> DataFrameGroupBy:
        return data.groupby(group_by)

    def sum(self, data: Union[pd.DataFrame, DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        sum_res = data.sum()

        if hasattr(sum_res, "to_frame"):
            sum_res = sum_res.to_frame().transpose()

        return self._generate_result(sum_res, entry)

    def count(self, data: Union[pd.DataFrame, DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        count_res = data.count()

        if hasattr(count_res, "to_frame"):
            count_res = count_res.to_frame().transpose()

        return self._generate_result(count_res, entry)

    def _generate_result(self, data: Union[pd.DataFrame, DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        fields = entry.fields or data.columns
        return [
            (
                self.generate_result_name(
                    entry, field if len(entry.fields) > 1 else None, index_values=index if entry.group_by is not None else None
                ),
                row[field],
            ) for (index, row), field in product(data.iterrows(), fields)
        ]
