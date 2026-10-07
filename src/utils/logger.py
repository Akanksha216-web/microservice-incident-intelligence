import logging
import sys


def setup_logger(name: str = "RCAEval", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a structured stream logger for the application.

    Args:
        name (str): Name of the logger instance (usually __name__).
        level (int): Logging severity level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger object instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if logger is initialized multiple times
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    # Define standard production log format: Timestamp | Level | Module | Line | Message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Stream Handler for console / standard output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger