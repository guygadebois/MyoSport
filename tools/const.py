# Copyright (c) 2015 Gilles Lourdelet
# MIT Licence (MIT)
# Please see LICENSE file for details.
"""This module provides a const-like dictionary class.
After importation, const value can be added to the project by doing :
const.name = value
"""

import sys


class _const(object):
    """A dictionary wrapper that avoids overriding existing keys."""
    class ConstError(TypeError):
        """An error class, raised when attempting to override
        an existing key"""
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value

sys.modules[__name__] = _const()
