import logging

from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QPlainTextEdit


class LogPanel(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setEnabled(False)

        self.setFormatter(
            logging.Formatter("%(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self)
        logging.getLogger().setLevel(logging.DEBUG)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def clear(self):
        self.widget.setPlainText("")
