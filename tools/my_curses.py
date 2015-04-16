# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module provides curses functions and enums used by interactives modules
"""

import curses


def init(std_screen):
    """Initialize curses window with custom parameters."""
    curses.curs_set(0)
    std_screen.nodelay(True)


if __name__ == "__main__":
    pass
