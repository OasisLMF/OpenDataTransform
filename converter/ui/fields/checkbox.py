from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QCheckBox

from converter.ui.fields.base import BaseFieldMixin


class Checkbox(BaseFieldMixin, QCheckBox):
    def __init__(self, tab, config_path, label, default):
        self.default = default

        super().__init__(tab, config_path, label)

    def update_ui_from_config(self, config):
        new_value = config.get_template_resolved_value(
            self.config_path, self.default
        )
        if new_value != self.checkState:
            self.setChecked(new_value)

    def on_change(self, v):
        self.main_window.set_working_value(self.config_path, bool(v))

    @property
    def change_signal(self):
        return self.stateChanged
