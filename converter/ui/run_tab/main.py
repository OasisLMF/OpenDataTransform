from PySide6.QtWidgets import QVBoxLayout, QWidget
from __feature__ import true_property


class RunTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
