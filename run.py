"""Application entry point."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import faulthandler  # report segmentation faults as tracebacks
from visiomode.main import main

faulthandler.enable()

main()
