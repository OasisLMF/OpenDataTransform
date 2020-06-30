import logging
from functools import reduce
from typing import Any, Dict, Iterable, Generic, TypeVar, Union, List

import pandas as pd

from ..connector.base import BaseConnector
from ..mapping.base import BaseMapping, TransformationSet, TransformationEntry
from .base import BaseRunner
from ..transformers import run


logger = logging.getLogger(__name__)


class PandasRunner(BaseRunner):
    dataframe_type = pd.DataFrame
    series_type = pd.Series

    def __init__(self, **options):
        super().__init__(**options)

        self._dataframe: Union[None, pd.DataFrame] = None

    def get_dataframe(self, extractor: BaseConnector) -> pd.DataFrame:
        return pd.DataFrame(extractor.extract())

    def apply_transformation_entry(
        self,
        input_df: pd.DataFrame,
        entry: TransformationEntry,
    ):
        # process the when clause to get a filter series
        filter_series = input_df[run(input_df, entry.when)]

        if isinstance(filter_series, pd.Series):
            # if we have a series it treat it as a row mapping
            filtered_input = input_df[filter_series]
        elif filter_series:
            # if the filter series is normal value that resolves to true
            # return all rows
            filtered_input = input_df
        else:
            # if the filter series is normal value that resolves to false
            # return no rows, this should never happen so raise a warning.
            logger.warning(
                f"A transformer when clause resolves to false in all cases "
                f"({entry.when})."
            )
            filtered_input = self.dataframe_type()

        return run(filtered_input, entry.transformation)

    def apply_column_transformation(
        self,
        input_df: pd.DataFrame,
        entry_list: List[TransformationEntry],
    ):
        return reduce(
            lambda series, entry: series.combine_first(
                self.apply_transformation_entry(input_df, entry),
            ),
            entry_list,
            self.series_type()
        )

    def apply_transformation_set(
        self,
        input_df: pd.DataFrame,
        transformation_set: TransformationSet,
    ) -> pd.DataFrame:
        return reduce(
            lambda target, col_transforms: target.assign(
                **{col_transforms[0]: self.apply_column_transformation(
                    input_df, col_transforms[1]
                )}
            ),
            transformation_set.items(),
            self.dataframe_type(),
        )

    def transform(
        self, extractor: BaseConnector, mapping: BaseMapping
    ) -> Iterable[Dict[str, Any]]:
        transformations = mapping.get_transformations()

        df = self.get_dataframe(extractor)

        transformed = reduce(
            self.apply_transformation_set,
            transformations,
            df,
        )

        return transformed
