# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module provides classes and functionnalities used for reading/writing
into a data file.
"""

from __future__ import print_function
from enum import IntEnum
import os
import struct


class GestureType(IntEnum):
    """An enum mapping every gesture to a number."""
    UNKNOWN = 0
    FOREHAND_SMASH = 1
    FOREHAND_SMASH_JUMP = 2
    FOREHAND_CLEAR = 3
    FOREHAND_DRIVE = 4
    FOREHAND_DROP_SHOT = 5
    FOREHAND_NET_SHOT = 6
    FOREHAND_NET_KILL = 7
    BACKEND_SMASH = 8
    BACKEND_CLEAR = 9
    BACKEND_DROP_SHOT = 10
    BACKEND_NET_SHOT = 11
    BACKEND_NET_KILL = 12


class _Factory(object):         # pylint: disable=too-few-public-methods
    """A class defining the unpack_from_file class method.
    Derived class must define this two class variables:
    - format_string: the format string that represents the struct to be packed.
    - struct_size: the size of the struct to be packed.
    """
    format_string = None
    struct_size = None

    @classmethod
    def unpack_from_file(cls, bin_file):
        """Instanciates a derived class by reading data from the specified
        binary file."""
        bin_data = bin_file.read(cls.struct_size)
        if not bin_data:
            raise IOError("Could not read %s in file" % cls.__name__)
        data = struct.unpack(cls.format_string, bin_data)
        return cls(*data) # pylint: disable=star-args


class FileHeader(_Factory):
    """A header class that describes a data file."""

    # Format string must be updated when adding/removing member variables
    # that need to be packed into data file.
    format_string = "<iiii"
    struct_size = struct.calcsize(format_string)

    def __init__(self,
                 player_id=-1,
                 gesture_type=GestureType.UNKNOWN,
                 rec_frame_rate=20,
                 gestures_nbr=0):
        self.player_id = player_id
        self.gesture_type = gesture_type
        self.rec_frame_rate = rec_frame_rate
        self._gestures_nbr = gestures_nbr

    def get_gestures_nbr(self):
        """Get the number of gestures."""
        return self._gestures_nbr

    def pack_into_file(self, bin_file):
        """Packs class contents into a binary struct, and write it into the
        specified binary file."""
        bin_file.write(struct.pack(self.format_string,
                                   self.player_id,
                                   self.gesture_type,
                                   self.rec_frame_rate,
                                   self._gestures_nbr))


class GestureHeader(_Factory):
    """A header class that describes a recorded gesture data."""
    pass                        # TODO(gilles) implement the class.



################################################################################
#     UNIT TESTS
################################################################################

def unit_test_struct():
    """A test set for struct packing/unpacking into binary files."""

    print ("    - Testing stuct pack/unpack...")

    header1 = FileHeader()
    header1.player_id = 42

    header2 = FileHeader()
    header2.gesture_type = GestureType.FOREHAND_SMASH

    file_name = "data_file_test.dat"
    if os.path.isfile(file_name):
        os.remove(file_name)

    with open(file_name, "wb") as bin_file:
        header1.pack_into_file(bin_file)
        header2.pack_into_file(bin_file)
    with open(file_name, "rb") as bin_file:
        header3 = FileHeader.unpack_from_file(bin_file)
        header4 = FileHeader.unpack_from_file(bin_file)

    if os.path.isfile(file_name):
        os.remove(file_name)

    assert header3.__dict__ == header1.__dict__
    assert header4.__dict__ == header2.__dict__
    assert header3.__dict__ != header2.__dict__


if __name__ == "__main__":
    print ("Testing data_file module:")
    unit_test_struct()
    print ("Test succeeded.")
