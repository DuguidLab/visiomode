#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import time

import serial

from visiomode import devices


class WaterReward(devices.OutputDevice):
    reward_epoch = 1500  # time from moment servo moves out in ms

    def __init__(self, address):
        super().__init__(address)
        self.bus = serial.Serial(address, 9600, timeout=1)
        time.sleep(2)  # Allow the port enough time to do its thing after a reset

    def on_correct(self):
        """Dispenses water reward."""
        self.bus.write(b"T\n")
        time.sleep(self.reward_epoch / 1000)

    def test(self):
        self.bus.write(b"T\n")
