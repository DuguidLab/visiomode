"""Configuration & fixtures for pytest."""

import queue
from collections.abc import Generator
from datetime import datetime

import pygame
import pytest

import visiomode.config as cfg
from visiomode import core, models, stimuli, tasks, webpanel

core.load_plugins()


@pytest.fixture(scope="module")
def pygame_init() -> Generator[None, None, None]:
    """Ensure pygame is initialised before running tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(scope="module")
def test_action_q() -> Generator[queue.Queue, None, None]:
    """Queue for action messages."""
    yield queue.Queue()


@pytest.fixture(scope="module")
def test_log_q() -> Generator[queue.Queue, None, None]:
    """Queue for log messages."""
    yield queue.Queue()


@pytest.fixture()
def webapp(test_action_q, test_log_q):
    app = webpanel.create_app(test_action_q, test_log_q)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def config(tmp_path):
    test_config = cfg.Config()
    test_data_dir = tmp_path / "visiomode_data"
    test_data_dir.mkdir()
    test_config.data_dir = str(test_data_dir)
    test_cache_dir = tmp_path / "visiomode_data/cache"
    test_cache_dir.mkdir()
    test_config.cache_dir = str(test_cache_dir)
    test_config.save(str(tmp_path / ".visiomode.json"))

    return test_config


@pytest.fixture()
def client(webapp, config):
    return webapp.test_client()


@pytest.fixture()
def runner(webapp):
    return webapp.test_cli_runner()


@pytest.fixture()
def session(config):
    """Generate test session data and save in the expected path."""

    session = models.Session(
        animal_id="testanimal",
        experimenter_name="test",
        experiment="test_exp",
        duration=30,
        spec={"stimulus_duration": 10000},
        timestamp=str(datetime.now().isoformat()),
    )
    session.trials.extend(
        [
            models.Trial(
                outcome="correct",
                iti=5.0,
                response=models.Response(
                    timestamp=str(datetime.now().isoformat()),
                    name="lever",
                    pos_x=0.0,
                    pos_y=0.0,
                    dist_x=0.0,
                    dist_y=0.0,
                ),
                response_time=1.0,
                sdt_type="hit",
                stimulus="None",
            ),
            models.Trial(
                outcome="incorrect",
                iti=5.0,
                response=models.Response(
                    timestamp=str(datetime.now().isoformat()),
                    name="lever",
                    pos_x=0.0,
                    pos_y=0.0,
                    dist_x=0.0,
                    dist_y=0.0,
                ),
                response_time=1.5,
                sdt_type="false_alarm",
                stimulus="None",
            ),
        ]
    )
    return session.save(config.data_dir)


@pytest.fixture()
def animal():
    animal = models.Animal(
        animal_id="testanimal",
        date_of_birth=str(datetime.now().isoformat()),
        sex="M",
        species="Mus musculus",
        genotype="wt",
    )
    return animal.save()


@pytest.fixture()
def experimenter():
    experimenter = models.Experimenter(
        experimenter_name="testexperimenter",
        laboratory_name="duguid lab",
        institution_name="UoE",
    )
    return experimenter.save()
