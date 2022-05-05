from __feature__ import true_property  # noqa
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QPushButton


class AddMenu(QMenu):
    def __init__(self, main_window, button, config):
        super().__init__(button)

        self.main_window = main_window
        self.config = config

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
        self.add_config_entry(
            self.config.TEMPLATE_TRANSFORMATION_PATH,
            {
                "loader": {
                    "path": "converter.connector.csv.CsvConnector",
                    "options": {
                        "write_header": True,
                        "quoting": "nonnumeric",
                    },
                },
                "extractor": {
                    "path": "converter.connector.csv.CsvConnector",
                    "options": {
                        "write_header": True,
                        "quoting": "nonnumeric",
                    },
                },
                "runner": {
                    "path": "converter.runner.pandas.PandasRunner",
                },
            },
        )

    def add_acc_entry(self):
        self.add_config_entry(self.config.ACC_TRANSFORMATION_PATH)

    def add_loc_entry(self):
        self.add_config_entry(self.config.LOC_TRANSFORMATION_PATH)

    def add_ri_entry(self):
        self.add_config_entry(self.config.RI_TRANSFORMATION_PATH)

    def add_config_entry(self, config_path, default_conf=None):
        self.main_window.set_working_value(config_path, default_conf or {})

    def setup_available_actions(self):
        # if not self.config.has_template:
        #     self.addAction(self.add_template_action)

        if not self.config.has_acc:
            self.addAction(self.add_acc_action)

        if not self.config.has_loc:
            self.addAction(self.add_loc_action)

        if not self.config.has_ri:
            self.addAction(self.add_ri_action)


class AddTabButton(QPushButton):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.text = ""

        self.context_menu = None
        self.setup_context_menu(self.main_window.config)
        self.main_window.config_changed.connect(self.setup_context_menu)

        self.setFixedWidth(25)

    def setup_context_menu(self, config):
        if self.context_menu:
            self.context_menu.deleteLater()

        self.context_menu = AddMenu(self.main_window, self, config)
        self.setMenu(self.context_menu)
