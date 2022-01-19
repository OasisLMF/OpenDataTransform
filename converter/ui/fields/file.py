import os

from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton

from converter.ui.fields.base import BaseFieldMixin


class FileField(BaseFieldMixin, QHBoxLayout):
    def __init__(self, tab, config_path):
        self.name_field = QLineEdit()
        self.name_field.setEnabled(False)

        self.file_button = QPushButton("Select")
        self.file_button.clicked.connect(self.on_select_clicked)

        super().__init__(tab, config_path)

        self.addWidget(self.name_field)
        self.addWidget(self.file_button)

    def on_select_clicked(self):
        if self.main_window.config.path:
            config_dir = os.path.dirname(self.main_window.config.path)
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
    def change_signal(self):
        return self.name_field.textChanged

    def on_change(self, t):
        self.main_window.set_working_value(self.config_path, t)

    def update_ui_from_config(self, config):
        self.name_field.setText(config.get(self.config_path, ""))
