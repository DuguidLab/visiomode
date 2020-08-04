"""Communications module for external microcontrollers over the serial bus"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import re
import json
import yaml
import serial
import logging
import threading
import visiomode.config as conf


class BaseDevice:
    address = None

    def __init__(self, address, config_path=None):
        self.address = address
        self.config_path = config_path or (
            conf.Config().devices + os.sep + self.get_identifier() + ".yml"
        )

        # if a config file exists, load it
        if os.path.exists(self.config_path):
            self.load()

    def load(self):
        """Loads YAML file parameters as class attributes."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
            for key, value in config.items():
                if key not in self.__dict__.keys():
                    logging.info(
                        "{} is not a valid config parameter, skipping...".format(key)
                    )
                    continue
                setattr(self, key, value)

    def save(self):
        """Save device configuration."""
        pass

    def calibrate(self):
        """Calibrate device parameters."""
        pass

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
    servo_start = 10
    servo_end = 170
    movt_delay = 500
    pump_ms = 50

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
