from typing import List, Type

from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QVBoxLayout, QWidget

from converter.connector import BaseConnector, CsvConnector
from converter.runner import BaseRunner, DaskRunner, ModinRunner, PandasRunner
from converter.ui.fields.dynamic import DynamicClassFormBlock
from converter.ui.config_tab.mapping import MappingGroupBox


CONNECTOR_CLASSES: List[Type[BaseConnector]] = list(
    sorted(
        [
            CsvConnector,
        ],
        key=lambda c: c.name,
    )
)

RUNNER_CLASSES: List[Type[BaseRunner]] = list(
    sorted(
        [
            PandasRunner,
            DaskRunner,
            ModinRunner,
        ],
        key=lambda c: c.name,
    )
)


class ConfigTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.main_window = parent

        self.layout = QVBoxLayout(self)

        # setup mapping config
        self.layout.addWidget(MappingGroupBox(self))

        # setup extractor config
        self.layout.addWidget(
            DynamicClassFormBlock(
                self, "Extractor", "extractor", CONNECTOR_CLASSES
            )
        )

        # setup loader config
        self.layout.addWidget(
            DynamicClassFormBlock(self, "Loader", "loader", CONNECTOR_CLASSES)
        )

        # add runner config
        self.layout.addWidget(
            DynamicClassFormBlock(
                self,
                "Runner",
                "runner",
                RUNNER_CLASSES,
                default_class=PandasRunner,
            )
        )

        self.main_window.running_changed.connect(
            lambda b: self.setEnabled(not b)
        )
