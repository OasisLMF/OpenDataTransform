from itertools import product
from typing import List, Union
from uuid import uuid4

import pandas as pd
from pandas.core.groupby.generic import DataFrameGroupBy

from converter.validator.base import BaseValidator, ValidationResult, ValidatorConfigEntry, ValidationResultEntry


class PandasValidator(BaseValidator):
    def run_entry(self, data: pd.DataFrame, entry: ValidatorConfigEntry) -> ValidationResult:
        fields = set(
            entry.fields +
            (entry.group_by or [])
        )

        if not entry.fields:
            # if no fields are selected copy the index into a temp column
            # so that counts can still be performed
            field_name = uuid4()
            data[field_name] = 1
            fields.add(field_name)

        return super().run_entry(data[fields], entry)

    def group_data(self, data: pd.DataFrame, group_by: List[str], entry: ValidatorConfigEntry) -> DataFrameGroupBy:
        return data.groupby(group_by)

    def sum(self, data: Union[pd.DataFrame, DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResultEntry]:
        sum_res = data.sum()

        if hasattr(sum_res, "to_frame"):
            sum_res = sum_res.to_frame().transpose()

        return self._generate_result(sum_res, entry)

    def count(self, data: Union[pd.DataFrame, DataFrameGroupBy], entry: ValidatorConfigEntry) -> List[ValidationResultEntry]:
        count_res = data.count()

        if hasattr(count_res, "to_frame"):
            count_res = count_res.to_frame().transpose()

        return self._generate_result(count_res, entry)

    def _generate_result(self, data: Union[pd.DataFrame, DataFrameGroupBy], config_entry: ValidatorConfigEntry) -> List[ValidationResultEntry]:
        results = []

        fields = config_entry.fields or data.columns
        for (index, row), field in product(data.iterrows(), fields):
            res_entry = ValidationResultEntry(value=str(row[field]))

            if config_entry.fields:
                res_entry["field"] = field

            if config_entry.group_by:
                if len(config_entry.group_by) == 1:
                    res_entry["groups"] = {config_entry.group_by[0]: str(index)}
                else:
                    res_entry["groups"] = dict(zip(config_entry.group_by, map(str, index)))

            results.append(res_entry)

        return results
