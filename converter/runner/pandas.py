import logging
import re
from functools import reduce
from operator import and_, or_
from typing import Any, Dict, Iterable, List, Union

import pandas as pd
from numpy import nan

from ..connector.base import BaseConnector
from ..mapping.base import BaseMapping, TransformationEntry, TransformationSet
from ..transformers import run
from ..transformers.transform import (
    GroupWrapper,
    RowType,
    TransformerMapping,
    default_match,
    default_replace,
    default_search,
)
from .base import BaseRunner


def get_logger():
    return logging.getLogger(__name__)


#
# Group Wrappers
#


class PandasGroupWrapper(GroupWrapper):
    """
    Base class for the pandas implementation for any and all groups
    """

    def in_operator(self, x, y):
        return reduce(or_, (x == c for c in y), False)

    def not_in_operator(self, x, y):
        return reduce(and_, (x != c for c in y), True)


class PandasAnyWrapper(PandasGroupWrapper):
    """
    Pandas specific implementation of the ``any`` expression
    """

    def check_fn(self, values):
        return reduce(or_, values, False)


class PandasAllWrapper(PandasGroupWrapper):
    """
    Pandas specific implementation of the ``all`` expression
    """

    def check_fn(self, values):
        return reduce(and_, values, True)


#
# Transformer overrides
#


def logical_and_transformer(row, lhs, rhs):
    return lhs & rhs


def logical_or_transformer(row, lhs, rhs):
    return lhs | rhs


def logical_not_transformer(row, value):
    try:
        return not bool(value)
    except ValueError:
        # assume we are dealing with series or
        # dataframe is we get a value error
        return value.apply(lambda v: not bool(v))


def in_transformer(row, lhs, rhs):
    if hasattr(lhs, "is_in"):
        return lhs.is_in(rhs)
    else:
        return reduce(or_, map(lambda s: lhs == s, rhs))


def not_in_transformer(row, lhs, rhs):
    if hasattr(lhs, "is_not_in"):
        return lhs.is_not_in(rhs)
    else:
        return reduce(and_, map(lambda s: lhs != s, rhs))


#
# String Manipulations
#


class StrReplace:
    def __init__(self, series_type):
        self.series_type = series_type

    def __call__(self, row: RowType, target, pattern: re.Pattern, repl):
        if isinstance(target, self.series_type):
            return target.astype(str).str.replace(pattern, repl)
        else:
            return default_replace(row, target, pattern, repl)


class StrMatch:
    def __init__(self, series_type):
        self.series_type = series_type

    def __call__(self, row: RowType, target, pattern: re.Pattern):
        if isinstance(target, self.series_type):
            return target.astype(str).str.match(pattern)
        else:
            return default_match(row, target, pattern)


class StrSearch:
    def __init__(self, series_type):
        self.series_type = series_type

    def __call__(self, row: RowType, target, pattern: re.Pattern):
        if isinstance(target, self.series_type):
            return target.astype(str).str.contains(pattern)
        else:
            return default_search(row, target, pattern)


class StrJoin:
    def __init__(self, series_type):
        self.series_type = series_type

    def to_str(self, obj):
        return (
            obj.astype(str) if isinstance(obj, self.series_type) else str(obj)
        )

    def concat(self, left, right):
        left_is_series = isinstance(left, self.series_type)
        right_is_series = isinstance(right, self.series_type)

        if left_is_series or not right_is_series:
            # if the left it already a series or if the right isn't a series
            # the strings will be concatenated in the correct order
            return self.to_str(left) + self.to_str(right)
        else:
            # if right is a series and left isnt force the join to prepend left
            return self.to_str(right).apply(lambda x: self.to_str(left) + x)

    def join(self, left, join, right):
        return self.concat(self.concat(left, join), right)

    def __call__(self, row: RowType, join, *elements):
        if not elements:
            return ""
        elif len(elements) == 1:
            return self.to_str(elements[0])
        else:
            return reduce(
                lambda reduced, element: self.join(reduced, join, element),
                elements[1:],
                elements[0],
            )


class PandasRunner(BaseRunner):
    """
    Default implementation for a pandas loike runner
    """

    dataframe_type = pd.DataFrame
    series_type = pd.Series

    def get_dataframe(self, extractor: BaseConnector) -> pd.DataFrame:
        """
        Builds a dataframe from the etractors data

        :param extractor: The extractor providing the input data

        :return: The created dataframe
        """
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
        """
        Applies a single transformation to the dataset returning the result
        as a series.

        :param input_df: The dataframe loaded from the extractor
        :param entry: The transformation to apply

        :return: The transformation result
        """
        transformer_mapping: TransformerMapping = {
            "logical_and": logical_and_transformer,
            "logical_or": logical_or_transformer,
            "logical_not": logical_not_transformer,
            "is_in": in_transformer,
            "not_in": not_in_transformer,
            "any": lambda r, values: PandasAnyWrapper(values),
            "all": lambda r, values: PandasAllWrapper(values),
            "str_replace": StrReplace(self.series_type),
            "str_match": StrMatch(self.series_type),
            "str_search": StrSearch(self.series_type),
            "str_join": StrJoin(self.series_type),
        }

        # process the when clause to get a filter series
        filter_series = run(input_df, entry.when, transformer_mapping)

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

        result = run(filtered_input, entry.transformation, transformer_mapping)
        if isinstance(result, self.series_type):
            return result
        else:
            return self.series_type(result, input_df.index)

    def apply_column_transformation(
        self, input_df: pd.DataFrame, entry_list: List[TransformationEntry],
    ):
        """
        Applies all the transformations for a single output column

        :param input_df: The dataframe loaded from the extractor
        :param entry_list: A list of all the transformations to apply to
            generate the output series

        :return: The transformation result
        """
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
        """
        Applies all the transformations to produce the output dataframe

        :param input_df: The dataframe loaded from the extractor
        :param transformation_set: The full set of transformations to apply
            to the ``input_df`` to produce the output dataframe.

        :return: The transformed dataframe
        """
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
