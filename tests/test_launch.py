#  This file is part of visiomode.
#  Copyright (c) 2022 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

from collections.abc import Generator

import pygame
import pytest

from visiomode import core


def test_launch(pygame_init) -> None:
    """Test the application starts as expected."""
    # Set up a timer to automatically close the application as soon as it enters
    # its main loop.
    pygame.time.set_timer(pygame.QUIT, 100)

    # Start the application
    core.Visiomode()
