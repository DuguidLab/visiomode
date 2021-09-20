"""Communications module for external microcontrollers over the serial bus"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import abc
import serial.tools.list_ports as ports
import visiomode.mixins as mixins
import visiomode.config as conf
import visiomode.plugins as plugins


def get_available_devices():
    """Return list of all serial devices connected to the machine."""
    return [dev.device for dev in ports.comports()]


def get_input_profile(profile_id):
    return InputDevice.get_child(profile_id)


def get_output_profile(profile_id):
    return OutputDevice.get_child(profile_id)


def check_device_profile(profile_id, address):
    """Allow user to check whether a device profile will work for a port address."""
    OutputDevice.get_child(profile_id)(address).output()


class Device(mixins.BaseClassMixin, mixins.YamlAttributesMixin):
    def __init__(self, profile_path=None):
        self.profile_path = profile_path or (
            conf.Config().devices + os.sep + self.get_identifier() + ".yml"
        )
        self.load_yaml(self.profile_path)

    def __repr__(self):
        return "<{} device at {}>".format(self.get_common_name(), self.address)


class InputDevice(abc.ABC, Device):
    """Interface for input devices"""

    def __init__(self, profile_path=None):
        super().__init__()


class OutputDevice(abc.ABC, Device):
    """Interface for output devices"""

    @abc.abstractmethod
    def output(self):
        pass

    def calibrate(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__dict__.keys():
                setattr(self, key, value)


class DeviceError(Exception):
    pass


plugins.load_modules_dir(__path__[0])
