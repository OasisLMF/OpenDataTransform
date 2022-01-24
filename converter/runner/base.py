import asyncio
import json
import logging
from functools import reduce
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Dict,
    Iterable,
    List,
    TypedDict,
    Union,
)

from converter.config import Config
from converter.connector.base import BaseConnector
from converter.mapping.base import (
    BaseMapping,
    ColumnConversions,
    DirectionalMapping,
    TransformationEntry,
)
from converter.metadata.log import log_metadata
from converter.transformers.transform import run
from converter.types.notset import NotSet, NotSetType


RowType = Any


class Converters(TypedDict):
    int: Callable[[Any, bool, List], Union[int, None]]
    float: Callable[[Any, bool, List], Union[float, None]]
    string: Callable[[Any, bool, List], Union[str, None]]


def build_converter(t) -> Callable[[Any, bool, List], Any]:
    def _converter(value, nullable, null_values):
        if nullable and value in null_values:
            return None
        return t(value)

    return _converter


class _BaseRunner:
    row_value_conversions: Converters = {
        "int": build_converter(int),
        "float": build_converter(float),
        "string": build_converter(str),
    }
    name = "Base Runner"
    options_schema = {"type": "object", "properties": {}}

    def __init__(self, config: Config, **options):
        self.config = config
        self._options = options

    @classmethod
    def log_type_coercion_error(cls, row, column, value, to_type, reason):
        """
        Logs a failure of a row type coercion

        :param row: The input row that failed
        :param column: The name of the column in which the error occurred
        :param value: The value of the failing column
        :param to_type: The type the coercion was attempting
        :param reason: The error message
        """
        logging.warning(
            f"Cannot coerce {column} ({value}) to {to_type}. "
            f"Reason: {reason}. Row: {json.dumps(row)}."
        )

    def coerce_row_types(self, row, conversions: ColumnConversions):
        """
        Changes data types of each input column. If a cast fails a warning
        will be written to the logs and the row will be ignored.

        :param row: The input row.
        :param conversions: The set of conversions to run

        :return: The updated input row if there are no errors, ``None`` if
            any updates fail.
        """
        coerced_row = {}
        for column, value in row.items():
            conversion = conversions.get(column)
            if not conversion:
                coerced_row[column] = value
            else:
                try:
                    coerced_row[column] = self.row_value_conversions[
                        conversion.type  # type: ignore
                    ](value, conversion.nullable, conversion.null_values)
                except Exception as e:
                    self.log_type_coercion_error(
                        row, column, row[column], conversion.type, e
                    )
                    return None

        return coerced_row

    def combine_column(
        self,
        row,
        current_column_value: Union[Any, NotSetType],
        entry: TransformationEntry,
    ):
        """
        Combines the current column value with the result of the
        transformation. If the current value is ``NotSet`` the value of the
        current transformation will be calculated and applied.

        :param row: The row loaded from the extractor
        :param current_column_value: The current transformed value
        :param entry: The transformation to apply

        :return: The combined column value
        """
        if current_column_value is not NotSet:
            return current_column_value

        return self.apply_transformation_entry(row, entry)

    def assign(
        self,
        input_row: RowType,
        output_row: Union[RowType, NotSetType],
        **assignments,
    ) -> RowType:
        """
        Helper function for assigning a values to the output row.

        :param input_row: The row loaded from the extractor
        :param output_row: The row object to assign to or None
        :param assignments: The assignments to apply to the row

        :return: The updated row
        """
        return {
            **(output_row or {}),  # type: ignore
            **assignments,
        }

    def apply_transformation_entry(
        self,
        row: RowType,
        entry: TransformationEntry,
    ) -> RowType:
        """
        Applies a single transformation to the row returning the result
        as a column value.

        :param row: The row loaded from the extractor
        :param entry: The transformation to apply

        :return: The transformation result
        """

        # process the when clause to get a filter series
        if run(row, entry.when_tree or entry.when):
            return run(row, entry.transformation_tree or entry.transformation)
        else:
            return NotSet

    def apply_column_transformation(
        self,
        row: RowType,
        entry_list: List[TransformationEntry],
    ):
        """
        Applies all the transformations for a single output column

        :param row: The current input row
        :param entry_list: A list of all the transformations to apply to
            generate the output series

        :return: The transformation result
        """
        result = reduce(
            lambda current_column_value, entry: self.combine_column(
                row,
                current_column_value,
                entry,
            ),
            entry_list,
            NotSet,
        )
        return result

    def apply_transformation_set(
        self,
        row: RowType,
        transformations: DirectionalMapping,
    ) -> RowType:
        """
        Applies all the transformations to produce the output row

        :param row: The current input row
        :param transformations: The full set of column conversions and
            transformation sets to apply to the ``row`` row.

        :return: The transformed row
        """
        logging.info(
            f"Running transformation set {transformations.input_format} -> "
            f"{transformations.output_format}."
        )
        coerced_row = self.coerce_row_types(row, transformations.types)
        if coerced_row is None:
            return NotSet

        return reduce(
            lambda target, col_transforms: self.assign(
                row,
                target,
                **{
                    col_transforms[0]: self.apply_column_transformation(
                        coerced_row, col_transforms[1]
                    )
                },
            ),
            transformations.transformation_set.items(),
            NotSet,
        )


class BaseRunner(_BaseRunner):
    """
    Runs the transformations on the extracted data and writes
    it to the data loader

    :param config: The global config for the system
    """

    name = "Base"

    def run(
        self,
        extractor: BaseConnector,
        mapping: BaseMapping,
        loader: BaseConnector,
    ):
        """
        Runs the transformation process and sends the data to the data loader

        :param extractor: The data connection to extract data from
        :param mapping: Mapping object describing the transformations to apply
        :param loader: The data connection to load data to
        """
        log_metadata(self.config, mapping)
        loader.load(self.transform(extractor, mapping))

    def transform(
        self, extractor: BaseConnector, mapping: BaseMapping
    ) -> Iterable[Dict[str, Any]]:
        """
        Performs the transformation

        :param extractor: The data connection to extract data from
        :param mapping: Mapping object describing the transformations to apply

        :return: An iterable containing the transformed data
        """
        raise NotImplementedError()


class BaseAsyncRunner(_BaseRunner):
    """
    Runs the transformations on the extracted data and writes it to the data
    loader. The connectors and transformation are all async objects allowing
    for async data providers such as websockets or polled apis to be used as
    a data connection.

    The connectors and transformations should be done in an eager way so that
    each row is processed and passed to the loader as it's received or cached
    for processing later. After each row if processed the next should be
    awaited so that new data can be extracted.

    :param config: The global config for the system
    """

    def run(
        self,
        extractor: BaseConnector,
        mapping: BaseMapping,
        loader: BaseConnector,
    ):
        log_metadata(self.config, mapping)
        asyncio.run(loader.aload(self.transform(extractor, mapping)))

    async def transform(
        self, extractor: BaseConnector, mapping: BaseMapping
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Performs the transformation

        :param extractor: The data connection to extract data from
        :param mapping: Mapping object describing the transformations to apply

        :return: An iterable containing the transformed data
        """
        raise NotImplementedError()
        # This is here so that mypy knows its an async iterable
        yield {}  # pragma: no cover
