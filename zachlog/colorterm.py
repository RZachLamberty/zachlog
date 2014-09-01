#!/usr/bin/env python
"""
colorterm

Facilities for colorized output. Includes a colorized stream handler that uses
colors when appropriate.

The handler is stripped down, and strictly python 2.7-compatible. Based off the
version found in logutils_ sans the Win32 API conversion.

The possible ANSI escape sequences are described here_.

.. _logutils: https://pypi.python.org/pypi/logutils/
.. _here: http://en.wikipedia.org/wiki/ANSI_escape_code#Sequence_elements

.. moduleauthor:: Patrick Wong <pwong@peak6.com>
"""

from __future__ import absolute_import
from logging import StreamHandler as _StreamHandler
from itertools import imap as _imap
from functools import partial as _partial
import zachlog as _logging

# Ye olde constants
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = xrange(8)
BOLD, FAINT, ITALIC, UNDERLINE, BLINK = _imap(str, xrange(1, 6))
_CSI, _RESET = '\x1b[', '\x1b[0m'
_LOGGER = _logging.getLogger(__name__)


def _color(fg=None, bg=None, style=""):
    params = []
    if bg:
        params.append(str(bg + 40))
    if fg:
        params.append(str(fg + 30))
    params.extend(style)
    return "%sm" % ";".join(params)


def colorize(msg, foreground, background=None, style=""):
    """Colorize some text."""
    return ''.join((_CSI, _color(foreground, background, style), str(msg), _RESET))


# Make methods for each color
(black, red, green, yellow,
 blue, magenta, cyan, white) = (_partial(colorize, foreground=c) for c in xrange(8))


_DEFAULT_LEVELS = {
    "DEBUG": _color(fg=WHITE),
    "INFO": _color(fg=WHITE, style=BOLD),
    "WARNING": _color(fg=YELLOW),
    "ERROR": _color(fg=RED),
    "CRITICAL": _color(bg=RED, fg=WHITE, style=[BOLD, BLINK])
}


class ColorizedStreamHandler(_StreamHandler):
    """A stream handler which supports colorizing of console streams.
    Does not support Windows (on purpose) due to added complexity.
    """
    def __init__(self, *args, **kwargs):
        super(ColorizedStreamHandler, self).__init__(*args, **kwargs)
        self.levels = _DEFAULT_LEVELS.copy()

    @property
    def __is_tty(self):
        try:
            return self.stream.isatty()
        except Exception:
            return False

    def set_level_color(self, **kwargs):
        """Update the style config for kwargs of log levels pointing to a
        triple of ``(foreground, background, [list of styles])``.
        """
        for k, v in kwargs.viewitems():
            self.levels[k] = _color(*v)

    def emit(self, record):
        try:
            message = self.format(record)
            self.stream.write(message)
            self.stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def format(self, record):
        message = _StreamHandler.format(self, record)
        # Do not colorize stack traces or non-stream sources
        if self.__is_tty:
            parts = message.split('\n', 1)
            parts[0] = self.__colorize(parts[0], record)
            message = '\n'.join(parts)
        return message

    def __colorize(self, message, record):
        """Colorize the message."""
        color = self.levels.get(record.levelname)
        if color:
            message = ''.join((_CSI, color, message, _RESET))
        return message


def _main():
    _logging.Config("rotate").no_file.configure()
    logger = _logging.getLogger("colorterm")
    logger.debug('Dude, this is seriously what, a debugging message?')
    logger.info("There's information, then there's information")
    logger.warning('WARNING: die soon')
    logger.error('ERROR: somehting wrong')
    logger.critical('CRITICAL: yu are dooomed')
    #for m in (red, yellow, green, cyan, blue, magenta):
    #    logger.debug(m("MAKING RAINBOW"))

if __name__ == '__main__':
    _main()
