#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import logging
import os
import tempfile
import time
import typing
import unittest

import visiomode.config as config


class ConfigTest(unittest.TestCase):
    pre_test_config_path: typing.Optional[str]
    previous_working_directory: str
    temporary_directory: tempfile.TemporaryDirectory

    def setUp(self) -> None:
        # Backup previous config before toying with the module
        if config.Config._instance:
            self.pre_test_config_path = config.Config().config_path
            config.Config().save()
        else:
            self.pre_test_config_path = None
        self.previous_working_directory = os.getcwd()

        # Nuke the config
        config.Config._instance = None

        # Move into a temporary directory for test
        self.temporary_directory = tempfile.TemporaryDirectory()
        os.chdir(self.temporary_directory.name)

    def tearDown(self) -> None:
        # Reset the state as we found it
        config.Config._instance = None
        os.chdir(self.previous_working_directory)
        if (
            self.pre_test_config_path
        ):  # if not, the config hadn't been initialised before test
            config.Config(self.pre_test_config_path)

        self.temporary_directory.cleanup()

    def assert_not_equal_ctime(self, attribute: str, function: typing.Callable) -> None:
        """
        Test that ctimes of `attribute` are different before and after call to
        `function`.
        """
        config_ = config.Config()
        first_ctime = os.stat(getattr(config_, attribute)).st_ctime

        # Artificial sleep so that ctime can be different when recreating the
        # directory. Without it, the ctime is the same, possibly because the
        # deletion and creation coalesce somehow?
        time.sleep(0.001)

        function()

        second_ctime = os.stat(getattr(config_, attribute)).st_ctime

        self.assertNotEqual(first_ctime, second_ctime)

    def test_singleton(self) -> None:
        """Test that we get the same instance with subsequent calls."""
        first_call_config = config.Config()
        second_call_config = config.Config()

        self.assertTrue(first_call_config is second_call_config)

    def test_directory_creation(self) -> None:
        """Test that we create the proper files mentioned in the config."""
        config_ = config.Config()
        self.assertTrue(os.path.exists(config_.data_dir))
        self.assertTrue(os.path.exists(config_.cache_dir))
        self.assertTrue(os.path.exists(config_.db_dir))

    def test_all_attributes_initialised(self) -> None:
        """Test that we create all the attributes in the default config."""
        config_ = config.Config()
        for key in config.DEFAULT_CONFIG.keys():
            self.assertTrue(hasattr(config_, key))

    def test_save_and_reload(self) -> None:
        """
        Test that reloading a config from file gives us the same config back, at least
        with regards to the required attributes.
        """
        backup_config = config.Config()
        backup_config.fullscreen = not backup_config.fullscreen
        backup_config.save(".custom-config.json")

        config.Config._instance = None

        new_config = config.Config(".custom-config.json")

        for key in config.DEFAULT_CONFIG:
            self.assertTrue(getattr(backup_config, key) == getattr(new_config, key))

    def test_malformed_config_load(self) -> None:
        """Test that a malformed config is corrected on load."""
        config_ = config.Config()
        del config_.fullscreen
        config_.save()

        config.Config._instance = None
        with self.assertLogs(level=logging.WARNING) as log_context_manager:
            config.Config()
        self.assertEqual(
            log_context_manager.output,
            [
                "WARNING:root:Config is malformed, it does not have attribute "
                "'fullscreen'. Using default value."
            ],
        )

    def test_clear_cache(self) -> None:
        """Test clearing cache does delete and recreate cache directory."""
        self.assert_not_equal_ctime("cache_dir", config.clear_cache)

    def test_clear_db(self) -> None:
        """Test clearing database does delete and recreate database directory."""
        self.assert_not_equal_ctime("db_dir", config.clear_db)

    def test_clear_data(self) -> None:
        """Test clearing data does delete and recreate data directory."""
        self.assert_not_equal_ctime("data_dir", config.clear_data)


if __name__ == "__main__":
    unittest.main()
