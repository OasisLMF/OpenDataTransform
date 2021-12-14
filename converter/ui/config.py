from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

from converter.config import Config


class ConfigWidget(QWidget):
    changed = Signal(object)

    def __init__(self, data: Config):
        super().__init__()

        self._data = data

    def get(self):
        return self._data

    def set(self, new_data):
        self._data = new_data
        self.changed.emit(self._data)
