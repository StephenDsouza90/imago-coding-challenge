import logging

import json_log_formatter


class Logger:
    """
    Logger configures and provides a singleton JSON-formatted logger for the application.
    This logger outputs logs in JSON format, suitable for structured logging and integration with log management systems.
    """

    _logger = None

    def __init__(self):
        """
        Initialize the Logger and set up JSON logging if not already configured.
        """
        if self._logger is None:
            self.setup_logging()

    @classmethod
    def setup_logging(cls):
        """
        Set up a JSON log formatter and attach it to the logger instance.
        """
        if cls._logger is None:
            json_handler = logging.StreamHandler()
            json_handler.setFormatter(json_log_formatter.JSONFormatter())

            cls._logger = logging.getLogger("app_logger")
            cls._logger.addHandler(json_handler)
            cls._logger.setLevel(logging.INFO)
            cls._logger.propagate = False

    @classmethod
    def get_logger(cls):
        """
        Retrieve the singleton logger instance for use throughout the application.
        """
        return cls._logger
