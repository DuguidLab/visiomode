"""App configuration loader"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import yaml


DEFAULT_PATH = '/etc/visiomode/config.yaml'


class Config:
    """Configuration class for visiomode components.

    Defaults to development settings unless initialised with a valid path to a config YAML.
    """
    redis_port = 6379
    redis_host = 'localhost'
    debug = True

    def __init__(self, path=DEFAULT_PATH):
        """Initialises Config with a path to a configuration file.

        If a valid configuration file exists, the program assumes it is NOT in debug mode, unless the config file
        specifies otherwise.

        Args:
            path: Path to config YAML, defaults to DEFAULT_PATH. Only used if it exists.
        """
        if os.path.exists(path):
            self.debug = False
            self.load(path)

    def load(self, path):
        """Method to load YAML file parameters as class attributes.

        Args:
            path: Path to config YAML, assumed to exist.
        """
        with open(path) as f:
            config = yaml.safe_load(f)
            for key, value in config.items():
                setattr(self, key, value)
