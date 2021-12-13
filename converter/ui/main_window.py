import random

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QTabWidget, QMainWindow
from __feature__ import true_property

from converter.ui.config_tab.main import ConfigTab
from converter.ui.run_tab.main import RunTab


class MainWindow(QMainWindow):
    def __init__(self, config):
        self.config = config

        super().__init__()

        # setup the top menu
        self._create_actions()
        self._create_menu_bar()

        tabs = QTabWidget()
        tabs.addTab(ConfigTab(), "Config")
        tabs.addTab(RunTab(), "Run")
        self.setCentralWidget(tabs)

    def _create_actions(self):
        # create config actions
        self.open_config = QAction("&Open")
        self.save_config = QAction("&Save")

    def _create_menu_bar(self):
        bar = self.menuBar()

        # create file menu items
        file_menu = bar.addMenu("&File")
        file_menu.addAction(self.open_config)
        file_menu.addAction(self.save_config)
