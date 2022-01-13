from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit


class StringField(QLineEdit):
    def __init__(self, tab, config_path):
        super().__init__()

        self.tab = tab
        self.main_window = tab.main_window
        self.config_path = config_path

        self.on_config_loaded(tab.main_window.config)
        self.textChanged.connect(self.on_changed)

        self.main_window.config_changed.connect(self.on_config_loaded)

    def on_config_loaded(self, new_config):
        self.setText(new_config.get(self.config_path, ""))

    def on_changed(self, v):
        self.main_window.set_working_value(self.config_path, v)


class TextAreaField(QPlainTextEdit):
    def __init__(self, tab, config_path):
        super().__init__()

        self.tab = tab
        self.main_window = tab.main_window
        self.config_path = config_path

        self.on_config_loaded(tab.main_window.config)
        self.textChanged.connect(self.on_changed)

        self.main_window.config_changed.connect(self.on_config_loaded)

    def on_config_loaded(self, new_config):
        self.setPlainText(new_config.get(self.config_path, ""))

    def on_changed(self, v):
        self.main_window.set_working_value(self.config_path, v)
