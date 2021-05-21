#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

"""Utility functions for loading plugins."""

import glob
import importlib.util
import sys
import logging
from builtins import str


def load_module(path: str, name: str = None) -> None:
    """Load plugin module from file.

    Args:
        path:
        name:

    Returns:

    """
    name = name or "visiomode{}".format(
        path.split("visiomode")[-1].replace("/", ".").replace(".py", "")
    )
    if name in sys.modules:
        logging.info("Skipping {} - plugin module is already loaded".format(name))
        return

    spec = importlib.util.spec_from_file_location(name, path)

    if not spec:
        logging.warning(
            "Plugin module {} could not be loaded from {}".format(name, path)
        )
        return

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    logging.info("Loaded plugin module {}".format(name))


def load_modules_dir(path: str, exclude: list = None) -> None:
    """Load all modules from a directory.

    This will not load __init__.py, if one exists.

    Args:
        path:
        exclude:

    Returns:

    """
    logging.info("Loading plugin modules from {}".format(path))
    module_files = glob.glob(path + "/*.py")

    excluded_modules = exclude.append("__init__") if exclude else ["__init__"]
    logging.info("Excluding modules {}".format(excluded_modules))

    for module_path in module_files:
        if module_path.split("/")[-1].replace(".py", "") in excluded_modules:
            continue
        load_module(module_path)
