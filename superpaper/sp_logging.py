"""Logging tools for Superpaper."""

import logging

import sp_paths

DEBUG = False
VERBOSE = False
LOGGING = False
G_LOGGER = logging.getLogger("default")

if DEBUG and not LOGGING:
    G_LOGGER.setLevel(logging.INFO)
    CONSOLE_HANDLER = logging.StreamHandler()
    G_LOGGER.addHandler(CONSOLE_HANDLER)
elif LOGGING:
    DEBUG = True
    G_LOGGER.setLevel(logging.INFO)
    FILE_HANDLER = logging.FileHandler("{0}/{1}.log".format(sp_paths.PATH, "log"),
                                       mode="w")
    G_LOGGER.addHandler(FILE_HANDLER)
    CONSOLE_HANDLER = logging.StreamHandler()
    G_LOGGER.addHandler(CONSOLE_HANDLER)

def custom_exception_handler(exceptiontype, value, tb_var):
    """Log uncaught exceptions."""
    G_LOGGER.exception("Uncaught exception type: %s", str(exceptiontype))
    G_LOGGER.exception("Exception: %s", str(value))
    G_LOGGER.exception(str(tb_var))
