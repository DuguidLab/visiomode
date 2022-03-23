"""Application entry point."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import faulthandler  # report segmentation faults as tracebacks
import visiomode.core

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("visiomode").version
except DistributionNotFound:
    # package is not installed
    pass


faulthandler.enable()


def run():
    """Application entry point."""
    visiomode.core.Visiomode()


if __name__ == "__main__":
    run()
