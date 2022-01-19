class BaseFieldMixin:
    def __init__(self, tab, config_path, *args, defer_initial_ui_update=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab = tab
        self.main_window = tab.main_window
        self.config_path = config_path

        # set the initial selections
        if not defer_initial_ui_update:
            self.on_config_changed(self.main_window.config)
        self.main_window.config_changed.connect(self.on_config_changed)

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
