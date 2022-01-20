from PySide6.QtWidgets import QLabel


class Label(QLabel):
    def __init__(self, label, tab, config_path):
        super().__init__(label)

        self.tab = tab
        self.config_path = config_path

        if hasattr(self.tab, "show_all_updated"):
            self.on_show_all_updated(self.tab.show_all_fields)
            self.tab.show_all_updated.connect(self.on_show_all_updated)
        self.tab.main_window.config_changed.connect(self.on_config_changed)

    def on_show_all_updated(self, show_all):
        self.update_visibility(show_all, self.tab.main_window.config)

    def on_config_changed(self, config):
        self.update_visibility(self.tab.show_all_fields, config)

    def update_visibility(self, show_all, config):
        if show_all or not config.uses_template_value(self.config_path):
            self.show()
        else:
            self.hide()
