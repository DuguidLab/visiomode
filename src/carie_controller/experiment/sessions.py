"""Experiment session classes"""
import os
import json
import logging
import datetime


class Session():
    """Experiment session class"""
    def __init__(self, mouse, session, task, save_dir):
        # Sanitise session so that ids < 10 are e.g. 01 instead of just 1
        self.session = '0' + str(session) if int(session) < 10 else session
        self.mouse = str(mouse)
        self.task = str(task)
        self.session_id = "sub-mouse{mouse}_ses-{session}_task-{task}".format(
            mouse=self.mouse,
            session=self.session,
            task=self.task,
        )
        self.filename = self.session_id + ".json"
        self.path = str(save_dir) + os.sep + self.filename

        self.trials = []
        self.start_time = None
        self.end_time = None


    def start(self):
        logging.info("Session %s started", self.session_id)


    def end(self):
        return


    def add_trial(self, trial):
        self.trials.append(trial)


    def save(self):
        return


    def load(self):
        return


class Trial():
    def __init__(self, args):
        return

    @classmethod
    def from_json(cls, data):
        return
