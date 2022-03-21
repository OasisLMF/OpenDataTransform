import os

from converter.data import get_data_root, hide_system_data_path


def test_system_data_path_not_in_path___result_is_unchanged():
    p = "/some/test/path"

    assert hide_system_data_path(p) == p


def test_system_data_path_not_at_the_start_of_the_path___result_is_unchanged():
    p = f"/some{os.path.abspath(get_data_root())}/test/path"

    assert hide_system_data_path(p) == p


def test_system_data_path_at_the_start_but_not_a_dir___result_is_unchanged():
    p = f"{os.path.abspath(get_data_root())}more/test/path"

    assert hide_system_data_path(p) == p


def test_system_data_path_the_start___result_is_changed():
    p = f"{os.path.abspath(get_data_root())}/test/path"

    assert hide_system_data_path(p) == "<system data path>/test/path"
