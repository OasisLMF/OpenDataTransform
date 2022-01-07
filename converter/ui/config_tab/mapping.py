from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLabel

from converter.mapping import FileMapping


class MappingCombo(QComboBox):
    def __init__(self, tab, prop, options):
        super().__init__()
        self.tab = tab
        self.prop = prop
        self.options = options

        self.addItems(self.options)

        self.update_selection_from_config(self.tab.main_window.config)
        self.currentTextChanged.connect(
            lambda v: self.tab.main_window.set_working_value(f"mapping.options.{prop}", v)
        )

    def refresh_options(self, options):
        self.options = options
        self.clear()
        self.addItems(self.options)

    def update_selection_from_config(self, config):
        try:
            current_index = self.options.index(
                config.get(f"mapping.options.{self.prop}", "")
            )
            self.setCurrentIndex(current_index)
        except ValueError:
            self.setCurrentIndex(0)


class MappingGroupBox(QGroupBox):
    def __init__(self, tab):
        super(MappingGroupBox, self).__init__("Mapping")

        self.tab = tab

        layout = QFormLayout()

        config = self.tab.main_window.config
        formats = self.get_mapping_formats(config)

        self.input_combo = MappingCombo(self.tab, "input_format", formats)
        layout.addRow(QLabel("From:"), self.input_combo)

        self.output_combo = MappingCombo(self.tab, "output_format", formats)
        layout.addRow(QLabel("To:"), self.output_combo)

        # connect the combobox to be update when a config is loaded
        self.tab.main_window.config_changed.connect(
            self.refresh_on_config_load
        )

        self.setLayout(layout)

    @classmethod
    def get_mapping_formats(cls, config):
        return [""] + list(
            FileMapping(config, raise_errors=False).mapping_graph.nodes
        )

    def refresh_on_config_load(self, new_config):
        formats = self.get_mapping_formats(new_config)

        self.input_combo.refresh_options(formats)
        self.input_combo.update_selection_from_config(new_config)

        self.output_combo.refresh_options(formats)
        self.output_combo.update_selection_from_config(new_config)
