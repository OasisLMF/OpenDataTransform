from typing import Any, Dict, Iterable

import pandas as pd

from ..connector.base import BaseConnector
from ..mapping.base import BaseMapping
from .base import BaseRunner


class PandasRunner(BaseRunner):
    def get_dataframe(self, extractor):
        return pd.DataFrame(extractor.extract())

    def transform(
        self, extractor: BaseConnector, mapping: BaseMapping
    ) -> Iterable[Dict[str, Any]]:
        return []
