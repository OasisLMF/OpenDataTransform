import os

from __feature__ import true_property  # noqa
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTabWidget, QScrollArea

from converter.config import Config
from converter.ui.config_tab.main import ConfigTab
from converter.ui.metadata_tab.main import MetadataTab
from converter.ui.run_tab.main import RunTab


class MainWindow(QMainWindow):
    config_changed = Signal(object)
    running_changed = Signal(bool)

    def __init__(self, config, update_log_paths):
        super().__init__()

        # initialise the config
        self._loaded_config = config
        self._working_config = Config()
        self._default_working_config = Config()

        # setup the top menu
        self._create_actions()
        self._create_menu_bar()

        # setup tabs
        tabs = QTabWidget()

        self.config_tab = ConfigTab(self)
        config_scroll_wrapper = QScrollArea()
        config_scroll_wrapper.setWidget(self.config_tab)
        tabs.addTab(config_scroll_wrapper, "Config")

        self.metadata_tab = MetadataTab(self)
        meta_scroll_wrapper = QScrollArea()
        meta_scroll_wrapper.setWidget(self.metadata_tab)
        tabs.addTab(meta_scroll_wrapper, "Metadata")

        self.run_tab = RunTab(self)
        run_scroll_wrapper = QScrollArea()
        run_scroll_wrapper.setWidget(self.run_tab)
        tabs.addTab(run_scroll_wrapper, "Run")

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
        if self.config_has_changes:
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
            self.reset_changes(file_path)

            # update the new log location
            self.update_log_paths(file_path)

    def _handle_file_save(self, overwrite=False):
        if not overwrite or not self._loaded_config.path:
            file_path = QFileDialog.getSaveFileName(
                self,
                caption="Save the current config...",
                dir=os.getcwd(),
                filter="Config Files (*.yml *.yaml)",
            )[0]
        else:
            file_path = self._loaded_config.path

        if file_path:
            self.config.save(file_path)
            self.reset_changes(file_path)

    def reset_changes(self, file_path):
        self._loaded_config = Config(
            config_path=file_path,
            overrides=self._loaded_config.overrides,
            env=self._loaded_config.env,
            argv=self._loaded_config.argv,
        )
        self._working_config = Config()
        self._default_working_config = Config()
        self.config_changed.emit(self._loaded_config)

    @property
    def config_has_changes(self):
        return bool(self._working_config)

    def set_working_value(self, path, v):
        if self._working_config.get(path, None) == v:
            return
        self._working_config.set(path, v)

    def set_default_working_value(self, path, v):
        self._default_working_config.set(path, v)

    @property
    def config(self):
        config = self._loaded_config
        return Config(
            config_path=config.path,
            overrides=config.merge_config_sources(
                self._default_working_config.config,
                self._working_config.config,
            ),
        )

    def _create_menu_bar(self):
        bar = self.menuBar()

        # create file menu items
        file_menu = bar.addMenu("&File")
        file_menu.addAction(self.open_config)
        file_menu.addAction(self.save_config)
        file_menu.addAction(self.save_config_as)
