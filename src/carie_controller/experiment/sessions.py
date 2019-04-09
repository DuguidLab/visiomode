"""Experiment session classes"""
import os
import json
import logging
import datetime


class Session():
    """Experiment session data class.

    Each instance is an experimental session and holds all relevant information
    including mouse ID.

    Attributes:
        mouse: A string MouseID as it appears in the animal records, e.g. "3801295940".
        session: An integer representing which session this is in sequence, e.g. 2 (if second).
        task: A string of the task ID, e.g. openfield.
        timestamp: A string with the datetime in ISO format.
        session_id: A string generated using the session ID, mouse ID and task ID.
        filename: A string that's basically the session_id with '.json' stuck at its end.
        trials: A list of trial data as dictionaries.
    """
    def __init__(self, mouse, session, task, timestamp):
        """Inits Session with mouse, session, task and timestamp details."""
        # Sanitise session so that ids < 10 are e.g. 01 instead of just 1
        self.session = '0' + str(session) if int(session) < 10 else str(session)
        self.mouse = str(mouse)
        self.task = str(task)
        self.timestamp = str(timestamp)
        self.session_id = "sub-mouse{mouse}_ses-{session}_task-{task}".format(
            mouse=self.mouse,
            session=self.session,
            task=self.task,
        )
        self.filename = self.session_id + ".json"
        self.trials = []

    def add_trial(self, trial):
        if isinstance(trial, Trial):
            self.trials.append(trial.to_dict())
        elif isinstance(trial, dict):
            self.trials.append(trial)
        else:
            raise TypeError(
                "Expected dictionary or 'Trial' object, not {}".format(type(trial)))

    def save(self, data_dir):
        self.load(data_dir)
        # path and filename are superfluous for json file
        session = vars(self).pop('filename')
        path = str(data_dir) + os.sep + self.filename
        with open(path, 'w') as f:
            json.dump(session, f)

    def load(self, data_dir):
        path = str(data_dir) + os.sep + self.filename
        if not os.path.isfile(path):
            return None
        with open(path, 'r') as f:
            self.trials = json.load(f)['trials']

    @classmethod
    def from_json(cls, raw):
        return cls(**json.loads(raw))

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            return cls(**json.load(f))

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Trial():
    __trial_keys = [
        'x', 'y', 'duration', 'touch_force', 'timestamp',
        'x_distance', 'y_distance', 'event', 'time_iso'
    ]

    def __init__(self, **kwargs):
        for key in kwargs:
            if key == 'time_iso':
                self.__setattr__(key, datetime.datetime.now().isoformat())
                continue
            if key in self.__trial_keys:
                self.__setattr__(key, kwargs[key])

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_json(cls, raw):
        return cls()
