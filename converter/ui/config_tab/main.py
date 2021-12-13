from PySide6.QtWidgets import QWidget, QVBoxLayout
from __feature__ import true_property


class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
