"""Communications module for external microcontrollers over the serial bus"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import re
import json
import serial
import threading


class BaseDevice:
    address = None

    def __init__(self, address):
        self.address = address

    @classmethod
    def get_common_name(cls):
        """"Return the human-readable, space-separated name for the class."""
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)

    @classmethod
    def get_children(cls):
        """Return all inheriting children as a generator."""
        for child in cls.__subclasses__():
            yield from child.get_children()
            yield child

    @classmethod
    def get_identifier(cls):
        return cls.__name__.lower()

    def __repr__(self):
        return "<{} device at {}>".format(self.get_common_name(), self.address)


class InputDevice(BaseDevice):
    pass


class OutputDevice(BaseDevice):
    pass


class WaterReward(OutputDevice):
    def __init__(self, address, threaded=True):
        super().__init__(address)
        self.threaded = threaded

    def dispense(self):
        if not self.threaded:
            return self._dispense()
        thread = threading.Thread(target=self._dispense)
        thread.start()

    def _dispense(self):
        with serial.Serial(self.address) as bus:
            bus.write("test")


class DeviceError(Exception):
    pass
