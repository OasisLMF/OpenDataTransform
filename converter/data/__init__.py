import os
import sys


def get_data_root():
    """
    Gets the root of the data directory. This handles running as a normal
    python project and when ran as the pyinstaller exe.
    """
    return getattr(sys, "_MEIPASS", os.path.dirname(__file__))


def get_data_path(*parts):
    """
    Gets a path in the data dir (either in the normal dir or the temp
    dir for the py installer exe)

    :param parts: The parts of the path to join (similar to os.path.join)
    """
    return os.path.join(get_data_root(), *parts)
