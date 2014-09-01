#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
module: zachlog
author: Zach Lamberty and Patrick Wong
created: 2014-08-31

Description:
    Stripped down version of peak6 logging. Defaults in a yaml file.

Usage:
    import zachlog as logging
    logger = logging.getLogger(__name__)
    logging.Config(__name__).configure()
    logger.info("Info statement")

"""

from __future__ import absolute_import  # Prevent namespace conflicts w/ std
import logging as _std_logging
import logging.config as _logconfig
import os as _os
import yaml as _yaml

_YAML_FILE = _os.path.dirname(_os.path.realpath(__file__)) + "/default.yaml"
_VALID_LEVELS = ("DEBUG", "INFO", "WARN", "ERROR", "CRITICAL")
_SPECIAL_LOGGERS = ('__main__', 'print')

CRITICAL = _std_logging.CRITICAL
DEBUG = _std_logging.DEBUG
ERROR = _std_logging.ERROR
FATAL = _std_logging.FATAL
INFO = _std_logging.INFO
WARNING = _std_logging.WARNING
_std_logging.captureWarnings(True)

_NULL_HANDLER = _std_logging.NullHandler()


def _default_config():
    try:
        with open(_YAML_FILE, 'rb') as f:
            return _yaml.load(f.read())
    except IOError:
        print "*** %s NOT FOUND ***" % _YAML_FILE
        raise


class Config(dict):
    """ An extended dictionary with some methods to modify the configuration
    settings before ultimately configuring it with the logging module.

    Creating an instance bootstraps the `default.yaml`__ config.

    Args:
        application_name (optional): the name of your application.

            This can be depicted as a path if you intend to have subfolders. If
            nothing is provided, this will signal just console logging.

        log_filename (optional): Name of the log file before .log. (default: "server")
    """
    def __init__(self, application_name=None, log_filename="server"):
        super(Config, self).__init__(_default_config())

    def _reset_console(self):
        self["handlers"]["console"] = {
            "class": "zachlog.colorterm.ColorizedStreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }

    @property
    def color(self):
        """Returns True if console output will be in color"""
        if self["handlers"]["console"]["class"] == "logging.NullHandler":
            return None
        return self["handlers"]["console"]["class"] == \
            "zachlog.colorterm.ColorizedStreamHandler"

    @color.setter
    def color(self, inp):
        """Set the console output to be colored, None to disable"""
        if inp is None:
            self._remove_handler("console")
        else:
            self._reset_console()
            if inp:
                self["handlers"]["console"]["class"] = \
                    "zachlog.colorterm.ColorizedStreamHandler"
            else:
                self["handlers"]["console"]["class"] = "logging.StreamHandler"

    def _remove_handler(self, name):
        self["handlers"][name].clear()
        self["handlers"][name]["class"] = "logging.NullHandler"
        return self

    def configure(self):
        """Alias of :func:`.dictConfig`.

        It will set up logging and readies your logger instance for use."""
        dictConfig(self)


def dictConfig(config):  # noqa
    """Delegate to :func:`logging.config.dictConfig`."""
    _logconfig.dictConfig(config)


def getLogger(name):  # noqa
    """Delegate to :func:`logging.getLogger`.

    Add a :class:`logging.NullHandler` as well in case :func:`.dictConfig` is
    not invoked to prevent errors from manifesting due to missing handlers.
    """
    logger = _std_logging.getLogger(name)
    # Ensure that we attach a null handler if for some reason dictConfig isn't used.
    if _NULL_HANDLER not in logger.handlers:
        logger.addHandler(_NULL_HANDLER)
    return logger
