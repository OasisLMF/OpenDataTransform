from converter.config import Config
from converter.connector import BaseConnector


class FakeConnector(BaseConnector):
    def __init__(self, data=None, **options):
        super().__init__(Config(), **options)
        self.data = data or []

    def extract(self):
        return self.data

    def load(self, data):
        self.data = list(data)

    async def aextract(self):
        for row in self.data:
            yield row

    async def aload(self, data):
        self.data = [row async for row in data]
