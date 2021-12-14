import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QGroupBox, QComboBox
from __feature__ import true_property

from converter.mapping import FileMapping


class ConfigTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout(self)

        # setup mapping config
        mapping_group_box = QGroupBox("Mapping")
        mapping_group_box.setLayout(self._create_mapping_form())
        self.layout.addWidget(mapping_group_box)

        # setup extractor config
        extractor_group_box = QGroupBox("Extractor")
        extractor_group_box.setLayout(self._create_extractor_config())
        self.layout.addWidget(extractor_group_box)

        # setup loader config
        loader_group_box = QGroupBox("Loader")
        loader_group_box.setLayout(self._create_loader_config())
        self.layout.addWidget(loader_group_box)

    def _create_mapping_form(self):
        mapping = FileMapping(
            self.parentWidget().config.get(),
            raise_errors=False
        )

        formats = list(mapping.mapping_graph.nodes)

        layout = QFormLayout()

        from_combo = QComboBox()
        from_combo.addItems(formats)
        layout.addRow(QLabel("From:"), from_combo)

        to_combo = QComboBox()
        to_combo.addItems(formats)
        layout.addRow(QLabel("To:"), to_combo)

        return layout

    def _create_extractor_config(self):
        layout = QFormLayout()

        return layout

    def _create_loader_config(self):
        layout = QFormLayout()

        return layout
