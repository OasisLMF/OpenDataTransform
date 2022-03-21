import os

from __feature__ import true_property  # noqa
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QTabBar,
    QTabWidget,
)

from converter.config import Config
from converter.ui.config_tab.add_tab_button import AddTabButton
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

        self.minimumWidth = 750

        # setup tabs
        self.tabs = QTabWidget()
        self.tabs.tabsClosable = True
        self.tabs.tabCloseRequested.connect(self.on_close_tab)

        self.metadata_tab = MetadataTab(self)
        meta_scroll_wrapper = QScrollArea()
        meta_scroll_wrapper.setWidget(self.metadata_tab)
        self.tabs.addTab(meta_scroll_wrapper, "Metadata")
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)

        self.run_tab = RunTab(self)
        self.tabs.addTab(self.run_tab, "Run")
        self.tabs.tabBar().setTabButton(1, QTabBar.RightSide, None)

        # add create tab button
        self.tab_button = AddTabButton(self)
        self.tabs.setCornerWidget(self.tab_button)

        self.config_tabs = {}
        self.initialise_config_tabs(self.config)
        self.config_changed.connect(self.initialise_config_tabs)

        self.setCentralWidget(self.tabs)

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

            # setup the config tabs
            self.initialise_config_tabs(self.config)

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
            env=self._loaded_config.env,
            argv=self._loaded_config.argv,
        )
        self._working_config = Config()
        self._default_working_config = Config()
        self.config_changed.emit(self.config)

    @property
    def config_has_changes(self):
        return bool(self._working_config)

    def set_working_value(self, path, v):
        current = self.config.get(path, None)

        if current == v:
            return

        self._working_config.set(path, v)
        self.config_changed.emit(self.config)

    def set_default_working_value(self, path, v):
        self._default_working_config.set(path, v)

    @property
    def config(self):
        config = Config(
            overrides=Config.merge_config_sources(
                self._loaded_config,
                self._default_working_config.config,
                self._working_config.config,
            ),
        )
        config.path = self._loaded_config.path
        return config

    def _create_menu_bar(self):
        bar = self.menuBar()

        # create file menu items
        file_menu = bar.addMenu("&File")
        file_menu.addAction(self.open_config)
        file_menu.addAction(self.save_config)
        file_menu.addAction(self.save_config_as)

    def initialise_config_tabs(self, config):
        # add in reverse order as they are inserted into the front of the list
        self.initialise_config_tab(config, config.RI_TRANSFORMATION_PATH)
        self.initialise_config_tab(config, config.LOC_TRANSFORMATION_PATH)
        self.initialise_config_tab(config, config.ACC_TRANSFORMATION_PATH)
        self.initialise_config_tab(config, config.TEMPLATE_TRANSFORMATION_PATH)

    def initialise_config_tab(self, config, root_config_path):
        in_config = root_config_path in config

        if in_config and root_config_path not in self.config_tabs:
            self.create_tab(root_config_path)
        elif not in_config and root_config_path in self.config_tabs:
            self.config_tabs[root_config_path].deleteLater()
            del self.config_tabs[root_config_path]

    def create_tab(self, config_path):
        label = {
            self.config.TEMPLATE_TRANSFORMATION_PATH: "Config Template",
            self.config.ACC_TRANSFORMATION_PATH: "Account",
            self.config.LOC_TRANSFORMATION_PATH: "Location",
            self.config.RI_TRANSFORMATION_PATH: "Reinsurance",
        }[config_path]

        tab = ConfigTab(
            self,
            config_path,
            force_all_fields=config_path
            == self.config.TEMPLATE_TRANSFORMATION_PATH,
        )
        self.tabs.insertTab(0, tab, label)
        self.tabs.currentIndex = 0
        self.config_tabs[config_path] = tab

    def on_close_tab(self, idx):
        tab: ConfigTab = self.tabs.widget(idx)

        self._loaded_config.delete(tab.root_config_path)
        self._default_working_config.delete(tab.root_config_path)
        self._working_config.delete(tab.root_config_path)

        self.config_changed.emit(self.config)

        self.tabs.removeTab(idx)
