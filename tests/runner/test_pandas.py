import os
from tempfile import TemporaryDirectory

import pandas as pd

from converter.connector import BaseConnector
from converter.files import write_yaml
from converter.mapping import FileMapping
from converter.runner import PandasRunner


class FakeConnector(BaseConnector):
    def __init__(self, data=None, **options):
        super().__init__(**options)
        self.data = data

    def extract(self):
        return self.data

    def load(self, data):
        self.data = data


def test_mapping_applies_to_all_cols___forward_and_reverse_gets_to_the_input():
    input_data = [
        {'a': 1, 'b': 2},
        {'a': 3, 'b': 4},
        {'a': 5, 'b': 6},
        {'a': 7, 'b': 8},
    ]

    with TemporaryDirectory() as search:
        write_yaml(
            os.path.join(search, "A-B.yml"),
            {
                "input_format": "A",
                "output_format": "B",
                "forward_transform": {
                    "c": [{"transformation": "a * 2"}],
                    "b": [{"transformation": "b + 3"}],
                },
                "reverse_transform": {
                    "a": [{"transformation": "c / 2"}],
                    "b": [{"transformation": "d - 2"}],
                },
            },
        )

        # run forward
        forward_mapping = FileMapping(
            input_format="A",
            output_format="B",
            standard_search_path=search,
        )
        forward_extractor = FakeConnector(data=input_data)
        forward_loader = FakeConnector()

        PandasRunner().run(forward_extractor, forward_mapping, forward_loader)

        assert forward_loader.data == [
            {'c': 2, 'd': 5},
            {'c': 6, 'd': 7},
            {'c': 10, 'd': 9},
            {'c': 14, 'd': 11},
        ]

        # reverse runner
        reverse_mapping = FileMapping(
            input_format="B",
            output_format="A",
            standard_search_path=search,
        )
        reverse_extractor = forward_loader
        reverse_loader = FakeConnector()

        assert reverse_loader.data == input_data
