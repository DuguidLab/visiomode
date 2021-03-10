"""App configuration loader"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import yaml
import logging
import visiomode.mixins as mixins


DEFAULT_PATH = "/etc/visiomode/config.yaml"


class Config(mixins.YamlAttributesMixin):
    """Configuration class for visiomode components.

    Defaults to development settings unless initialised with a valid path to a config YAML, or the file specified by
    DEFAULT_PATH exists.
    """

    debug = True
    flask_key = "dev"
    data_dir = "instance/"
    fps = 60
    width = 400
    height = 800
    fullscreen = False
    devices = "devices/"

    def __init__(self, path=DEFAULT_PATH):
        """Initialises Config with a path to a configuration file.

        If a valid configuration file exists, the program assumes it is NOT in debug mode, unless the config file
        specifies otherwise.

        Args:
            path: Path to config YAML, defaults to DEFAULT_PATH. Only used if it exists.
        """
        self.load_yaml(path)
