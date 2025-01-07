"""App configuration module."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import json
import logging
import os
import shutil
import typing

import serial.tools.list_ports as ports

logging.basicConfig(level=logging.INFO)

DEFAULT_CONFIG = {
    "debug": True,
    "flask_key": "dev",
    "data_dir": "visiomode_data",
    "instance_dir": "visiomode_data/instance",
    "cache_dir": "visiomode_data/cache",
    "db_dir": "visiomode_data/db",
    "fps": 60,
    "width": 400,
    "height": 800,
    "fullscreen": False,
    "devices": "devices",
    "input_device_address": (ports.comports()[1].device if len(ports.comports()) > 1 else "/dev/ttyS0"),
    "reward_device_address": (ports.comports()[0].device if len(ports.comports()) else "/dev/ttyS0"),
    "config_path": ".visiomode.json",
}


class Config:
    """App configuration class.

    This class loads and saves configuration from a JSON file. If no config file exists, it creates one with default values.

    Attributes:
        debug: Debug mode flag.
        flask_key: Flask secret key.
        data_dir: Path to data directory.
        instance_dir: Path to the Flask instance directory.
        cache_dir: Path to cache directory.
        db_dir: Path to database directory.
        fps: Screen refresh rate in frames per second.
        width: Screen width.
        height: Screen height.
        fullscreen: Fullscreen mode flag.
        devices: Path to devices directory.
        input_device_address: Path to the input device address.
        reward_device_address: Path to the device address.
        config_path: Path to the config.
    """

    debug: bool
    flask_key: str
    data_dir: str
    instance_dir: str
    cache_dir: str
    db_dir: str
    fps: int
    width: int
    height: int
    fullscreen: bool
    devices: str
    input_device_address: str
    reward_device_address: str
    config_path: str

    _instance = None

    def __new__(
        cls,
        config_path: typing.Optional[str] = None,
    ) -> "Config":
        """Initialise Config singleton with a path to a configuration file.

        If a valid configuration file exists, the program assumes it is NOT in debug
        mode, unless the config file specifies otherwise. If no config file exists, the
        program assumes it IS in debug mode.

        Args:
            config_path (str, optional): Path to config JSON, defaults to
                                         DEFAULT_CONFIG_PATH. Only used if it exists.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)

            if config_path is None:
                config_path = DEFAULT_CONFIG["config_path"]

            if os.path.exists(config_path):
                logging.info(f"Loading config from {config_path}")
                cls._instance._load_config(config_path)
            else:
                logging.warning("No config file found, using defaults")
                cls._instance._set_defaults()
                cls._instance.save()

            os.makedirs(cls._instance.data_dir, exist_ok=True)
            os.makedirs(cls._instance.cache_dir, exist_ok=True)
            os.makedirs(cls._instance.db_dir, exist_ok=True)
        elif config_path is not None:
            logging.warning("Config has already been loaded, ignoring `config_path` passed to constructor.")

        return cls._instance

    def save(self, path: typing.Optional[str] = None):
        if path is None:
            path = self.config_path
        else:
            self.config_path = path

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def to_dict(self):
        return self.__dict__

    def _load_config(self, config_path: str):
        """Loads config from a JSON file.

        Args:
            config_path: Path to config JSON file.
        """
        with open(config_path) as f:
            config = json.load(f)

        for key, value in config.items():
            if key in DEFAULT_CONFIG:
                setattr(self, key, value)
            else:
                logging.warning(f"Unknown config key: {key}")

        self._validate()

    def _set_defaults(self):
        """Sets config to default values."""
        for key, value in DEFAULT_CONFIG.items():
            setattr(self, key, value)

    def _validate(self) -> None:
        for key, value in DEFAULT_CONFIG.items():
            if not hasattr(self, key):
                logging.warning(f"Config is malformed, it does not have attribute '{key}'. Using default value.")
                setattr(self, key, value)


def clear_cache():
    """Clears the cache directory."""
    shutil.rmtree(Config().cache_dir, ignore_errors=True)
    os.makedirs(Config().cache_dir, exist_ok=True)


def clear_db():
    """Clears the database directory."""
    shutil.rmtree(Config().db_dir, ignore_errors=True)
    os.makedirs(Config().db_dir, exist_ok=True)


def clear_data():
    """Clears the data directory."""
    shutil.rmtree(Config().data_dir, ignore_errors=True)
    shutil.rmtree(Config().config_path, ignore_errors=True)

    # Create new config file with default settings
    Config._instance = None
    new_config = Config()
    new_config.save()
