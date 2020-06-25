"""Database connection handling module"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import dataclasses
import datetime
import socket
import json
import typing


@dataclasses.dataclass
class Base:
    """Base model class."""

    def to_dict(self):
        """Returns class instance attributes as a dictionary."""
        return dataclasses.asdict(self)

    def to_json(self, path=None):
        """Returns class instance attributes as JSON."""
        return json.dumps(self.to_dict())


@dataclasses.dataclass
class Trial(Base):
    """Trial model class.

    Attributes:
        outcome: String descriptive of trial outcome, e.g. "hit", "miss", "pre-cued".
        iti: Float representing the "silent" time before the stimulus is presented in milliseconds.
        reaction_time: Integer representing the time between stimulus presentation and response in milliseconds.
        duration: Integer representing the duration of the touch in milliseconds.
        pos_x: Float representing the touch position in the x-axis.
        pos_y: Float representing the touch position in the y-axis.
        dist_x: Float representing the distance travelled while touching the screen in the x-axis.
        dist_y: Float representing the distance travelled while touching the screen in the y-axis.
        timestamp: String trial date and time (ISO format). Defaults to current date and time.
    """

    outcome: str
    iti: float
    reaction_time: int
    duration: int
    pos_x: float
    pos_y: float
    dist_x: float
    dist_y: float
    timestamp: str = datetime.datetime.now().isoformat()

    def __repr__(self):
        return "<Trial {}>".format(str(self.timestamp))


@dataclasses.dataclass
class Session(Base):
    """Session model class.

    Attributes:
        animal_id: String representing the animal identifier.
        experiment: A string holding the experiment identifier.
        protocol: A string holding the protocol identifier.
        duration: Integer representing the session duration in minutes.
        complete: Boolean value indicating whether or not a session was completed
        timestamp: A string with the session start date and time (ISO format). Defaults to current date and time.
        notes: String with additional session notes. Defaults to empty string
        device: String hostname of the device running the session. Defaults to the hostname provided by the socket lib.
        trials: A mutable list of session trials; each trial is an instance of the Trial dataclass.
    """

    animal_id: str
    experiment: str
    protocol: str
    duration: float
    complete: bool = False
    timestamp: str = datetime.datetime.now().isoformat()
    notes: str = ""
    device: str = socket.gethostname()
    trials: typing.List[Trial] = dataclasses.field(default_factory=list)

    def to_dict(self):
        """Returns class instance attributes as a dictionary.

        This method overrides the Base class to cast nested Trial objects under self.trials as dictionaries.
        """
        self.trials = [trial.to_dict() for trial in self.trials if self.trials]
        return dataclasses.asdict(self)

    def save(self, path):
        """Save session to json file."""
        session_id = (
            "sub-"
            + self.animal_id
            + "_exp-"
            + self.experiment
            + "_date-"
            + self.timestamp.replace(":", "").replace("-", "").replace(".", "")
        )
        f_path = path + os.sep + session_id
        with open(f_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f)

    def __repr__(self):
        return "<Session {}>".format(str(self.timestamp))
