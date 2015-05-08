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

    # Format string must be updated when adding/removing member variables
    # that need to be packed into data file.
    format_string = "<ii"
    struct_size = struct.calcsize(format_string)

    def __init__(self,
                 samples_nbr=0,
                 next_gesture_offset=-1):
        self.samples_nbr = samples_nbr
        self.next_gesture_offset = next_gesture_offset

    def is_last_gesture(self):
        """Returns True if gesture is the last of the data file."""
        return self.next_gesture_offset != -1

    def pack_into_file(self, bin_file):
        """Packs class contents into a binary struct, and write it into the
        specified binary file."""
        bin_file.write(struct.pack(self.format_string,
                                   self.samples_nbr,
                                   self.next_gesture_offset))


class GestureSample(_Factory):
    """A class containing data for one sample of a recorded gesture."""

    # Format string must be updated when adding/removing member variables
    # that need to be packed into data file.
    format_string = "<iiiiiiiiiiiiiiiiii"
    struct_size = struct.calcsize(format_string)

    def __init__(self, *args):
        """A sample can be initialized either by passing 18 integers or 4 lists.
        > _Factory.unpack_from_files passes 18 integers by unrolling:
        emg(8 integers), quat(4 integers), acc(3 integers), gyro(3 integers)
        > Any other manual way to initialize GestureSample should be done by
        passing 4 lists representing, in order: emg, quat, acc, gyro"""
        if len(args) == 18:
            self.emg = args[:8]
            self.quat = args[8:12]
            self.acc = args[12:15]
            self.gyro = args[15:]
        elif len(args) == 4:
            emg = args[0]
            quat = args[1]
            acc = args[2]
            gyro = args[3]

            assert len(emg) == 8
            assert len(quat) == 4
            assert len(acc) == 3
            assert len(gyro) == 3

            self.emg = tuple(emg)
            self.quat = tuple(quat)
            self.acc = tuple(acc)
            self.gyro = tuple(gyro)
        else:
            assert False

    def pack_into_file(self, bin_file):
        """Packs class contents into a binary struct, and write it into the
        specified binary file."""
        assert len(self.emg) == 8
        assert len(self.quat) == 4
        assert len(self.acc) == 3
        assert len(self.gyro) == 3

        args = self.emg + self.quat + self.acc + self.gyro
        bin_file.write(struct.pack(self.format_string, *args)) # pylint: disable=star-args


class Gesture(object):
    """A class representing a whole gesture recording.
    Contains a header and a list of samples.
    """

    def __init__(self, gesture_header=None, samples=None):
        """A Gesture can be initialized either by instanciating a new Gesture
        or by calling 'unpack_from_file()'.
        Arguments should be None when instanciating a new Gesture."""
        if gesture_header is None:
            self.header = GestureHeader()
        else:
            assert type(gesture_header) == GestureHeader
            self.header = gesture_header
        if samples is None:
            self.samples = []
        else:
            self.samples = samples

    def append_sample(self, emg, quat, acc, gyro):
        """Appends a sample at the end of the gesture."""
        self.samples.append(GestureSample(emg, quat, acc, gyro))
        self.header.samples_nbr += 1

    def pack_into_file(self, bin_file):
        """Packs gesture header and samples into the specified binary file."""
        assert self.header.samples_nbr > 0

        offset = bin_file.tell() # Get current offset in file.
        offset += GestureHeader.struct_size
        offset += self.header.samples_nbr * GestureSample.struct_size
        self.header.next_gesture_offset = offset

        self.header.pack_into_file(bin_file)
        for sample in self.samples:
            sample.pack_into_file(bin_file)

    @classmethod
    def unpack_from_file(cls, bin_file):
        """Creates a Gesture instance by reading
        header and samples from the specified binary file."""
        header = GestureHeader.unpack_from_file(bin_file)
        samples = []
        for _ in range(header.samples_nbr):
            samples.append(GestureSample.unpack_from_file(bin_file))
        return Gesture(header, samples)


class Recording(object):
    """A class representing a set of gestures, recorded all at once.
    Contains a file header and a list of gestures."""

    def __init__(self, file_header=None, gestures=None):
        """A Recording can be initialized either by instanciating a new
        Recording or by calling 'unpack_from_file()'.
        Arguments should be None when instanciating a new Recording."""
        if file_header is None:
            self.file_header = FileHeader()
        else:
            assert type(file_header) == FileHeader
            self.file_header = file_header
        if gestures is None:
            self.gestures = []
        else:
            self.gestures = gestures

    def set_player_id(self, player_id):
        """Set a new value to file_header.player_id."""
        assert type(player_id) == int
        self.file_header.player_id = player_id

    def set_gesture_type(self, gesture_type):
        """Set a new value to file_header.gesture_type."""
        assert type(gesture_type) == GestureType
        self.file_header.gesture_type = gesture_type

    def append_gesture(self, gesture):
        """Appends a gesture to the set."""
        assert type(gesture) == Gesture
        self.gestures.append(gesture)
        self.file_header._gestures_nbr += 1

    def pack_into_file(self, bin_file):
        """Packs file header and gestures into the specified binary file."""
        assert self.file_header.get_gestures_nbr() > 0
        assert self.file_header.player_id >= 0
        assert self.file_header.gesture_type != GestureType.UNKNOWN

        self.file_header.pack_into_file(bin_file)
        for gesture in self.gestures:
            gesture.pack_into_file(bin_file)

    @classmethod
    def unpack_from_file(cls, bin_file):
        """Creates a Recording instance by reading
        file header and gestures from the specified binary file."""
        file_header = FileHeader.unpack_from_file(bin_file)
        gestures = []
        for _ in range(file_header.get_gestures_nbr()):
            gestures.append(Gesture.unpack_from_file(bin_file))

        # Make sure whe have reached the end of the file.
        file_position = bin_file.tell()
        bin_file.seek(0, os.SEEK_END)
        end_file_position = bin_file.tell()
        assert file_position == end_file_position
        return Recording(file_header, gestures)


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


def unit_test_complete_packing():
    """Tests packing/unpacking a whole recording into binary file."""

    print ("    - Testing packing a whole recording...")

    # TODO
    pass


if __name__ == "__main__":
    print ("Testing data_file module:")
    unit_test_struct()
    unit_test_complete_packing()
    print ("Test succeeded.")
