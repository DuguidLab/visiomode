#!/bin/bash

# Script to build a release and upload to PYPI
#
# This file is part of visiomode.
# Copyright (c) 2022 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
# Distributed under the terms of the MIT Licence.
#
set -e

version="$1"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "master" ]]; then
  echo 'The release script should only be run on the master branch. Aborting...';
  exit 1;
fi

echo "Creating release for $version"

git tag -m "Release version $version" "v$version"

rm -rf dist/
SETUPTOOLS_SCM_PRETEND_VERSION_FOR_VISIOMODE="$version" python3 -m build
twine upload dist/*
