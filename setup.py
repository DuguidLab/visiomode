"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup, find_packages

APP = ["run.py"]
DATA_FILES = [("visiomode", ["visiomode/res"])]
OPTIONS = {
    "iconfile": "/Users/celefthe/Programming/projects/visiomode/icon.icns",
}

setup(
    name="visiomode",
    version="0.0.1",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    packages=find_packages(),
    include_package_data=True,
)