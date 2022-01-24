import os
from distutils import cmd

from setuptools import find_packages, setup


root_path = os.path.dirname(__file__)


def readfile(p):
    with open(p) as f:
        return f.read()


def read_reqs():
    reqs_path = os.path.join(root_path, "requirements-package.in")
    return readfile(reqs_path).split("\n")


def read_readme():
    reqs_path = os.path.join(root_path, "README.md")
    return readfile(reqs_path)


class BuildExeCommand(cmd.Command):
    """A custom command to build the executable."""

    description = "run PyInstaller to generate the executable"
    user_options = []  # type: ignore

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import PyInstaller.building.build_main
        PyInstaller.building.build_main.main(
            None,
            os.path.join(os.path.dirname(__file__), "exe.spec"),
            noconfirm=True,
            distpath=os.path.join(os.path.dirname(__file__), "dist-exe"),
            workpath=os.path.dirname(__file__),
            clean_build=True,
        )


setup(
    name="converter",
    version="0.0.1",
    cmdclass={
        "build_exe": BuildExeCommand,
    },
    packages=find_packages(exclude=("tests", "tests.*")),
    package_data={"converter": ["data/mappings/*"], "": ["README.rst"]},
    install_requires=read_reqs(),
    entry_points="""
        [console_scripts]
        converter=converter.cli:cli
    """,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/OasisLMF/OasisDataconverter",
    python_requires=">=3.8",
    license="BSD 3-Clause License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
