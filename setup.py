import os

from setuptools import find_packages, setup


root_path = os.path.dirname(__file__)


def readfile(p):
    with open(p) as f:
        return f.read()


def read_reqs():
    reqs_path = os.path.join(root_path, "requirements-package.in")
    return readfile(reqs_path).split("\n")


def read_readme():
    reqs_path = os.path.join(root_path, "README.rst")
    return readfile(reqs_path)


setup(
    name="converter",
    version="0.0.1",
    packages=find_packages(exclude=("tests", "tests.*")),
    package_data={"converter": ["_data/mappings/*"], "": ["README.rst"]},
    install_requires=read_reqs(),
    entry_points="""
        [console_scripts]
        converter=converter.cli:cli
    """,
    long_description=read_readme(),
    url="https://github.com/OasisLMF/OasisDataconverter",
    python_requires=">=3.8",
)
