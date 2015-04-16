# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module provides curses functions and enums used by interactives modules
"""

import curses
from enum import Enum


class Key(Enum):
    """Enum representing keybord keys events.
    Can be compared with getch()'s return value
    """
    SPACE = 32
    ESCAPE = 27
    Q = 113

def init(std_screen):
    """Initialize curses window with custom parameters."""
    curses.curs_set(0)
    std_screen.nodelay(True)


if __name__ == "__main__":
    pass
