from typing import List, Type

from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QVBoxLayout, QWidget

from converter.config import Config
from converter.connector import BaseConnector, CsvConnector
from converter.runner import BaseRunner, DaskRunner, ModinRunner, PandasRunner
from converter.ui.config_tab.dynamic import DynamicClassFormBlock
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

        parent.config_changed.connect(self.clear_changes)

        self.layout = QVBoxLayout(self)
        self._working_config = Config()
        self._default_working_config = Config()

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

    @property
    def config(self):
        return self.main_window.config

    @property
    def working_config(self):
        config = self.config
        return Config(
            config_path=config.path,
            overrides=config.merge_config_sources(
                self._default_working_config.config,
                self._working_config.config,
            ),
        )

    @property
    def has_changes(self):
        return bool(self._working_config)

    def set_working_value(self, path, v):
        if self._working_config.get(path, None) == v:
            return
        self._working_config.set(path, v)

    def set_default_working_value(self, path, v):
        self._default_working_config.set(path, v)

    def clear_changes(self):
        self._working_config = Config()
        self._default_working_config = Config()