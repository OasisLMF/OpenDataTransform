import yaml
from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QLabel

from converter.data import get_data_path
from converter.ui.fields.date import DateField
from converter.ui.fields.multiselect import MultiSelect
from converter.ui.fields.string import StringField, TextAreaField


class MetadataTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.main_window = parent

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel(
            "The metadata is used To provide extra context about a performed transformation. "
            "All fields are optional."
        ))
        with open(get_data_path("forms", "metadata.yaml")) as f:
            entries = yaml.load(f, yaml.Loader)

            for prop, spec in entries.items():
                self.create_field(f"metadata.{prop}", spec)

        self.main_window.running_changed.connect(
            lambda b: self.setEnabled(not b)
        )

    def create_field(self, conf_path, spec):
        if spec.get("sub_type", None) == "multiselect":
            self.create_multiselect(conf_path, spec)
        elif spec["type"] == "date":
            self.create_calendar(conf_path, spec)
        elif spec["type"] == "string":
            self.create_string_field(conf_path, spec)

    def create_multiselect(self, conf_path, spec):
        group = QGroupBox(spec["title"])
        layout = QVBoxLayout()
        widget = MultiSelect(self, conf_path, spec["enum"])

        layout.addWidget(widget)
        group.setLayout(layout)

        self.layout.addWidget(group)

    def create_calendar(self, conf_path, spec):
        group = QGroupBox(spec["title"])
        layout = QVBoxLayout()
        widget = DateField(self, conf_path)

        layout.addWidget(widget)
        group.setLayout(layout)

        self.layout.addWidget(group)

    def create_string_field(self, conf_path, spec):
        group = QGroupBox(spec["title"])
        layout = QVBoxLayout()
        widget = (
            TextAreaField(self, conf_path)
            if spec.get("sub_type") == "text_area"
            else StringField(self, conf_path)
        )

        layout.addWidget(widget)
        group.setLayout(layout)

        self.layout.addWidget(group)
