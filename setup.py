from setuptools import setup
from glob import glob

APP = ["run.py"]
DATA_FILES = [("visiomode", glob("visiomode/res/*"))]

setup(
    name="visiomode",
    version="0.0.1",
    app=APP,
    data_files=DATA_FILES,
    packages=["visiomode"],
    include_package_data=True,
    install_requires=["Flask", "PyYAML"],
    entry_points={'console_scripts': ['visiomode = visiomode.main:main']},
)
