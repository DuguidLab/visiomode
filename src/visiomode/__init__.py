"""Application entry point."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import faulthandler  # report segmentation faults as tracebacks

import visiomode.core
from visiomode.__about__ import __version__  # noqa: F401

faulthandler.enable()


def run():
    """Entry point for the `visiomode` cli command."""
    app = visiomode.core.Visiomode()
    app.run()


if __name__ == "__main__":
    run()
