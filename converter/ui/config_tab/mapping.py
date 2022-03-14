from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox

from converter.mapping import FileMapping
from converter.mapping.base import MappingFormat
from converter.ui.fields.base import BaseFieldMixin
from converter.ui.fields.label import Label


class MappingCombo(BaseFieldMixin, QComboBox):
    def __init__(self, tab, config_path, options):
        self.options = options

        super().__init__(tab, config_path, defer_initial_ui_update=True)

        self.addItems(
            [
                f"{opt.name} v{opt.version}" if opt else ""
                for opt in self.options
            ]
        )
        self.on_config_changed(self.main_window.config)

    def refresh_options(self, options):
        self.options = options
        self.clear()
        self.addItems(
            [
                f"{opt.name} v{opt.version}" if opt else ""
                for opt in self.options
            ]
        )

    def update_ui_from_config(self, config):
        try:
            selection = config.get_template_resolved_value(self.config_path)
            selected_index = self.options.index(
                MappingFormat(**selection) if selection else None
            )
            if selected_index != self.currentIndex:
                self.setCurrentIndex(selected_index)
        except (ValueError, KeyError):
            self.setCurrentIndex(0)

    @property
    def change_signal(self):
        return self.currentTextChanged

    def on_change(self, v):
        option = self.options[self.currentIndex]
        self.tab.main_window.set_working_value(
            self.config_path,
            {"name": option.name, "version": option.version}
            if option
            else None,
        )


class MappingGroupBox(QGroupBox):
    def __init__(self, tab, root_config_path):
        super(MappingGroupBox, self).__init__("Mapping")

        self.tab = tab
        self.main_window = tab.main_window
        self.root_config_path = root_config_path

        self.layout = QFormLayout()

        config = self.tab.main_window.config
        self.formats = self.get_mapping_formats(config)

        self.input_label = Label(
            "From:", self.tab, f"{root_config_path}.input_format"
        )
        self.input_combo = MappingCombo(
            self.tab, f"{root_config_path}.input_format", self.formats
        )
        self.layout.addRow(self.input_label, self.input_combo)

        self.output_label = Label(
            "To:", self.tab, f"{root_config_path}.output_format"
        )
        self.output_combo = MappingCombo(
            self.tab, f"{root_config_path}.output_format", self.formats
        )
        self.layout.addRow(self.output_label, self.output_combo)

        self.setLayout(self.layout)

    @classmethod
    def get_mapping_formats(cls, config):
        return [None] + list(
            FileMapping(config, "", raise_errors=False).mapping_graph.nodes
        )
