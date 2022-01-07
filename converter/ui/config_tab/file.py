import os

from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton


class FileField(QHBoxLayout):
    def __init__(self, tab):
        super().__init__()

        self.tab = tab
        self.name_field = QLineEdit()
        self.name_field.setEnabled(False)
        self.addWidget(self.name_field)

        self.file_button = QPushButton("Select")
        self.file_button.clicked.connect(self.on_select_clicked)
        self.addWidget(self.file_button)

    def on_select_clicked(self):
        if self.tab.config.path:
            config_dir = os.path.dirname(self.tab.config.path)
        else:
            config_dir = os.getcwd()

        file_path = QFileDialog.getSaveFileName(
            self.tab,
            caption="Select a file...",
            dir=config_dir,
            options=QFileDialog.DontConfirmOverwrite,
        )[0]

        if file_path:
            self.name_field.setText(os.path.relpath(file_path, config_dir))

    @property
    def value_changed(self):
        return self.name_field.textChanged

    def setValue(self, v):
        self.name_field.setText(v)
