from typing import Type, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QGroupBox, QComboBox, QCheckBox, QLineEdit
from __feature__ import true_property

from converter.connector import CsvConnector, BaseConnector
from converter.mapping import FileMapping


CONNECTOR_CLASSES: List[Type[BaseConnector]] = list(sorted([
    CsvConnector,
], key=lambda c: c.name))


class ConfigTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout(self)

        # setup mapping config
        mapping_group_box = QGroupBox("Mapping")
        mapping_group_box.setLayout(self._create_mapping_form())
        self.layout.addWidget(mapping_group_box)

        # setup extractor config
        extractor_group_box = QGroupBox("Extractor")
        extractor_group_box.setLayout(self._create_extractor_config())
        self.layout.addWidget(extractor_group_box)

        # setup loader config
        loader_group_box = QGroupBox("Loader")
        loader_group_box.setLayout(self._create_loader_config())
        self.layout.addWidget(loader_group_box)

    @property
    def config(self):
        return self.parentWidget().config.get()

    def _create_mapping_form(self):
        mapping = FileMapping(
            self.config,
            raise_errors=False
        )

        formats = list(mapping.mapping_graph.nodes)

        layout = QFormLayout()

        from_combo = QComboBox()
        from_combo.addItems(formats)
        layout.addRow(QLabel("From:"), from_combo)

        to_combo = QComboBox()
        to_combo.addItems(formats)
        layout.addRow(QLabel("To:"), to_combo)

        return layout

    def _create_extractor_config(self):
        config = self.config

        layout = QFormLayout()

        # setup the extractor combobox
        class_combo = QComboBox()
        class_combo.addItems(c.name for c in CONNECTOR_CLASSES)

        try:
            current_index = [
                f"{c.__module__}.{c.__qualname__}" for c in CONNECTOR_CLASSES
            ].index(config.get(
                "extractor.path",
                fallback=f"{CONNECTOR_CLASSES[0].__module__}.{CONNECTOR_CLASSES[0].__qualname__}"
            ))
            selected_connector = CONNECTOR_CLASSES[current_index]
            class_combo.setCurrentIndex(current_index)
        except ValueError:
            selected_connector = CONNECTOR_CLASSES[0]
            class_combo.setCurrentIndex(0)

        layout.addRow(QLabel("Class:"), class_combo)

        # create dynamic fields
        for k, v in selected_connector.options_schema.get("properties", {}).items():
            self._create_dynamic_field(
                layout,
                v.get("title", k),
                v,
                config.get(f"extractor.options.{k}", None)
            )

        return layout

    def _create_dynamic_field(self, layout, field_name, schema, value):
        if "enum" in schema:
            layout.addRow(field_name, self._create_enum_field(schema, value))
        elif schema["type"] == "boolean":
            layout.addRow("", self._create_boolean_field(field_name, schema, value))
            # pass
        else:
            layout.addRow(field_name, self._create_text_field(value))

    def _create_enum_field(self, schema, value):
        combo = QComboBox()
        combo.addItems(schema["enum"])

        try:
            # TODO: add type coercion here
            selected_index = schema["enum"].index(value)
            combo.setCurrentIndex(selected_index)
        except ValueError:
            combo.setCurrentIndex(0)

        return combo

    def _create_boolean_field(self, field_name, schema, value):
        if value is None:
            value = schema.get("default", False)

        field = QCheckBox(field_name)
        field.setChecked(value)
        return field

    def _create_text_field(self, value):
        field = QLineEdit()
        field.setText(value or "")
        return field

    def _create_loader_config(self):
        layout = QFormLayout()

        return layout
