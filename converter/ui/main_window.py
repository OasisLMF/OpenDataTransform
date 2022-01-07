import os

from __feature__ import true_property  # noqa
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTabWidget

from converter.config import Config
from converter.ui.config_tab.main import ConfigTab
from converter.ui.run_tab.main import RunTab


class MainWindow(QMainWindow):
    config_changed = Signal(object)
    running_changed = Signal(bool)

    def __init__(self, config, update_log_paths):
        super().__init__()

        # initialise the config
        self.config = config

        # setup the top menu
        self._create_actions()
        self._create_menu_bar()

        # setup tabs
        tabs = QTabWidget()

        self.config_tab = ConfigTab(self)
        tabs.addTab(self.config_tab, "Config")

        self.run_tab = RunTab(self)
        tabs.addTab(self.run_tab, "Run")

        self.setCentralWidget(tabs)

        self.running_changed.connect(
            lambda b: self.menuBar().setEnabled(not b)
        )

        self.update_log_paths = update_log_paths

    def _create_actions(self):
        # create config actions
        self.open_config = QAction("&Open")
        self.open_config.triggered.connect(self._handle_file_open)
        self.save_config = QAction("&Save")
        self.save_config.triggered.connect(
            lambda: self._handle_file_save(overwrite=True)
        )
        self.save_config_as = QAction("&Save As...")
        self.save_config_as.triggered.connect(self._handle_file_save)

    def _handle_file_open(self):
        if self.config_tab.has_changes:
            msg = QMessageBox(
                QMessageBox.Warning,
                "Are you sure?",
                (
                    "You have unsaved changes to your current config. "
                    "If you continue all unsaved changes will be lost."
                ),
                buttons=QMessageBox.Open | QMessageBox.Cancel,
            )

            if msg.exec_() == QMessageBox.Cancel:
                return

        file_path = QFileDialog.getOpenFileName(
            self,
            caption="Open a new config...",
            dir=os.getcwd(),
            filter="Config Files (*.yml *.yaml)",
        )[0]

        if file_path:
            self.config = Config(
                config_path=file_path,
                overrides=self.config.overrides,
                env=self.config.env,
                argv=self.config.argv,
            )
            self.config_changed.emit(self.config)

            # update the new log location
            self.update_log_paths(file_path)

    def _handle_file_save(self, overwrite=False):
        if not overwrite or not self.config.path:
            file_path = QFileDialog.getSaveFileName(
                self,
                caption="Save the current config...",
                dir=os.getcwd(),
                filter="Config Files (*.yml *.yaml)",
            )[0]
        else:
            file_path = self.config.path

        if file_path:
            self.config_tab.working_config.save(file_path)

            self.config = Config(
                config_path=file_path,
                overrides=self.config.overrides,
                env=self.config.env,
                argv=self.config.argv,
            )
            self.config_changed.emit(self.config)

    def _create_menu_bar(self):
        bar = self.menuBar()

        # create file menu items
        file_menu = bar.addMenu("&File")
        file_menu.addAction(self.open_config)
        file_menu.addAction(self.save_config)
        file_menu.addAction(self.save_config_as)
