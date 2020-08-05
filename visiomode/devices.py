"""Communications module for external microcontrollers over the serial bus"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import abc
import serial
import threading
import serial.tools.list_ports as ports
import visiomode.mixins as mixins
import visiomode.config as conf


def get_available_devices():
    """Return list of all serial devices connected to the machine."""
    return [dev.device for dev in ports.comports()]


class Device(mixins.BaseClassMixin, mixins.YamlAttributesMixin):
    def __init__(self, address, profile_path=None):
        self.address = address
        self.profile_path = profile_path or (
            conf.Config().devices + os.sep + self.get_identifier() + ".yml"
        )
        self.load_yaml(self.profile_path)

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

    def __init__(self, address):
        super().__init__(address)
        self.bus = serial.Serial(address, 9600, timeout=5)

    def output(self):
        """Dispenses water reward."""
        # if not self.threaded:
        #     return self._dispense()
        # thread = threading.Thread(target=self._dispense)
        # thread.start()
        self.bus.write(b"T")


class DeviceError(Exception):
    pass
