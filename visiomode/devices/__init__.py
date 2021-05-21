"""Communications module for external microcontrollers over the serial bus"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import abc
import serial
import time
import serial.tools.list_ports as ports
import visiomode.mixins as mixins
import visiomode.config as conf


def get_available_devices():
    """Return list of all serial devices connected to the machine."""
    return [dev.device for dev in ports.comports()]


def check_device_profile(profile_id, address):
    """Allow user to check whether a device profile will work for a port address."""
    OutputDevice.get_child(profile_id)(address).output()


class Device(mixins.BaseClassMixin, mixins.YamlAttributesMixin):
    def __init__(self, address, profile_path=None):
        self.address = address
        self.profile_path = profile_path or (
            conf.Config().devices + os.sep + self.get_identifier() + ".yml"
        )
        self.load_yaml(self.profile_path)

    def __repr__(self):
        return "<{} device at {}>".format(self.get_common_name(), self.address)


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
    reward_epoch = 1500  # time from moment servo moves out in ms

    def __init__(self, address):
        super().__init__(address)
        self.bus = serial.Serial(address, 9600, timeout=1)
        time.sleep(2)  # Allow the port enough time to do its thing after a reset

    def output(self):
        """Dispenses water reward."""
        self.bus.write(b"T\n")
        time.sleep(self.reward_epoch / 1000)


class DeviceError(Exception):
    pass
