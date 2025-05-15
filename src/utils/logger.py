import logging

import json_log_formatter


class Logger:
    """
    Logger class to configure and retrieve a JSON-formatted logger.
    """

    _logger = None

    def __init__(self):
        """
        Initializes the Logger class and sets up the logging configuration.
        """
        if self._logger is None:
            self.setup_logging()

    @classmethod
    def setup_logging(cls):
        """
        Configures a logger that outputs logs in JSON format to the console.
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
        Returns the configured logger instance.
        """
        return cls._logger
