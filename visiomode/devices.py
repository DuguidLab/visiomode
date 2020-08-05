"""Communications module for external microcontrollers over the serial bus"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import abc
import serial
import threading
import visiomode.mixins as mixins


class Device(mixins.BaseClassMixin, mixins.YamlAttributesMixin):
    address = None

    def __init__(self, address, config_path=None):
        self.address = address
        self.load_yaml(config_path)

    def __repr__(self):
        return "<{} device at {}>".format(self.__name__, self.address)


class InputDevice(abc.ABC, Device):
    """Interface for input devices"""


class OutputDevice(abc.ABC, Device):
    """Interface for output devices"""

    @abc.abstractmethod
    def output(self):
        pass

    def calibrate(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__dict__.keys():
                setattr(self, key, value)


class WaterReward(OutputDevice):
    servo_start = 10
    servo_end = 170
    movt_delay = 500
    pump_ms = 50

    def __init__(self, address, threaded=True):
        super().__init__(address)
        self.threaded = threaded

    def output(self):
        """Dispenses water reward."""
        if not self.threaded:
            return self._dispense()
        thread = threading.Thread(target=self._dispense)
        thread.start()

    def _dispense(self):
        with serial.Serial(self.address) as bus:
            bus.write("test")


class DeviceError(Exception):
    pass
