from setuptools import setup, find_packages
from glob import glob

APP = ["run.py"]
DATA_FILES = [("visiomode", glob("visiomode/res/*"))]

setup(
    name="visiomode",
    version="0.0.1",
    app=APP,
    data_files=DATA_FILES,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "redis",
        "Flask",
        "Flask-SocketIO",
        "PyYAML",
        "pygame==2.0.0.dev6",
        "numpy",
    ],
)
