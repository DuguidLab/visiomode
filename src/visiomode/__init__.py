"""Application entry point."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import faulthandler  # report segmentation faults as tracebacks
import visiomode.core

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("visiomode")
except PackageNotFoundError:
    # package is not installed
    pass


faulthandler.enable()


def run():
    """Application entry point."""
    visiomode.core.Visiomode()
