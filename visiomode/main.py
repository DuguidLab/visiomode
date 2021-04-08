"""Main entry point"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import sys
from pathlib import Path

from visiomode import config, core


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
        if not os.access(config_path, os.R_OK):
            print(f"Config at '{config_path.as_posix()}' cannot be accessed.")
            return

    else:
        config_path = Path(config.DEFAULT_PATH)

    core.Visiomode(config_path)


if __name__ == '__main__':
    main()
