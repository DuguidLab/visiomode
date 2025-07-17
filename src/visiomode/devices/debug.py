#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import time

from visiomode import devices


class DebugInput(devices.InputDevice):
    def get_response(self):
        pass


class DebugOutput(devices.OutputDevice):
    def test(self):
        pass
