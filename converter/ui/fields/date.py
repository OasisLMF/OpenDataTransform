from __feature__ import true_property  # noqa
from dateutil.utils import today
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QCalendarWidget


class DateField(QCalendarWidget):
    def __init__(self, tab, config_path):
        super().__init__()

        self.tab = tab
        self.main_window = tab.main_window
        self.config_path = config_path

        self.on_config_loaded(tab.main_window.config)
        self.main_window.config_changed.connect(self.on_config_loaded)

    def on_config_loaded(self, new_config):
        try:
            self.selectionChanged.disconnect(self.on_changed)
        except RuntimeError:
            pass

        conf_date = new_config.get(self.config_path, None)
        if conf_date:
            self.setSelectedDate(QDate.fromString(conf_date, Qt.ISODate))
        else:
            # if no date is set the default is today so we need to store this
            # in the default working config so that it will be written
            self.main_window.set_default_working_value(
                self.config_path,
                today().isoformat(),
            )

        self.selectionChanged.connect(self.on_changed)

    def on_changed(self):
        self.main_window.set_working_value(
            self.config_path, self.selectedDate.toString(Qt.ISODate)
        )
