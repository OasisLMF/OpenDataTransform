from typing import Type, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QGroupBox, QComboBox, QCheckBox, QLineEdit
from __feature__ import true_property

from converter.config import Config
from converter.connector import CsvConnector, BaseConnector
from converter.mapping import FileMapping


CONNECTOR_CLASSES: List[Type[BaseConnector]] = list(sorted([
    CsvConnector,
], key=lambda c: c.name))


class ConfigTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        parent.config_changed.connect(self.clear_changes)

        self.layout = QVBoxLayout(self)
        self._working_config = Config()
        self._default_working_config = Config()

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
        return self.parentWidget().config

    @property
    def working_config(self):
        config = self.config
        return Config(
            overrides=config.merge_config_sources(config, self._default_working_config, self._working_config)
        )

    @property
    def has_changes(self):
        return bool(self._working_config)

    def set_working_value(self, path, v):
        self._working_config.set(path, v)
        print(self._working_config.to_yaml())
        print("WORKING CONFIG CHANGED")

    def set_default_working_value(self, path, v):
        self._default_working_config.set(path, v)
        print("DEFAULT WORKING CONFIG CHANGED")
        print(self._default_working_config.to_yaml())

    def clear_changes(self):
        self._working_config = Config()
        self._default_working_config = Config()

    def _create_mapping_form(self):
        config = self.working_config

        mapping = FileMapping(
            self.config,
            raise_errors=False
        )

        formats = list(mapping.mapping_graph.nodes)

        layout = QFormLayout()

        from_combo = QComboBox()
        from_combo.addItems([""] + formats)

        try:
            current_index = formats.index(config.get("mapping.input_format", ""))
            from_combo.setCurrentIndex(current_index)
        except ValueError:
            from_combo.setCurrentIndex(0)

        layout.addRow(QLabel("From:"), from_combo)
        from_combo.currentTextChanged.connect(lambda v: self.set_working_value("mapping.input_format", v))

        to_combo = QComboBox()
        to_combo.addItems([""] + formats)

        try:
            current_index = formats.index(config.get("mapping.output_format", ""))
            to_combo.setCurrentIndex(current_index)
        except ValueError:
            to_combo.setCurrentIndex(0)

        layout.addRow(QLabel("To:"), to_combo)
        to_combo.currentTextChanged.connect(lambda v: self.set_working_value("mapping.output_format", v))

        return layout

    def _create_extractor_config(self):
        return self._create_connector_config("extractor")

    def _create_loader_config(self):
        return self._create_connector_config("loader")

    def _create_connector_config(self, root_config_path):
        config = self.working_config

        layout = QFormLayout()

        # setup the extractor combobox
        class_combo = QComboBox()
        class_combo.addItems(c.name for c in CONNECTOR_CLASSES)

        try:
            current_index = [
                f"{c.fully_qualified_name()}" for c in CONNECTOR_CLASSES
            ].index(config.get(
                f"{root_config_path}.path",
                fallback=f"{CONNECTOR_CLASSES[0].fully_qualified_name()}"
            ))
            selected_connector = CONNECTOR_CLASSES[current_index]
            class_combo.setCurrentIndex(current_index)
        except ValueError:
            selected_connector = CONNECTOR_CLASSES[0]
            class_combo.setCurrentIndex(0)
            self.set_default_working_value(
                f"{root_config_path}.path", f"{CONNECTOR_CLASSES[0].fully_qualified_name()}"
            )

        class_combo.currentIndexChanged.connect(
            lambda v: self.set_working_value(
                f"{root_config_path}.path", f"{CONNECTOR_CLASSES[v].fully_qualified_name()}"
            )
        )
        layout.addRow(QLabel("Class:"), class_combo)

        # create dynamic fields
        for k, v in selected_connector.options_schema.get("properties", {}).items():
            config_path = f"{root_config_path}.options.{k}"
            self._create_dynamic_field(
                layout,
                v.get("title", k),
                v,
                config.get(config_path, None),
                config_path,
            )

        return layout

    def _create_dynamic_field(self, layout, field_name, schema, value, config_path):
        if "enum" in schema:
            layout.addRow(field_name, self._create_enum_field(schema, value, config_path))
        elif schema["type"] == "boolean":
            layout.addRow("", self._create_boolean_field(field_name, schema, value, config_path))
        else:
            layout.addRow(field_name, self._create_text_field(value, config_path))

    def _create_enum_field(self, schema, value, config_path):
        combo = QComboBox()
        combo.addItems(schema["enum"])

        try:
            # TODO: add type coercion here
            selected_index = schema["enum"].index(value)
            combo.setCurrentIndex(selected_index)
        except ValueError:
            combo.setCurrentIndex(0)
            self.set_default_working_value(config_path, schema["enum"][0])

        combo.currentIndexChanged.connect(lambda i: self.set_working_value(config_path, schema["enum"][i]))
        return combo

    def _create_boolean_field(self, field_name, schema, value, config_path):
        if value is None:
            value = schema.get("default", False)
            self.set_default_working_value(config_path, value)

        field = QCheckBox(field_name)
        field.setChecked(value)
        field.stateChanged.connect(lambda v: self.set_working_value(config_path, v))
        return field

    def _create_text_field(self, value, config_path):
        field = QLineEdit()
        field.setText(value or "")
        field.textChanged.connect(lambda v: self.set_working_value(config_path, v))
        return field
