from __feature__ import true_property  # noqa
from dateutil.utils import today
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QCalendarWidget

from converter.ui.fields.base import BaseFieldMixin


class DateField(BaseFieldMixin, QCalendarWidget):
    def update_ui_from_config(self, config):
        conf_date = config.get(self.config_path, None)
        if conf_date:
            self.setSelectedDate(QDate.fromString(conf_date, Qt.ISODate))
        else:
            # if no date is set the default is today so we need to store this
            # in the default working config so that it will be written
            self.main_window.set_default_working_value(
                self.config_path,
                today().isoformat(),
            )

    def on_change(self):
        self.main_window.set_working_value(
            self.config_path, self.selectedDate.toString(Qt.ISODate)
        )

    @property
    def change_signal(self):
        return self.selectionChanged
