from threading import Thread

from PySide6.QtCore import QThread, QObject, Signal
from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from converter.controller import Controller
from converter.ui.run_tab.log import LogPanel
from converter.ui.run_tab.validation import ValidationPanel


class ControllerRunner(QObject):
    finished = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            Controller(self.config).run()
        finally:
            self.finished.emit()


class RunThread:
    def __init__(self, on_start, on_finish):
        self.on_start = on_start
        self.on_finish = on_finish

        self.worker = None
        self.thread = None

    def start(self, config, moveObjects):
        self.on_start()

        self.thread = QThread()
        self.worker = ControllerRunner(config)
        self.worker.moveToThread(self.thread)

        for obj in moveObjects:
            obj.moveToThread(self.thread)

        self.worker.finished.connect(self.on_finish)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()


class RunTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.layout = QVBoxLayout(self)

        self.validation_panel = ValidationPanel(self)
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
        self.thread.start(
            self.main_window.config_tab.working_config,
            [self.log_panel.widget, self.validation_panel.layout],
        )
