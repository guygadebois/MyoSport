# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module records MYO's data that will next be used for feeding
the learning machine system.
"""

import sys
from myoraw.myo_raw import MyoRaw


def main():
    """Record programs's main function. Launched from command-line.

    Input args:
        TODO(gilles): Add doc when implementing arguments parsing.
    """

    myo_raw = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
    myo_raw.connect()

    def proc_emg(emg, _):
        """Called every time MYO send new EMG data."""
        print emg

    def proc_imu(quat, acc, gyro):
        """Called every time MYO send new IMU data."""
        print quat, acc, gyro

    myo.add_emg_handler(proc_emg)
    myo.add_imu_handler(proc_imu)


    try:
        while True:
            myo_raw.run(1)

    except KeyboardInterrupt:
        pass
    finally:
        myo_raw.disconnect()

if __name__ == '__main__':
    main()
