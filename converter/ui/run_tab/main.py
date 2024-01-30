from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from converter.ui.run_tab.log import LogPanel
from converter.ui.run_tab.validation import ValidationPanel
from converter.ui.run_tab.worker import RunThread


class RunTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.layout = QVBoxLayout(self)

        self.validation_panel = ValidationPanel(self.main_window)
        self.layout.addLayout(self.validation_panel.layout)

        self.log_panel = LogPanel(self)
        self.layout.addWidget(self.log_panel.widget)

        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.run)
        self.layout.addWidget(self.run_button)

        self.main_window.running_changed.connect(
            lambda b: self.run_button.setEnabled(not b)
        )

        self.thread = RunThread(
            lambda: self.main_window.running_changed.emit(True),
            lambda: self.main_window.running_changed.emit(False),
        )

    def run(self):
        self.validation_panel.clear()
        self.log_panel.clear()

        self.main_window.update_log_paths(self.main_window.config.path)
        self.thread.start(
            self.main_window.config,
            self.log_panel,
            self.validation_panel,
        )
