from functools import reduce
from typing import Any, AsyncIterable, Dict

from converter.connector import BaseConnector
from converter.mapping import BaseMapping
from converter.runner.base import BaseAsyncRunner
from converter.types.notset import NotSet, NotSetType


class EagerRunner(BaseAsyncRunner):
    name = "Eager"

    async def transform(
        self, extractor: BaseConnector, mapping: BaseMapping
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Runs the transformation on each row as its passed in and yields the
        result to the loader

        :param extractor: The data connection to extract data from
        :param mapping: Mapping object describing the transformations to apply

        :return: An async iterable containing the transformed data
        """
        transformations = mapping.get_transformations()

        async for row in extractor.aextract():
            transformed = reduce(
                self.apply_transformation_set, transformations, row
            )

            if isinstance(transformed, NotSetType):
                continue

            if len([v for v in transformed.values() if v != NotSet]) > 0:
                # only yield rows that have some values set
                yield transformed
