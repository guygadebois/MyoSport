# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module records MYO's data that will next be used for feeding
the learning machine system.
"""

import curses
import sys
from myo_buffer import MyoBuffer
from myoraw.myo_raw import MyoRaw
import tools.my_curses as my_curses


def _start_curses(std_screen, myo_raw, myo):
    """Process in a curses environment."""

    my_curses.init(std_screen)
    last_key = -1
    while True:
        myo_raw.run(1)
        std_screen.clear()
        key = std_screen.getch()
        if key != curses.ERR:
            if key == my_curses.Key.ESCAPE or key == my_curses.Key.Q:
                break
            last_key = key
        std_screen.addstr(10, 10, "Last key pressed : %d\n" % (last_key))
        std_screen.addstr(0, 0, str(myo))
        std_screen.refresh()


def main():
    """Record programs's main function. Launched from command-line.

    Input args:
        TODO(gilles): Add doc when implementing arguments parsing.
    """

    myo_raw = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
    myo = MyoBuffer(myo_raw)
    myo_raw.connect()

    try:
        curses.wrapper(_start_curses, myo_raw, myo)
    except KeyboardInterrupt:
        pass
    finally:
        myo_raw.disconnect()


if __name__ == "__main__":
    main()
