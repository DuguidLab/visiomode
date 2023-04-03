"""Communications module for external microcontrollers over the serial bus"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import queue
import logging
import serial.tools.list_ports as ports
import visiomode.mixins as mixins
import visiomode.config as conf
import visiomode.plugins as plugins


def get_available_devices():
    """Return list of all serial devices connected to the machine."""
    return [dev.device for dev in ports.comports()]


def get_input_device(profile_id, address=None):
    return InputDevice.get_child(profile_id)(address)


def get_output_profile(profile_id, address=None):
    return OutputDevice.get_child(profile_id)(address)


def check_device_profile(profile_id, address):
    """Allow user to check whether a device profile will work for a port address."""
    # TODO - support input devices too
    try:
        OutputDevice.get_child(profile_id)(address).test()
    except TypeError:
        logging.error("Not an output device!")

    try:
        InputDevice.get_child(profile_id)(address).test()
    except TypeError:
        logging.error("Not an input device!")


class Device(mixins.BaseClassMixin, mixins.ProtocolEventsMixin):
    def __init__(self, address=None, profile_path=None):
        self.profile_path = profile_path or (
            conf.Config().devices + os.sep + self.get_identifier() + ".yml"
        )
        self.address = address

    def test(self):
        raise NotImplementedError

    def __repr__(self):
        return "<{} device at {}>".format(self.get_common_name(), self.address)


class InputDevice(Device):
    """Interface for input devices"""

    def get_response(self):
        raise NotImplementedError


class OutputDevice(Device):
    """Interface for output devices"""

    def calibrate(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__dict__.keys():
                setattr(self, key, value)


class DeviceError(Exception):
    pass


plugins.load_modules_dir(__path__[0])
