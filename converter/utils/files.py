import contextlib
import urllib.parse
from urllib import parse

import fsspec


def split_s3_url(parts):
    query = parse.parse_qs(parts.query)
    params = {
        "anon": "key" not in query and "token" not in query,
        "key": query.get("key", [None])[0],
        "secret": query.get("secret", [None])[0],
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


def split_azure_url(parts):
    connection_string = None

    query = parse.parse_qs(parts.query)
    if "endpoint" in query:
        connection_string = f"BlobEndpoint={ query.get('endpoint', [None])[0]};"
    if "account" in query:
        connection_string += f"AccountName={ query.get('account', [None])[0] };"
    if "key" in query:
        connection_string += f"AccountKey={ query.get('key', [None])[0] };"


    params = {
        "anon": "key" not in query and "secret" not in query,
        "connection_string": connection_string,
        "client_id": query.get("client", [None])[0],
        "client_secret": query.get("secret", [None])[0],
        "tenant_id": query.get("tenant", [None])[0],
        "account_name": query.get("account", [None])[0],
        "account_key": query.get("key", [None])[0],
        "use_ssl": query.get("ssl", ["True"])[0] == "True",
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
    elif url_parts.scheme in ["az", "abfs", "adl"]:
        path, params = split_azure_url(url_parts)

    return opener, path, params


@contextlib.contextmanager
def open_file(path: str, mode, **kwargs):
    opener, path, opts = parse_url_options(path)
    with opener(path, mode, **kwargs, **opts) as f:
        yield f
