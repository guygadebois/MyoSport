# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module defines the MyoBufer class."""


class MyoBuffer(object):
    """This class bufferizes the last MYO's data received."""

    def __init__(self, myo_raw):
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

    def __str__(self):
        return ("EMG => %s\nQUAT=> %s\nACC => %s\nGYRO => %s"
                % (str(self.emg), str(self.quat),
                   str(self.acc), str(self.gyro)))
