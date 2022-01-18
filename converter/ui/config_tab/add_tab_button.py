from PySide6.QtCore import Signal
from __feature__ import true_property  # noqa
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QPushButton


class AddMenu(QMenu):
    def __init__(self, main_window, button):
        super().__init__(button)

        self.main_window = main_window

        self.add_template_action = QAction("Add template...")
        self.add_template_action.triggered.connect(self.add_template_entry)

        self.add_acc_action = QAction("Add Account Transformation...")
        self.add_acc_action.triggered.connect(self.add_acc_entry)

        self.add_loc_action = QAction("Add Location Transformation...")
        self.add_loc_action.triggered.connect(self.add_loc_entry)

        self.add_ri_action = QAction("Add Reinsurance Transformation...")
        self.add_ri_action.triggered.connect(self.add_ri_entry)

        self.setup_available_actions()

    def add_template_entry(self):
        self.add_config_entry(self.main_window.config.TEMPLATE_TRANSFORMATION_PATH)

    def add_acc_entry(self):
        self.add_config_entry(self.main_window.config.ACC_TRANSFORMATION_PATH)

    def add_loc_entry(self):
        self.add_config_entry(self.main_window.config.LOC_TRANSFORMATION_PATH)

    def add_ri_entry(self):
        self.add_config_entry(self.main_window.config.RI_TRANSFORMATION_PATH)

    def add_config_entry(self, config_path):
        self.main_window.set_working_value(config_path, {})

    def setup_available_actions(self):
        if not self.main_window.config.has_template:
            self.addAction(self.add_template_action)

        if not self.main_window.config.has_acc:
            self.addAction(self.add_acc_action)

        if not self.main_window.config.has_loc:
            self.addAction(self.add_loc_action)

        if not self.main_window.config.has_ri:
            self.addAction(self.add_ri_action)


class AddTabButton(QPushButton):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.text = ""

        self.context_menu = None
        self.setup_context_menu()
        self.main_window.config_changed.connect(self.setup_context_menu)

        self.setFixedWidth(25)

    def setup_context_menu(self, *args):
        if self.context_menu:
            self.context_menu.deleteLater()

        self.context_menu = AddMenu(self.main_window, self)
        self.setMenu(self.context_menu)
