from setuptools import setup, find_packages
from glob import glob

APP = ["run.py"]
DATA_FILES = [("visiomode", glob("visiomode/res/*"))]

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="visiomode",
    version="0.0.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    app=APP,
    data_files=DATA_FILES,
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Flask", "PyYAML"],
)
