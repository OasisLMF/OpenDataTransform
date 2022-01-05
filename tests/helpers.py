import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def change_cwd(new_dir):
    orig_dir = Path().absolute()
    try:
        os.chdir(new_dir)
        yield
    finally:
        os.chdir(orig_dir)
