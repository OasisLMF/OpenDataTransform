import logging
from functools import reduce
from operator import and_, or_
from typing import Any, Dict, Iterable, List, Union

import pandas as pd
from numpy import nan

from ..connector.base import BaseConnector
from ..mapping.base import BaseMapping, TransformationEntry, TransformationSet
from ..transformers import run
from ..transformers.transform import TransformerMapping
from .base import BaseRunner


def get_logger():
    return logging.getLogger(__name__)


def logical_not(value):
    try:
        return not bool(value)
    except ValueError:
        # assume we are dealing with series or
        # dataframe is we get a value error
        return value.apply(lambda v: not bool(v))


class PandasRunner(BaseRunner):
    dataframe_type = pd.DataFrame
    series_type = pd.Series

    transformer_mapping: TransformerMapping = {
        "logical_and": lambda r, lhs, rhs: lhs & rhs,
        "logical_or": lambda r, lhs, rhs: lhs | rhs,
        "logical_not": lambda r, v: logical_not(v),
        "is_in": lambda r, lhs, rhs: reduce(or_, map(lambda s: s == lhs, rhs)),
        "not_in": lambda r, lhs, rhs: reduce(
            and_, map(lambda s: s != lhs, rhs)
        ),
    }

    def get_dataframe(self, extractor: BaseConnector) -> pd.DataFrame:
        return pd.DataFrame(extractor.extract())

    def combine_series(self, first: Union[pd.Series, None], second):
        """
        Helper function for combining 2 series. This is used so that
        other pandas implementations can override the behaviour to
        account for special cases.

        Some pandas implementations dont like combining on empty series.
        If first is None we just return the second series which will be in
        the implementations specific series.

        :param first: The preferred series to take data from
        :param second: The secondary series to take data from

        :return: The combined series
        """
        if first is None:
            return second
        elif second is None:
            return first
        else:
            return first.combine_first(second)

    def assign(self, dataframe: Union[pd.DataFrame, None], **assignments):
        """
        Helper function for assigning a series to a dataframe. Some
        implementations of pandas are less efficient if we start with an empty
        dataframe so here we allow for `None` to be passed and create the
        initial dataframe from the first assigned series.

        :param dataframe: The data frame to assign to or None
        :param assignments: The assignments to apply to the dataframe

        :return: The updated dataframe
        """
        for name, series in assignments.items():
            if series is None:
                series = self.series_type([nan])

            if dataframe is None:
                dataframe = series.to_frame(name=name)
            else:
                series.name = name
                dataframe, series = dataframe.align(series, axis=0)
                dataframe = dataframe.assign(**{name: series})

        return dataframe

    def apply_transformation_entry(
        self, input_df: pd.DataFrame, entry: TransformationEntry,
    ):
        # process the when clause to get a filter series
        filter_series = run(input_df, entry.when, self.transformer_mapping)

        if isinstance(filter_series, self.series_type):
            # if we have a series it treat it as a row mapping
            filtered_input = input_df[filter_series]
        elif filter_series:
            # if the filter series is normal value that resolves to true
            # return all rows
            filtered_input = input_df
        else:
            # if the filter series is normal value that resolves to false
            # return no rows, this should never happen so raise a warning.
            get_logger().warning(
                f"A transformer when clause resolves to false in all cases "
                f"({entry.when})."
            )
            return None

        result = run(
            filtered_input, entry.transformation, self.transformer_mapping,
        )
        if isinstance(result, self.series_type):
            return result
        else:
            return self.series_type(result, input_df.index)

    def apply_column_transformation(
        self, input_df: pd.DataFrame, entry_list: List[TransformationEntry],
    ):
        result = reduce(
            lambda series, entry: self.combine_series(
                series, self.apply_transformation_entry(input_df, entry),
            ),
            entry_list,
            None,
        )
        return result

    def apply_transformation_set(
        self, input_df: pd.DataFrame, transformation_set: TransformationSet,
    ) -> pd.DataFrame:
        return reduce(
            lambda target, col_transforms: self.assign(
                target,
                **{
                    col_transforms[0]: self.apply_column_transformation(
                        input_df, col_transforms[1]
                    )
                },
            ),
            transformation_set.items(),
            None,
        )

    def transform(
        self, extractor: BaseConnector, mapping: BaseMapping
    ) -> Iterable[Dict[str, Any]]:
        transformations = mapping.get_transformations()

        df = self.get_dataframe(extractor)

        transformed = reduce(
            self.apply_transformation_set, transformations, df,
        )

        return (r.to_dict() for idx, r in transformed.iterrows())
