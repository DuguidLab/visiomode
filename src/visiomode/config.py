"""App configuration loader"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import json
import logging

logging.basicConfig(level=logging.INFO)


CONFIG_PATH = ".visiomode.json"

DEFAULT_CONFIG = {
    "debug": True,
    "flask_key": "dev",
    "data_dir": "visiomode_data",
    "cache_dir": "visiomode_data/cache",
    "fps": 60,
    "width": 400,
    "height": 800,
    "fullscreen": False,
    "devices": "devices/",
}


class Config:
    """App configuration loader."""

    debug: bool
    flask_key: str
    data_dir: str
    cache_dir: str
    fps: int
    width: int
    height: int
    fullscreen: bool
    devices: str

    def __init__(self):
        """Initialises Config with a path to a configuration file.

        If a valid configuration file exists, the program assumes it is NOT in debug mode, unless the config file
        specifies otherwise.

        Args:
            path: Path to config YAML, defaults to DEFAULT_PATH. Only used if it exists.
        """
        if os.path.exists(CONFIG_PATH):
            logging.info(f"Loading config from {CONFIG_PATH}")
            self._load_config(CONFIG_PATH)
        else:
            logging.warning("No config file found, using defaults")
            self._set_defaults()
            self.save()

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    def save(self, path=CONFIG_PATH):
        with open(path, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    def _load_config(self, path):
        """Loads config from a JSON file.

        Args:
            path: Path to config JSON file.
        """
        with open(path, "r") as f:
            config = json.load(f)

        for key, value in config.items():
            if key in DEFAULT_CONFIG:
                setattr(self, key, value)
            else:
                logging.warning("Unknown config key: {}".format(key))

    def _set_defaults(self):
        """Sets config to default values."""
        for key, value in DEFAULT_CONFIG.items():
            setattr(self, key, value)
