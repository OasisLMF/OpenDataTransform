"""
Generated random data and transforms it printing the result to the console

Each row is processed as soon as it is received and passed onto the console
loader.
"""
import asyncio
import json
from random import randint

from converter.connector import BaseConnector
from converter.mapping import BaseMapping
from converter.mapping.base import TransformationEntry


class RandomExtractor(BaseConnector):
    async def aextract(self):
        while True:
            row = {
                "a": randint(0, 100),
                "b": randint(0, 100),
            }
            yield row
            await asyncio.sleep(1)


class ConsoleLoader(BaseConnector):
    async def aload(self, data):
        async for row in data:
            print(json.dumps(row))


class Mapping(BaseMapping):
    def get_transformations(self):
        return [
            {
                "a": [TransformationEntry(transformation="a")],
                "b": [TransformationEntry(transformation="b")],
                "c": [TransformationEntry(transformation="a * 2")],
                "d": [TransformationEntry(transformation="b + 3")],
            },
        ]
