#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import logging
import os
import pathlib
import tempfile
import typing

import pytest

import visiomode.config as config


@pytest.fixture()
def set_up_and_tear_down() -> None:
    # Backup previous config before toying with the module
    if config.Config._instance:
        pre_test_config_path = config.Config().config_path
        config.Config().save()
    else:
        pre_test_config_path = None
    previous_working_directory = os.getcwd()

    # Nuke the config
    config.Config._instance = None

    # Move into a temporary directory for test
    temporary_directory = tempfile.TemporaryDirectory()
    os.chdir(temporary_directory.name)

    # Run test
    yield

    # Reset the state as we found it
    config.Config._instance = None
    os.chdir(previous_working_directory)
    if pre_test_config_path:  # if not, the config hadn't been initialised before test
        config.Config(pre_test_config_path)

    temporary_directory.cleanup()


def assert_clear_path(path_attribute: str, function: typing.Callable) -> None:
    """Tests `path` is properly cleared."""
    config_ = config.Config()

    sentinel_path = (
        getattr(config_, path_attribute)
        + os.sep
        + str(id(f"assert_clear_{path_attribute}"))
    )
    pathlib.Path(sentinel_path).touch()

    function()

    assert not os.path.exists(sentinel_path)
    assert os.path.exists(getattr(config_, path_attribute))


def test_singleton(set_up_and_tear_down) -> None:
    """Test that we get the same instance with subsequent calls."""
    first_call_config = config.Config()
    second_call_config = config.Config()

    assert first_call_config is second_call_config


def test_directory_creation(set_up_and_tear_down) -> None:
    """Test that we create the proper files mentioned in the config."""
    config_ = config.Config()
    assert os.path.exists(config_.data_dir)
    assert os.path.exists(config_.cache_dir)
    assert os.path.exists(config_.db_dir)


def test_all_attributes_initialised(set_up_and_tear_down) -> None:
    """Test that we create all the attributes in the default config."""
    config_ = config.Config()
    for key in config.DEFAULT_CONFIG.keys():
        assert hasattr(config_, key)


def test_save_and_reload(set_up_and_tear_down) -> None:
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
        assert getattr(backup_config, key) == getattr(new_config, key)


def test_malformed_config_load(caplog, set_up_and_tear_down) -> None:
    """Test that a malformed config is corrected on load."""
    config_ = config.Config()
    del config_.fullscreen
    config_.save()

    config.Config._instance = None
    with caplog.at_level(logging.WARNING):
        config.Config()
    assert (
        "Config is malformed, it does not have attribute 'fullscreen'. "
        "Using default value." in caplog.text
    )


def test_clear_cache(set_up_and_tear_down) -> None:
    """Test clearing cache does delete and recreate cache directory."""
    assert_clear_path("cache_dir", config.clear_cache)


def test_clear_db(set_up_and_tear_down) -> None:
    """Test clearing database does delete and recreate database directory."""
    assert_clear_path("db_dir", config.clear_db)


def test_clear_data(set_up_and_tear_down) -> None:
    """Test clearing data does delete and recreate data directory."""
    assert_clear_path("data_dir", config.clear_data)
