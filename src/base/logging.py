import os
import logging

class LoggerConfigurator:
    """
    A class to configure logging for the application.
    """

    def __init__(self, level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"):
        """
        Initializes the LoggerConfigurator with default logging level and format.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
            format (str): Logging format string.
        """
        self.level = level
        self.format = format
        self.logger = logging.getLogger("ResourceExplorer")

    def configure_logging(self):
        """
        Configures logging for the application.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if not self.logger.hasHandlers():  # Prevent duplicate handlers
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)  # Set desired logging level

        # Create and return a logger for the application
        logger = logging.getLogger(__name__)
        logger.setLevel(self.level)
        return logger

    def log_message(self, level, message):
        """
        Logs a message at the specified logging level.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
            message (str): The message to log.
        """
        if not self.logger:
            self.configure_logging()
        self.logger.log(level, message)