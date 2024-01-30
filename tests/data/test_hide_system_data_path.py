import os

from converter.data import get_data_root, hide_system_data_path


def test_system_data_path_not_in_path___result_is_unchanged():
    p = os.path.join(os.path.sep, "some", "test", "path")

    assert hide_system_data_path(p) == p


def test_system_data_path_not_at_the_start_of_the_path___result_is_unchanged():
    p = os.path.join(
        os.path.sep,
        "some",
        os.path.abspath(get_data_root())[1:],
        "test",
        "path",
    )

    assert hide_system_data_path(p) == p


def test_system_data_path_at_the_start_but_not_a_dir___result_is_unchanged():
    p = os.path.join(f"{os.path.abspath(get_data_root())}more", "test" "path")

    assert hide_system_data_path(p) == p


def test_system_data_path_the_start___result_is_changed():
    p = os.path.join(os.path.abspath(get_data_root()), "test", "path")

    assert hide_system_data_path(p) == os.path.join(
        "<system data path>", "test", "path"
    )
