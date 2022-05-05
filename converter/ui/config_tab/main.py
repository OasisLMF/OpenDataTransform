from typing import List, Type

from __feature__ import true_property  # noqa
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from converter.connector import (
    BaseConnector,
    CsvConnector,
    PostgresConnector,
    SQLiteConnector,
    SQLServerConnector,
)
from converter.runner import BaseRunner, DaskRunner, ModinRunner, PandasRunner
from converter.ui.config_tab.mapping import MappingGroupBox
from converter.ui.fields.dynamic import DynamicClassFormBlock


CONNECTOR_CLASSES: List[Type[BaseConnector]] = list(
    sorted(
        [
            CsvConnector,
            PostgresConnector,
            SQLiteConnector,
            SQLServerConnector,
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
    show_all_updated = Signal(bool)

    def __init__(self, parent, root_config_path, force_all_fields=False):
        super().__init__(parent=parent)

        self.root_config_path = root_config_path
        self.force_all_fields = force_all_fields
        self.show_all_fields = force_all_fields
        self.main_window = parent

        self.layout = QVBoxLayout(self)

        # setup mapping config
        self.layout.addWidget(MappingGroupBox(self, root_config_path))

        # setup extractor config
        self.layout.addWidget(
            DynamicClassFormBlock(
                self,
                "Extractor",
                f"{root_config_path}.extractor",
                CONNECTOR_CLASSES,
            )
        )

        # setup loader config
        self.layout.addWidget(
            DynamicClassFormBlock(
                self, "Loader", f"{root_config_path}.loader", CONNECTOR_CLASSES
            )
        )

        # add runner config
        self.layout.addWidget(
            DynamicClassFormBlock(
                self,
                "Runner",
                f"{root_config_path}.runner",
                RUNNER_CLASSES,
                default_class=PandasRunner,
            )
        )

        # if we dont force all the fields to be shown and a template is set,
        # add a toggle button to show/hide
        if not force_all_fields:
            self.toggle_all_fields_button = QPushButton("Show all fields")
            self.toggle_all_fields_button.clicked.connect(
                self.toggle_all_fields
            )
            self.update_show_field_toggle_button_visibility(
                self.main_window.config
            )
            self.main_window.config_changed.connect(
                self.update_show_field_toggle_button_visibility
            )
            self.layout.addWidget(self.toggle_all_fields_button)
        else:
            self.toggle_all_fields_button = None

        # Add a spacer to push all the fields up when fields are hidden
        self.layout.addStretch()

        self.main_window.running_changed.connect(self.on_running_changed)

    def on_running_changed(self, b):
        self.setEnabled(not b)

    def toggle_all_fields(self):
        self.show_all_fields = not self.show_all_fields
        self.toggle_all_fields_button.text = (
            "Show all fields"
            if not self.show_all_fields
            else "Hide template fields"
        )
        self.show_all_updated.emit(self.show_all_fields)

    def update_show_field_toggle_button_visibility(self, config):
        if self.main_window.config.has_template:
            self.toggle_all_fields_button.show()
        else:
            self.toggle_all_fields_button.hide()
