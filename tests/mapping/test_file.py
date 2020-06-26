from tempfile import NamedTemporaryFile

import yaml


def test_mapping_file_has_no_parent___mapping_ia_loaded_as_expected():
    with NamedTemporaryFile("w+") as f:
        yaml.dump({
            "input_format": "foo",
            "output_format": "bar",
            "forward_transform": {

            }
        }, f)
