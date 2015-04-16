# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module defines a set of const values used by the project"""

import sys
from tools import const

# Frame rates
const.reading_frame_rate = 60
const.classifying_frame_rate = 10

sys.modules[__name__] = const
