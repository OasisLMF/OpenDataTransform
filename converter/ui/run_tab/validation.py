import logging

import yaml
from __feature__ import true_property  # noqa
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem, QVBoxLayout, QLabel,
)

from converter.validator.base import ValidationResult, ValidationLogEntry


class ValidationPanel(logging.Handler):
    table_headers = ["Validator", "Group", "Field", "Value", "Operator"]

    def __init__(self, main_window):
        super().__init__()

        self.layout = QVBoxLayout()

        # setup tables
        self.tables = {}
        self.setup_tables(main_window.config)
        main_window.config_changed.connect(self.setup_tables)

    def setup_tables(self, config):
        for table in self.tables.values():
            if table is not None:
                self.layout.removeWidget(table)
                table.deleteLater()

        if config.has_acc:
            self.tables["acc"] = ValidationTable("Account")
        else:
            self.tables["acc"] = None

        if config.has_loc:
            self.tables["loc"] = ValidationTable("Location")
        else:
            self.tables["loc"] = None

        if config.has_ri:
            self.tables["ri"] = ValidationTable("Reinsurance")
        else:
            self.tables["ri"] = None

        for table in self.tables.values():
            if table is not None:
                self.layout.addWidget(table)

    def emit(self, record):
        parsed = yaml.safe_load(record.msg)
        if not isinstance(parsed[0], dict):
            return

        log_entry: ValidationLogEntry = parsed[0]
        validations: ValidationResult = parsed[0][
            "validations"
        ]

        rows = []
        row = ["", "", "", "", ""]
        for validation in validations:
            row[0] = validation["name"]

            for entry in validation["entries"]:
                groups = entry.get("groups", None) or {}
                row[1] = ", ".join(
                    map(lambda g: f"{g[0]}={g[1]}", groups.items())
                )
                row[2] = entry.get("field") or ""
                row[3] = entry.get("error") or entry.get("value") or ""
                row[4] = str(validation.get("operator"))

                rows.append(row)
                row = ["", "", "", "", ""]

        self.tables[log_entry["file_type"]].redraw_table(rows)

    def clear(self):
        for table in self.tables.values():
            if table is not None:
                table.clear()


class ValidationTable(QGroupBox):
    table_headers = ["Validator", "Group", "Field", "Value", "Operator"]

    def __init__(self, file_type):
        super().__init__(file_type)

        # switch to track if we are expecting the input validation output
        self.input = True
        self.file_type = file_type

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.input_table = self.create_table("Input Validation")
        self.output_table = self.create_table("Output Validation")

    def create_table(self, group_name):
        table = QTableWidget(0, len(self.table_headers))
        table.setHorizontalHeaderLabels(self.table_headers)
        table.resizeColumnsToContents()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(group_name))
        layout.addWidget(table)

        self.layout.addLayout(layout)

        return table

    def redraw_table(self, data):
        table = self.input_table if self.input else self.output_table
        self.input = not self.input

        # clear the table and resize
        table.clearContents()
        table.rowCount = len(data)  # type: ignore
        table.columnCount = len(self.table_headers)  # type: ignore

        # set the values of each entry
        for row_id, row in enumerate(data):
            for col_id, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                table.setItem(row_id, col_id, item)

        # resize the table to fit the content
        table.resizeColumnsToContents()

    def clear(self):
        self.input = True
        self.redraw_table([])
        self.redraw_table([])
