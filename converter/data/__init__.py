import os
import re
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


def hide_system_data_path(path):
    """
    Takes a path and replaces the system directory with a more useful string.

    When the exe is ran the data files will be extracted to a tmp directory
    which     is not useful as it will not exist once the exe is closed. Here
    we replace the system data path with something that makes it more explicit
    that the file came from the tool.

    The result is no longer a useful path from a system point of view and
    should only be used for reporting to users

    :param path: The path to process

    :return: The processed path
    """
    replacer = re.compile(f"^{os.path.abspath(get_data_root())}/")

    return replacer.sub("<system data path>/", os.path.abspath(path))
