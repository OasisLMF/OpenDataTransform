import os

from __feature__ import true_property  # noqa
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QTabWidget,
    QTabBar,
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

        # setup tabs
        self.tabs = QTabWidget()
        self.tabs.tabsClosable = True
        self.tabs.tabCloseRequested.connect(self.on_close_tab)

        self.run_tab = RunTab(self)
        run_scroll_wrapper = QScrollArea()
        run_scroll_wrapper.setWidget(self.run_tab)
        self.tabs.addTab(run_scroll_wrapper, "Run")
        self.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)

        self.metadata_tab = MetadataTab(self)
        meta_scroll_wrapper = QScrollArea()
        meta_scroll_wrapper.setWidget(self.metadata_tab)
        self.tabs.addTab(meta_scroll_wrapper, "Metadata")
        self.tabs.tabBar().setTabButton(1, QTabBar.RightSide, None)

        # add create tab button
        self.tab_button = AddTabButton(self)
        self.tabs.setCornerWidget(self.tab_button)

        self.config_tabs = []
        self.initialise_config_tabs(self.config)
        self.tab_button.tab_added.connect(self.create_tab)

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
            overrides=self._loaded_config.overrides,
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

    def initialise_config_tabs(self, config):
        for tab in self.config_tabs:
            tab.deleteLater()

        if config.has_template:
            self.create_tab(self.config.TEMPLATE_TRANSFORMATION_PATH)

        if config.has_acc:
            self.create_tab(self.config.ACC_TRANSFORMATION_PATH)

        if config.has_loc:
            self.create_tab(self.config.LOC_TRANSFORMATION_PATH)

        if config.has_ri:
            self.create_tab(self.config.RI_TRANSFORMATION_PATH)

    def create_tab(self, config_path):
        label = {
            self.config.TEMPLATE_TRANSFORMATION_PATH: "Template",
            self.config.ACC_TRANSFORMATION_PATH: "Account",
            self.config.LOC_TRANSFORMATION_PATH: "Location",
            self.config.RI_TRANSFORMATION_PATH: "Reinsurance",
        }[config_path]

        tab = ConfigTab(self, config_path, force_all_fields=config_path == self.config.TEMPLATE_TRANSFORMATION_PATH)
        scroll_wrapper = QScrollArea()
        scroll_wrapper.setWidget(tab)
        self.tabs.addTab(scroll_wrapper, label)
        self.config_tabs.append(scroll_wrapper)

    def on_close_tab(self, idx):
        scroll_scroll: QScrollArea = self.tabs.widget(idx)
        tab: ConfigTab = scroll_scroll.widget()
        tab.deleteLater()

        self._loaded_config.delete(tab.root_config_path)
        self._default_working_config.delete(tab.root_config_path)
        self._working_config.delete(tab.root_config_path)
        self.config_changed.emit(self.config)

        self.tabs.removeTab(idx)
