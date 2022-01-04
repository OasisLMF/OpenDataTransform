import logging

from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QPlainTextEdit


class LogPanel(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.readOnly = True

    def emit(self, record):
        msg = f"{record.levelname}: {record.msg}"
        self.widget.appendPlainText(msg)

    def clear(self):
        self.widget.setPlainText("")
