# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module defines the MyoBufer class."""

from threading import Thread


class MyoBuffer(Thread):
    """A threaded class that bufferizes the last MYO's data received."""

    def __init__(self, myo_raw):
        Thread.__init__(self)
        self.__myo_raw = myo_raw
        self.__stop_flag = False
        self.emg = []
        self.quat = []
        self.acc = []
        self.gyro = []
        myo_raw.add_emg_handler(self.emg_callback)
        myo_raw.add_imu_handler(self.imu_callback)

    def emg_callback(self, new_emg, _):
        """Called every time MYO sends new EMG data."""
        self.emg = new_emg

    def imu_callback(self, new_quat, new_acc, new_gyro):
        """Called every time MYO sends new IMU data."""
        self.quat = new_quat
        self.acc = new_acc
        self.gyro = new_gyro

    def run(self):
        while not self.__stop_flag:
            self.__myo_raw.run()

    def stop(self):
        self.__stop_flag = True

    def __str__(self):
        return ("EMG => %s\nQUAT=> %s\nACC => %s\nGYRO => %s"
                % (str(self.emg), str(self.quat),
                   str(self.acc), str(self.gyro)))
