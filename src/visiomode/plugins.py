#  This file is part of visiomode.
#  Copyright (c) 2021 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

"""Utility functions for loading plugins."""

import glob
import importlib.util
import logging
import sys
from typing import Optional


def load_module(path: str, name: Optional[str] = None) -> None:
    """Load plugin module from file.

    Args:
        path: Path to plugin module (i.e. a python file).
        name: Name of plugin module. If not provided, this will be inferred from the path.
    """
    name = name or "visiomode{}".format(path.split("visiomode")[-1].replace("/", ".").replace(".py", ""))
    if name in sys.modules:
        logging.info(f"Skipping {name} - plugin module is already loaded")
        return

    spec = importlib.util.spec_from_file_location(name, path)

    if not spec:
        logging.warning(f"Plugin module {name} could not be loaded from {path}")
        return

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    logging.info(f"Loaded plugin module {name}")


def load_modules_dir(path: str, exclude: Optional[list] = None) -> None:
    """Load all modules from a directory.

    This will not load __init__.py in that directory, if one exists.

    Args:
        path: Path to directory containing plugin modules.
        exclude: List of modules to exclude from loading.
    """
    logging.info(f"Loading plugin modules from {path}")
    module_files = glob.glob(path + "/*.py")

    excluded_modules = exclude.append("__init__") if exclude else ["__init__"]
    logging.info(f"Excluding modules {excluded_modules}")

    for module_path in module_files:
        if module_path.split("/")[-1].replace(".py", "") in excluded_modules:
            continue
        load_module(module_path)
