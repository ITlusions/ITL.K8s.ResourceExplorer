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

    def configure_logging(self):
        """
        Configures logging for the application.

        Returns:
            logging.Logger: Configured logger instance.
        """
        # Configure logging globally
        logging.basicConfig(
            level=self.level,
            format=self.format,
            handlers=[
                logging.StreamHandler()
            ],
        )

        # Create and return a logger for the application
        logger = logging.getLogger(__name__)
        logger.setLevel(self.level)
        return logger
