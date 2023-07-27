import urllib.parse
from typing import Dict, List, Union

import requests
import yaml


def is_url(p):
    return urllib.parse.urlparse(p).scheme not in ["", "file"]


def write_yaml(path: str, content: Union[Dict, List]):
    """
    Writes the provided content to the provided path

    :param path: The path to write the data to
    :param content: The data to write
    """
    with open(path, "w") as f:
        yaml.safe_dump(content, f)


def read_yaml(path):
    """
    Reads the yaml data from the provided path

    :param path: The path to read the data from

    :return: The loaded data
    """
    if is_url(path):
        res = requests.get(path)
        return yaml.load(res.text, yaml.SafeLoader)
    else:
        with open(path, encoding="utf8") as f:
            return yaml.load(f, yaml.SafeLoader)
