from threading import Thread

from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from converter.controller import Controller
from converter.ui.run_tab.log import LogPanel


class RunThread(Thread):
    def __init__(self, config, on_start, on_finish):
        super().__init__()
        self.config = config
        self.on_start = on_start
        self.on_finish = on_finish

    def run(self):
        try:
            self.on_start()
            Controller(self.config).run()
        finally:
            self.on_finish()


class RunTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.layout = QVBoxLayout(self)

        self.log_panel = LogPanel(self)
        self.layout.addWidget(self.log_panel.widget)

        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.run)
        self.layout.addWidget(self.run_button)

        self.main_window.running_changed.connect(
            lambda b: self.run_button.setEnabled(not b)
        )

    def run(self):
        self.log_panel.clear()
        RunThread(
            self.main_window.config_tab.working_config,
            lambda: self.main_window.running_changed.emit(True),
            lambda: self.main_window.running_changed.emit(False),
        ).start()
