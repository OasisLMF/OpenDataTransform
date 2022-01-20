from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QFormLayout, QGroupBox

from converter.ui.fields.checkbox import Checkbox
from converter.ui.fields.file import FileField
from converter.ui.fields.label import Label
from converter.ui.fields.select import Select
from converter.ui.fields.string import StringField


class DynamicClassFormBlock(QGroupBox):
    def __init__(
        self, tab, label, root_config_path, classes, default_class=None
    ):
        super().__init__(label)
        self.tab = tab
        self.main_window = tab.main_window
        self.classes = classes
        self.default_class = default_class or classes[0]
        self.root_config_path = root_config_path
        self.layout = QFormLayout()
        self.dynamic_fields = []

        self.class_selector = Select(
            tab,
            f"{self.root_config_path}.path",
            [self.get_fully_qualified_classname(cls) for cls in self.classes],
            labels=[
                self.get_selectable_class_name(cls) for cls in self.classes
            ],
            empty_label="",
        )
        self.class_selector.currentIndexChanged.connect(
            self.on_selection_changed
        )
        self.layout.addRow(
            Label("Class:", tab, f"{self.root_config_path}.path"),
            self.class_selector,
        )

        # populate initial dynamic fields
        current_cls_name = self.main_window.config.get(
            f"{self.root_config_path}.path", None
        )
        current_selection = next(
            (
                cls
                for cls in self.classes
                if self.get_fully_qualified_classname(cls) == current_cls_name
            ),
            None,
        )
        self.dynamic_fields = self.update_dynamic_fields_from_selection(
            current_selection
        )

        self.setLayout(self.layout)

    @classmethod
    def get_selectable_class_name(cls, option):
        return getattr(option, "name", str(option))

    @classmethod
    def get_fully_qualified_classname(cls, option):
        return f"{option.__module__}.{option.__qualname__}"

    def on_selection_changed(self, value):
        if value == 0:
            selected_class = None
        else:
            selected_class = self.classes[value - 1]
        self.dynamic_fields = self.update_dynamic_fields_from_selection(
            selected_class
        )

    def update_dynamic_fields_from_selection(self, selection):
        for field in self.dynamic_fields:
            self.layout.removeRow(field)

        if selection is None:
            return []

        return [
            self._create_dynamic_field(field_name, schema)
            for field_name, schema in selection.options_schema.get(
                "properties", {}
            ).items()
        ]

    def _create_dynamic_field(self, field_name, schema):
        config_path = f"{self.root_config_path}.options.{field_name}"
        label = schema.get("title", field_name)

        if "enum" in schema:
            field = Select(
                self.tab, config_path, schema["enum"], empty_label=""
            )
        elif schema["type"] == "boolean":
            field = Checkbox(
                self.tab, config_path, "", schema.get("default", False)
            )
        elif schema["type"] == "string" and schema["subtype"] == "path":
            field = FileField(self.tab, config_path)
        else:
            field = StringField(self.tab, config_path)

        self.layout.addRow(Label(label, self.tab, config_path), field)
        return field
