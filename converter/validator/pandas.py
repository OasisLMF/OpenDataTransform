from itertools import combinations
from typing import List, Union

import pandas as pd

from converter.validator.base import BaseValidator, ValidationResult, ValidatorConfigEntry


class PandasValidator(BaseValidator):
    def run_entry(self, data: pd.DataFrame, entry: ValidatorConfigEntry) -> List[ValidationResult]:
        return super().run_entry(data[set(entry.fields + entry.group_by)], entry)

    def group_data(self, data: pd.DataFrame, group_by: List[str], entry: ValidatorConfigEntry) -> pd.DataFrameGroupBy:
        return data.groupby(group_by)

    def sum(self, data: Union[pd.DataFrame, pd.DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        return self._generate_result(data.sum(), entry)

    def count(self, data: Union[pd.DataFrame, pd.DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        return self._generate_result(data.count(), entry)

    def _generate_result(self, data: Union[pd.DataFrame, pd.DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResult]:
        if data.index.name is not None:
            return [
                (self.generate_result_name(entry, field, index_values=row[[data.index.name]]), row[field])
                for row, field in combinations(data.iterrows(), entry.fields)
            ]
        elif data.index.names is not None:
            return [
                (self.generate_result_name(entry, field, index_values=row[[data.index.name]]), row[field])
                for row, field in combinations(data.iterrows(), entry.fields)
            ]
        else:
            return [
                (self.generate_result_name(entry, field), data.iloc[0][field])
                for field in entry.fields
            ]
