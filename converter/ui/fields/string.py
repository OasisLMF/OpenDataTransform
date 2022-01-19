from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit

from converter.ui.fields.base import BaseFieldMixin


class StringField(BaseFieldMixin, QLineEdit):
    def update_ui_from_config(self, config):
        self.setText(config.get(self.config_path, ""))

    @property
    def change_signal(self):
        return self.textChanged

    def on_change(self, *v):
        self.main_window.set_working_value(self.config_path, *v)


class TextAreaField(BaseFieldMixin, QPlainTextEdit):
    def update_ui_from_config(self, config):
        self.setPlainText(config.get(self.config_path, ""))

    @property
    def change_signal(self):
        return self.textChanged

    def on_change(self):
        self.main_window.set_working_value(self.config_path, self.plainText)
