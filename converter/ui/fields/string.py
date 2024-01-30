from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit

from converter.ui.fields.base import BaseFieldMixin


class StringField(BaseFieldMixin, QLineEdit):
    def update_ui_from_config(self, config):
        new_value = config.get_template_resolved_value(self.config_path, "")
        if new_value != self.text:
            self.setText(new_value)

    @property
    def change_signal(self):
        return self.textChanged

    def on_change(self, *v):
        self.main_window.set_working_value(self.config_path, *v)


class PasswordField(StringField):
    def __init__(
            self, tab, config_path, *args, defer_initial_ui_update=False, **kwargs
    ):
        super().__init__(tab, config_path, *args, defer_initial_ui_update=False, **kwargs)
        self.echoMode = QLineEdit.Password


class TextAreaField(BaseFieldMixin, QPlainTextEdit):
    def update_ui_from_config(self, config):
        new_value = config.get_template_resolved_value(self.config_path, "")
        if new_value != self.plainText:
            self.setPlainText(new_value)

    @property
    def change_signal(self):
        return self.textChanged

    def on_change(self):
        self.main_window.set_working_value(self.config_path, self.plainText)
