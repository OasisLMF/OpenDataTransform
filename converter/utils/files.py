import contextlib
import urllib.parse
from urllib import parse

import fsspec


def split_s3_url(parts):
    query = parse.parse_qs(parts.query)
    params = {
        "anon": "key" not in query and "token" not in query,
        "key": query["key"][0],
        "secret": query["secret"][0],
        "token": query.get("token", [None])[0],
        "use_ssl": query.get("ssl", ["True"])[0] == "True",
        "client_kwargs": {
            "endpoint_url": query.get("endpoint", [None])[0],
        },
    }

    return urllib.parse.urlunparse((
        parts[0],
        parts[1],
        parts[2],
        parts[3],
        "",
        parts[5],
    )), params


def parse_url_options(path):
    opener = fsspec.open

    params = {}

    url_parts = parse.urlparse(path)
    if url_parts.scheme == "s3":
        path, params = split_s3_url(url_parts)

    return opener, path, params


@contextlib.contextmanager
def open_file(path: str, mode, **kwargs):
    opener, path, opts = parse_url_options(path)
    with opener(path, mode, **kwargs, **opts) as f:
        yield f
