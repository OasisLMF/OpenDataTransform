import logging

import yaml
from __feature__ import true_property  # noqa
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem

from converter.validator.base import ValidationResult


class ValidationPanel(logging.Handler):
    table_headers = ["Validator", "Group", "Field", "Value", "Operator"]

    def __init__(self, parent):
        super().__init__()

        # switch to track if we are expecting the input validation output
        self.input = True

        self.layout = QHBoxLayout()

        self.input_table = self.create_table("Input Validation")
        self.output_table = self.create_table("Output Validation")

    def emit(self, record):
        validations: ValidationResult = yaml.safe_load(record.msg)[0]["validations"]
        table = self.input_table if self.input else self.output_table
        self.input = not self.input

        rows = []
        row = ["", "", "", "", ""]
        for validation in validations:
            row[0] = validation["name"]

            for entry in validation["entries"]:
                groups = validation.get("groups", None) or {}
                row[1] = ", ".join(map(lambda g: f"{g[0]}={g[1]}", groups.items()))
                row[2] = entry.get("field") or ""
                row[3] = entry.get("error") or entry.get("value") or ""
                row[4] = str(validation.get("operator"))

                rows.append(row)
                row = ["", "", "", "", ""]

        self.redraw_table(table, rows)

    def create_table(self, group_name):
        table = QTableWidget(0, len(self.table_headers))
        table.setHorizontalHeaderLabels(self.table_headers)
        table.resizeColumnsToContents()

        layout = QHBoxLayout()
        layout.addWidget(table)

        group_box = QGroupBox(group_name)
        group_box.setLayout(layout)

        self.layout.addWidget(group_box)

        return table

    def redraw_table(self, table: QTableWidget, data):
        # clear the table and resize
        table.clearContents()
        table.rowCount = len(data)
        table.columnCount = len(self.table_headers)

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
        self.redraw_table(self.input_table, [])
        self.redraw_table(self.output_table, [])
