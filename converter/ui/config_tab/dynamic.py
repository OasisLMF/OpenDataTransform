from PySide6.QtWidgets import QGroupBox, QFormLayout, QComboBox, QLabel, QCheckBox, QLineEdit
from __feature__ import true_property

from converter.ui.config_tab.file import FileField


class DynamicClassFormBlock(QGroupBox):
    def __init__(self, tab, label, root_config_path, classes, default_class=None):
        super().__init__(label)
        self.tab = tab
        self.classes = classes
        self.default_class = default_class or classes[0]
        self.root_config_path = root_config_path
        self.layout = QFormLayout()
        self.dynamic_fields = []

        self.class_selector = QComboBox()
        self.class_selector.addItems([
            self.get_selectable_class_name(cls) for cls in self.classes
        ])
        self.layout.addRow(QLabel("Class:"), self.class_selector)

        self.class_selector.currentIndexChanged.connect(self.on_selection_changed)
        self.on_config_loaded(self.tab.working_config)

        self.tab.main_window.config_changed.connect(self.on_config_loaded)

        self.setLayout(self.layout)

    @classmethod
    def get_selectable_class_name(cls, option):
        return getattr(option, "name", str(option))

    @classmethod
    def get_fully_qualified_classname(cls, option):
        return f"{option.__module__}.{option.__qualname__}"

    def on_selection_changed(self, value):
        selected_class = self.classes[value]
        self.tab.set_working_value(
            f"{self.root_config_path}.path", self.get_fully_qualified_classname(selected_class)
        )
        self.dynamic_fields = self.update_dynamic_fields_from_selection(selected_class, self.tab.working_config)

    def on_config_loaded(self, new_config):
        selection = self.update_selection_from_config(new_config)
        self.dynamic_fields = self.update_dynamic_fields_from_selection(selection, new_config)

    def update_selection_from_config(self, config):
        class_paths = [self.get_fully_qualified_classname(c) for c in self.classes]
        selected_in_config = config.get(f"{self.root_config_path}.path", fallback=None)

        try:
            current_index = class_paths.index(selected_in_config)
        except ValueError:
            current_index = None

        try:
            default_index = class_paths.index(self.get_fully_qualified_classname(self.default_class))
        except ValueError:
            default_index = None

        if current_index is not None:
            self.class_selector.setCurrentIndex(current_index)
            return self.classes[current_index]
        elif default_index is not None:
            self.class_selector.setCurrentIndex(default_index)
            self.tab.set_default_working_value(
                f"{self.root_config_path}.path", self.get_fully_qualified_classname(self.default_class)
            )
            return self.default_class
        else:
            self.class_selector.setCurrentIndex(0)
            self.tab.set_default_working_value(
                f"{self.root_config_path}.path", self.get_fully_qualified_classname(self.classes[0])
            )
            return self.classes[0]

    def update_dynamic_fields_from_selection(self, selection, config):
        for field in self.dynamic_fields:
            self.layout.removeRow(field)

        return [
            self._create_dynamic_field(field_name, schema, config)
            for field_name, schema in selection.options_schema.get("properties", {}).items()
        ]

    def _create_dynamic_field(self, field_name, schema, config):
        config_path = f"{self.root_config_path}.options.{field_name}"
        value = config.get(config_path, None)
        label = schema.get("title", field_name)

        if "enum" in schema:
            field = self._create_enum_field(schema, value, config_path)
        elif schema["type"] == "boolean":
            field = self._create_boolean_field(schema, value, config_path)
        elif schema["type"] == "string" and schema["subtype"] == "path":
            field = self._create_file_field(schema, value, config_path)
        else:
            field = self._create_text_field(schema, value, config_path)

        self.layout.addRow(label, field)
        return field

    def _create_enum_field(self, schema, value, config_path):
        if value is None:
            value = schema.get("default", schema["enum"][0])
            self.tab.set_default_working_value(config_path, value)

        combo = QComboBox()
        combo.addItems(schema["enum"])

        try:
            # TODO: add type coercion here
            selected_index = schema["enum"].index(value)
            combo.setCurrentIndex(selected_index)
        except ValueError:
            combo.setCurrentIndex(0)
            self.tab.set_default_working_value(config_path, schema["enum"][0])

        combo.currentIndexChanged.connect(lambda i: self.tab.set_working_value(config_path, schema["enum"][i]))
        return combo

    def _create_boolean_field(self, schema, value, config_path):
        if value is None:
            value = schema.get("default", False)
            self.tab.set_default_working_value(config_path, value)

        field = QCheckBox("")
        field.setChecked(value)
        field.stateChanged.connect(lambda v: self.tab.set_working_value(config_path, bool(v)))
        return field

    def _create_file_field(self, schema, value, config_path):
        if value is None:
            value = schema.get("default", "")
            self.tab.set_default_working_value(config_path, value)

        field = FileField(self.tab)
        field.setValue(value or "")
        field.value_changed.connect(lambda v: self.tab.set_working_value(config_path, v))
        return field

    def _create_text_field(self, schema, value, config_path):
        if value is None:
            value = schema.get("default", "")
            self.tab.set_default_working_value(config_path, value)

        field = QLineEdit()
        field.setText(value or "")
        field.textChanged.connect(lambda v: self.tab.set_working_value(config_path, v))
        return field
