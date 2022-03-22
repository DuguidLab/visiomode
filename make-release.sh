#!/bin/bash

# Script to build a release and upload to PYPI
#
# This file is part of visiomode.
# Copyright (c) 2022 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
# Distributed under the terms of the MIT Licence.
#
set -e

version="$1"

echo "Creating release for $version"

git tag -m "Release version $version" "v$version"
python -m setuptools_scm

rm -r dist/
python3 -m build
#twine upload dist/*
