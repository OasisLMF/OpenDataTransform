import asyncio
from functools import reduce
from typing import Any, AsyncIterable, Dict, Iterable, List, Union

from converter.config import Config
from converter.connector.base import BaseConnector
from converter.mapping.base import (
    BaseMapping,
    TransformationEntry,
    TransformationSet,
)
from converter.transformers.transform import run


RowType = Any


class NotSetType:
    """
    Value used when a transformation has not been applied due to  fix
    ambiguity with ``None`` being a valid value
    """

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, NotSetType)


NotSet = NotSetType()


class _BaseRunner:
    def __init__(self, config: Config, **options):
        self.config = config
        self._options = options

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
        :param current_column_value: Series representing the current
            transformed value
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
        **assignments
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
        self, row: RowType, entry: TransformationEntry,
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
        self, row: RowType, entry_list: List[TransformationEntry],
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
                row, current_column_value, entry,
            ),
            entry_list,
            NotSet,
        )
        return result

    def apply_transformation_set(
        self, row: RowType, transformation_set: TransformationSet,
    ) -> RowType:
        """
        Applies all the transformations to produce the output row

        :param row: The current input row
        :param transformation_set: The full set of transformations to apply
            to the ``row`` to produce the output row.

        :return: The transformed dataframe
        """
        return reduce(
            lambda target, col_transforms: self.assign(
                row,
                target,
                **{
                    col_transforms[0]: self.apply_column_transformation(
                        row, col_transforms[1]
                    )
                },
            ),
            transformation_set.items(),
            NotSet,
        )


class BaseRunner(_BaseRunner):
    """
    Runs the transformations on the extracted data and writes
    it to the data loader

    :param config: The global config for the system
    """

    def run(
        self,
        extractor: BaseConnector,
        mapping: BaseMapping,
        loader: BaseConnector,
    ):
        """
        Runs the transformation process and swnds the data to the data loader

        :param extractor: The data connection to extract data from
        :param mapping: Mapping object describing the transformations to apply
        :param loader: The data connection to load data to
        """
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
        yield {}  # pragma: no cover
