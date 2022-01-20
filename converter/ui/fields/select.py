from __feature__ import true_property  # noqa
from PySide6.QtWidgets import QComboBox

from converter.ui.fields.base import BaseFieldMixin


class Select(BaseFieldMixin, QComboBox):
    def __init__(
        self,
        tab,
        config_path,
        options,
        empty_label=None,
        empty_value=None,
        labels=None,
    ):
        self.empty_label = empty_label

        self.options = options
        self.option_labels = labels or list(map(str, options))

        if empty_label is not None:
            self.options = [empty_value, *options]
            self.option_labels = [empty_label, *self.option_labels]

        super().__init__(tab, config_path, defer_initial_ui_update=True)

        # add options
        self.addItems(self.option_labels)
        self.update_ui_from_config(self.main_window.config)

    def update_ui_from_config(self, config):
        try:
            selected = config.get(self.config_path, None)
            idx = self.options.index(selected)
            self.setCurrentIndex(idx)
        except ValueError:
            pass

    @property
    def change_signal(self):
        return self.currentIndexChanged

    def on_change(self, idx):
        self.main_window.set_working_value(self.config_path, self.options[idx])
