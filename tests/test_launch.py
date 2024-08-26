#  This file is part of visiomode.
#  Copyright (c) 2022 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pygame
import unittest

import visiomode.core as core


class AppLaunch(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Ensure pygame is initialised
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        # Ensure to clean up pygame
        pygame.quit()

    @staticmethod
    def test_launch() -> None:
        """Test the application starts as expected."""
        # Set up a timer to automatically close the application as soon as it enters
        # its main loop.
        pygame.time.set_timer(pygame.event.Event(pygame.QUIT), 100)

        # Start the application
        core.Visiomode()


if __name__ == "__main__":
    unittest.main()
