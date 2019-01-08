#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name="carie_controller",
    version="0.1.0",
    package_dir={'': 'src'},
    packages=find_packages('./src'),

    install_requires=[
        'docutils>=0.3',
    ],

    author="Constantinos Eleftheriou",
    author_email="Contantinos.Eleftheriou@ed.ac.uk",
    description="RPi control module for rodent-fiddle",
    license="MIT",
)
