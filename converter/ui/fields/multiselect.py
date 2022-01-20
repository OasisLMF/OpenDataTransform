from __feature__ import true_property  # noqa
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from converter.ui.fields.base import BaseFieldMixin


class MultiSelect(BaseFieldMixin, QListWidget):
    def __init__(self, tab, config_path, options):
        self.options = options
        self.selected = []

        super().__init__(tab, config_path, defer_initial_ui_update=True)
        self.selectionMode = self.MultiSelection

        # add options
        for opt in options:
            if isinstance(opt, str):
                self.addItem(QListWidgetItem(opt))
            else:
                group_header = QListWidgetItem(opt["group"])
                group_header.setFlags(Qt.ItemFlag.NoItemFlags)
                group_header.setForeground(Qt.black)
                header_font = QFont()
                header_font.setWeight(QFont.Bold)
                group_header.setFont(header_font)

                self.addItem(group_header)

                for group_opt in opt["entries"]:
                    self.addItem(QListWidgetItem(group_opt))

        self.on_config_changed(self.main_window.config)

    def update_ui_from_config(self, config):
        self.clearSelection()
        selected = config.get_template_resolved_value(self.config_path, [])
        for selection in selected:
            try:
                idx = self.options.index(selection)
                self.item(idx).setSelected(True)
            except ValueError:
                pass

    @property
    def change_signal(self):
        return self.itemSelectionChanged

    def on_change(self):
        self.main_window.set_working_value(
            self.config_path,
            [item.text() for item in self.selectedItems()],
        )
