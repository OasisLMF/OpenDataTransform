from PySide6.QtCore import Slot
from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLabel

from converter.mapping import FileMapping
from converter.mapping.base import MappingFormat


class MappingCombo(QComboBox):
    def __init__(self, tab, config_path, options):
        super().__init__()
        self.tab = tab
        self.main_window = tab.main_window
        self.config_path = config_path
        self.options = options

        self.addItems([
            f"{opt.name} v{opt.version}" if opt else ""
            for opt in self.options
        ])

        self.update_selection_from_config(self.tab.main_window.config)
        self.main_window.config_changed.connect(self.update_selection_from_config)

    def on_selection_changed(self, v):
        option = self.options[self.currentIndex]
        self.tab.main_window.set_working_value(
            self.config_path, {"name": option.name, "version": option.version} if option else None
        )

    def refresh_options(self, options):
        self.options = options
        self.clear()
        self.addItems([
            f"{opt.name} v{opt.version}" if opt else ""
            for opt in self.options
        ])

    def update_selection_from_config(self, config):
        try:
            self.currentTextChanged.disconnect(self.on_selection_changed)
        except RuntimeError:
            pass

        try:
            selection = config.get(self.config_path)
            selected_index = self.options.index(MappingFormat(**selection) if selection else None)
            if selected_index != self.currentIndex:
                self.setCurrentIndex(selected_index)
        except (ValueError, KeyError):
            self.setCurrentIndex(0)

        self.currentTextChanged.connect(self.on_selection_changed)


class MappingGroupBox(QGroupBox):
    def __init__(self, tab, root_config_path, show_all_fields):
        super(MappingGroupBox, self).__init__("Mapping")

        self.tab = tab
        self.show_all_fields = show_all_fields

        layout = QFormLayout()

        config = self.tab.main_window.config
        formats = self.get_mapping_formats(config)

        self.input_combo = MappingCombo(self.tab, f"{root_config_path}.input_format", formats)
        layout.addRow(QLabel("From:"), self.input_combo)

        self.output_combo = MappingCombo(self.tab, f"{root_config_path}.output_format", formats)
        layout.addRow(QLabel("To:"), self.output_combo)

        self.setLayout(layout)

    @classmethod
    def get_mapping_formats(cls, config):
        return [None] + list(
            FileMapping(config, raise_errors=False).mapping_graph.nodes
        )
