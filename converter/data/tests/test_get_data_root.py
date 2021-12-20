import os
import sys
from tempfile import TemporaryDirectory

from converter.data import get_data_root


def test_pyinstaller_dir_is_not_set___data_root_is_relative_to_package_root():
    assert os.path.abspath(get_data_root()) == os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )


def test_pyinstaller_dir_is_set___data_root_is_relative_installer_dir():
    try:
        with TemporaryDirectory() as d:
            sys._MEIPASS = d
            assert os.path.abspath(get_data_root()) == os.path.abspath(d)
    finally:
        del sys._MEIPASS
