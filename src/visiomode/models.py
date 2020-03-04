"""Database connection handling module"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
from dataclasses import dataclass, field
from typing import List


@dataclass
class Trial:
    """Trial model class.

    Attributes:
        timestamp: String trial date and time (ISO format).
        outcome: String descriptive of trial outcome, e.g. "hit", "miss", "pre-cued".
        iti: Integer representing the "silent" time before the stimulus is presented in milliseconds.
        reaction_time: Integer representing the time between stimulus presentation and response in milliseconds.
        duration: Integer representing the duration of the touch in milliseconds.
        pos_x: Float representing the touch position in the x-axis.
        pos_y: Float representing the touch position in the y-axis.
        dist_x: Float representing the distance travelled while touching the screen in the x-axis.
        dist_y: Float representing the distance travelled while touching the screen in the y-axis.
    """
    timestamp: str
    outcome: str
    iti: int
    reaction_time: int
    duration: int
    pos_x: float
    pos_y: float
    dist_x: float
    dist_y: float

    def __repr__(self):
        return "<Trial {}>".format(str(self.timestamp))


@dataclass
class Session:
    """Session model class.

    Attributes:
        status: A string holding the current session status, i.e. active or inactive.
        timestamp: A string with the session start date and time (ISO format).
        animal_id: String representing the animal identifier.
        experiment: A string holding the experiment identifier.
        protocol: A string holding the protocol identifier.
        duration: Integer representing the session duration in minutes.
        experiment_ref: String representing the experiment identifier.
        device: String hostname of the device running the session
        notes: String with additional session notes.
        trials: A mutable list of session trials; each trial is an instance of the Trial dataclass.
    """
    status: str
    timestamp: str
    animal_id: str
    experiment: str
    protocol: str
    duration: int
    device: str
    notes: str
    trials: List[Trial] = field(default_factory=list)

    def __repr__(self):
        return "<Session {}>".format(str(self.timestamp))
