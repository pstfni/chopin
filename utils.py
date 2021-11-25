import logging
import os
from typing import Union

import coloredlogs
import emoji


def get_log_level(level: Union[int, str] = None) -> int:
    """Return the logging level in the following order.
    Log level can bet the following you can use them either as a string or as integer:
    - CRITICAL = 50
    - FATAL = 50
    - ERROR = 40
    - WARNING = 30
    - WARN = 30
    - INFO = 20
    - DEBUG = 10
    - NOTSET = 0
    1. Base on input . Finally returns INFO level by
    2. Check if the LOGLEVEL env variable exists
    3. Return logging.INFO = 20 by default
    Args:
        level (int, str, optional): Can be either a string or an
            integer according to the exisiting logging `level https://docs.python.org/3/library/logging.html`_.
    Return:
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
    Setup root logger as a colored logger on stdout.
    This root logger is supposed to gather all logging propagated by specific
    loggers and show them in the console.
    Args:
        name: The name is typically a dot-separated hierarchical name like “a”, “a.b” or “a.b.c.d”.
            Choice of these names is entirely up to the developer who is using logging. You should know that
            "a.b" means that "b" will inherit from the configuration of "a". Please prefer to call `get_logger`
            as follow: ::
                 get_logger(__name__) # For this file name would be skynet.utils
        root_stdout_level: Configure the level of the root logger. The root logger is the logger that you
            obtain when you do logging.getLogger()
        module_stdout_level: Level of your module.
    Return:
        logging.Logger: A logger with the specified name, creating it if necessary.
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


def simplify_string(text: str) -> str:
    """Simplify a string: lowercase, and no emojis"""
    text = emoji.get_emoji_regexp().sub(u"", text)
    text = text.lower()
    text = text.rstrip(" ")
    text = text.replace("'", "")
    return text
