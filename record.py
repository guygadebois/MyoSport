# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module records MYO's data that will next be used for feeding
the learning machine system.
"""

import argparse
import curses
import sys
from threading import Thread
import time
from tools.data_file import Recording, GestureType
from myo_buffer import MyoBuffer
from myoraw.myo_raw import MyoRaw
import project_const as const
import tools.my_curses as my_curses


class TooHighLatency(Exception):
    """TODO(gilles): Add doc"""
    pass


def _start_recording(std_screen):
    """Starts recording process."""
    std_screen.bkgd(' ', curses.color_pair(my_curses.ColorPair.RECORDING))


def _stop_recording(std_screen):
    """Stops recording process."""
    std_screen.bkgd(' ', curses.color_pair(my_curses.ColorPair.DEFAULT))


def _loop(std_screen, myo):
    """Reading loop. Outputs MYO's data. Loops until ESC or Q key is pressed."""

    period = 1. / const.reading_frame_rate
    key = "None"
    recording = False
    while True:
        start_time = time.time()
        std_screen.clear()
        try:
            key = std_screen.getkey()
            if key == "q":
                break
            if key == " ":
                recording = not recording
                if recording:
                    _start_recording(std_screen)
                else:
                    _stop_recording(std_screen)
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


def record(player_id, gesture_type):
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
    parser = argparse.ArgumentParser(description="Records gestures using Myo.")
    parser.add_argument("player_id",
                        type=int,
                        help="a positive integer representing the player's ID.")
    parser.add_argument("gesture_type",
                        type=int,
                        help="a positive integer representing a gesture type.")
    args = parser.parse_args()
    if args.player_id < 0:
        parser.error("player_id must be a positive integer.")
    if args.gesture_type < GestureType.__MIN__ or args.gesture_type > GestureType.__MAX__:
        parser.error("gesture_type must be between %d and %d" % (GestureType.__MIN__, GestureType.__MAX__))
    record(args.player_id, GestureType(args.gesture_type))
