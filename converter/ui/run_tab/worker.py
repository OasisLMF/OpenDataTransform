import logging

from PySide6.QtCore import QThread, QObject, Signal
from __feature__ import true_property  # noqa

from converter.controller import Controller


class LogHandler(logging.Handler):
    """
    Log handler to send log records back to the main window
    thread through signals

    :param signal: The signal the logger should be hooked up to
    """
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record: logging.LogRecord) -> None:
        """
        Sends the record through the signal
        """
        self.signal.emit(record)


class ControllerRunner(QObject):
    """
    QObject wrapper that runs the transformation so that it can be
    sent to the worker thread

    :param config: The config of the transformation to perform
    """
    finished = Signal()
    """Signal that is emitted when the transformation ends"""

    generic_log_record = Signal(object)
    """Signal that passes the all log records"""

    validation_log_record = Signal(object)
    """Signal that passes the validation log records"""

    def __init__(self, config):
        super().__init__()
        self.config = config

        self.validation_log_handler = LogHandler(self.validation_log_record)
        """The handler to emit all records"""

        self.generic_log_handler = LogHandler(self.generic_log_record)
        """The handler to emit the validation records"""

    def create_validation_log_handler(self):
        """
        Sets up the handler to catch the validation log records
        """
        logger = logging.getLogger("converter.validator")
        logger.addHandler(self.validation_log_handler)
        logger.setLevel(logging.DEBUG)

    def remove_validation_log_handler(self):
        """
        Removes the validation log handler
        """
        logger = logging.getLogger("converter.validator")
        logger.removeHandler(self.validation_log_handler)

    def create_generic_log_handler(self):
        """
        Sets up the handler to catch the generic log records
        """
        logger = logging.getLogger()
        logger.addHandler(self.generic_log_handler)
        logger.setLevel(logging.DEBUG)

    def remove_generic_log_handler(self):
        """
        Removes the generic log handler
        """
        logger = logging.getLogger()
        logger.removeHandler(self.generic_log_handler)

    def run(self):
        """
        Runs the transformation
        """
        try:
            self.create_generic_log_handler()
            self.create_validation_log_handler()
            Controller(self.config).run()
        finally:
            self.remove_generic_log_handler()
            self.remove_validation_log_handler()
            self.finished.emit()


class RunThread:
    """
    Wraps the thread and worker setting up the log signals to pass
    the log messages to the main window thread

    :param on_start: Method to call before the transformation begins
    :param on_finish: Method to call after the transformation ends
    """
    def __init__(self, on_start, on_finish):
        self.on_start = on_start
        self.on_finish = on_finish

        self.worker = None
        """The controller runner"""

        self.thread = None
        """The thread the worker will be ran on"""

    def start(self, config, generic_log_handler, validation_log_handler):
        """
        Starts the thread connecting the log panels to the relevant signals

        :param config: Config for the transformation to run
        :param generic_log_handler: The handler to consume all log records
        :param validation_log_handler: The handler to consume validation log
            records
        """
        self.on_start()

        self.thread = QThread()
        self.worker = ControllerRunner(config)
        self.worker.moveToThread(self.thread)

        self.worker.finished.connect(self.on_finish)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)

        # connect the log handlers back to the main window
        self.worker.generic_log_record.connect(generic_log_handler.emit)
        self.worker.validation_log_record.connect(validation_log_handler.emit)

        self.thread.start()
