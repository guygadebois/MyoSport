# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module records MYO's data that will next be used for feeding
the learning machine system.
"""

import curses
import sys
from threading import Thread
import time
from myo_buffer import MyoBuffer
from myoraw.myo_raw import MyoRaw
import project_const as const
import tools.my_curses as my_curses


class TooHighLatency(Exception):
    """TODO(gilles): Add doc"""
    pass


def _loop(std_screen, myo):
    """Reading loop. Outputs MYO's data. Loops until ESC or Q key is pressed."""

    period = 1. / const.reading_frame_rate
    key = "None"
    while True:
        start_time = time.time()
        std_screen.clear()
        try:
            key = std_screen.getkey()
            if key == "q":
                break
        except curses.error:
            pass
        std_screen.addstr(10, 10, "Last key pressed : %s\n" % (key))
        std_screen.addstr(0, 0, str(myo))
        std_screen.refresh()
        sleep_time = period - (time.time() - start_time)
        if sleep_time < 0:
            raise TooHighLatency
        time.sleep(max(sleep_time, 0))


def _start_curses(std_screen, myo):
    """Process in a curses environment."""

    my_curses.init(std_screen)
    _loop(std_screen, myo)


def main():
    """Record programs's main function. Launched from command-line.

    Input args:
        TODO(gilles): Add doc when implementing arguments parsing.
    """

    myo_raw = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
    myo = MyoBuffer(myo_raw)
    myo_raw.connect()
    myo.start()

    try:
        curses.wrapper(_start_curses, myo)
    except KeyboardInterrupt:
        pass
    finally:
        myo.stop()
        myo.join()
        myo_raw.disconnect()


if __name__ == "__main__":
    main()
