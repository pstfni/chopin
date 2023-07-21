"""Logging related tooling."""

import logging
import os

import coloredlogs


def get_log_level(level: int | str | None = None) -> int:
    """Returns the logging level.

    Log level order:

        - CRITICAL = 50
        - FATAL = 50
        - ERROR = 40
        - WARNING = 30
        - WARN = 30
        - INFO = 20
        - DEBUG = 10
        - NOTSET = 0

    Args:
        level: Can be either a string or an integer according to the exisiting logging level

    Returns:
        int: Log level defined
    """
    level_name_to_integer = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "FATAL": logging.FATAL,
        "NOTSET": logging.NOTSET,
    }
    if isinstance(level, str) and level.upper() in level_name_to_integer:
        return level_name_to_integer[level.upper()]
    elif isinstance(level, int):
        return level
    elif os.environ.get("LOGLEVEL", "").upper() in level_name_to_integer:
        return level_name_to_integer[os.environ["LOGLEVEL"].upper()]
    else:
        return logging.INFO


def get_logger(name: str, root_stdout_level=None, module_stdout_level=None) -> logging.Logger:
    """Setup the logger and returns the requested `name` logger.

    Args:
        name: logger name, to identify it in the stdout (for example, `__name__`)
        root_stdout_level: Configure the level of the root logger. The root logger is the logger that you
            obtain when you do logging.getLogger()
        module_stdout_level: Level of your module.


    Returns:
        the logging.Logger correctly set-up


    Raises:
        ValueError:  If name is None raise an error.
    """
    if name is None:
        raise ValueError("You should provide a default name to your logger")

    root_stdout_level = get_log_level(root_stdout_level)
    module_stdout_level = get_log_level(module_stdout_level)

    # The root configuration is broadcast to all the module level
    fmt = "%(asctime)s %(name)s %(levelname)s %(message)s (%(filename)s:%(lineno)s)"
    coloredlogs.install(level=root_stdout_level, fmt=fmt)

    # Prepare the named logger as requested
    logger = logging.getLogger(name)
    logger.setLevel(module_stdout_level)

    return logger
