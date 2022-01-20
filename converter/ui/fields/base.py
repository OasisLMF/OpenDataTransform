from __feature__ import true_property  # noqa


class BaseFieldMixin:
    def __init__(
        self, tab, config_path, *args, defer_initial_ui_update=False, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.tab = tab
        self.main_window = tab.main_window
        self.config_path = config_path

        # set the initial selections
        if not defer_initial_ui_update:
            self.on_config_changed(self.main_window.config)
        self.main_window.config_changed.connect(self.on_config_changed)

        if hasattr(self.tab, "show_all_updated"):
            self.on_show_all_updated(self.tab.show_all_fields)
            self.tab.show_all_updated.connect(self.on_show_all_updated)
        self.main_window.config_changed.connect(
            self.on_config_changed_update_visibility
        )

    def on_config_changed(self, new_config):
        try:
            self.change_signal.disconnect(self.on_change)
        except RuntimeError:
            pass

        self.update_ui_from_config(new_config)

        self.change_signal.connect(self.on_change)

    def update_ui_from_config(self, config):
        raise NotImplementedError()

    @property
    def change_signal(self):
        raise NotImplementedError()

    def on_change(self, *args, **kwargs):
        raise NotImplementedError()

    def on_show_all_updated(self, show_all):
        self.update_visibility(show_all, self.tab.main_window.config)

    def on_config_changed_update_visibility(self, config):
        self.update_visibility(
            getattr(self.tab, "show_all_fields", True), config
        )

    def update_visibility(self, show_all, config):
        if show_all or not config.uses_template_value(self.config_path):
            self.show()
        else:
            self.hide()
