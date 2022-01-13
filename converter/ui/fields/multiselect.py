from __feature__ import true_property  # noqa
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QListWidget, QListWidgetItem


class MultiSelect(QListWidget):
    def __init__(self, tab, config_path, options):
        super().__init__()
        self.selectionMode = self.MultiSelection

        self.tab = tab
        self.main_window = tab.main_window
        self.config_path = config_path
        self.options = options
        self.selected = []

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

        # set the initial selections
        self.on_config_loaded(tab.main_window.config)
        self.itemSelectionChanged.connect(self.on_selection_changed)

        self.main_window.config_changed.connect(self.on_config_loaded)

    def on_config_loaded(self, new_config):
        self.clearSelection()
        selected = new_config.get(self.config_path, [])
        for selection in selected:
            try:
                idx = self.options.index(selection)
                self.item(idx).setSelected(True)
            except ValueError:
                pass

    def on_selection_changed(self):
        self.main_window.set_working_value(
            self.config_path,
            [item.text() for item in self.selectedItems()],
        )
