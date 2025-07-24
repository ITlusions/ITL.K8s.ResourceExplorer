import os
import logging
from typing import Optional

class LoggerConfigurator:
    """
    A class to configure logging for the application.
    """

    def __init__(self, level: int = logging.DEBUG, format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"):
        """
        Initializes the LoggerConfigurator with default logging level and format.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
            format (str): Logging format string.
        """
        self.level = level
        self.format = format
        self.logger = logging.getLogger(__name__)

    def configure_logging(self, log_file: Optional[str] = None) -> logging.Logger:
        """
        Configures logging for the application.

        Args:
            log_file (Optional[str]): Path to a log file (if any).

        Returns:
            logging.Logger: Configured logger instance.
        """
        if not self.logger.hasHandlers():  # Prevent duplicate handlers
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.format)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

            self.logger.setLevel(self.level)

        return self.logger

    def log_message(self, level: int, message: str) -> None:
        """
        Logs a message at the specified logging level.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
            message (str): The message to log.
        """
        if not self.logger.hasHandlers():
            self.configure_logging()
        self.logger.log(level, message)