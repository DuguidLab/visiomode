"""Application data model classes."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import dataclasses
import datetime
import socket
import json
import typing
import copy
import logging
import operator

from visiomode import __about__, config


cfg = config.Config()


@dataclasses.dataclass
class Base:
    """Base model class."""

    def to_dict(self):
        """Get class instance attributes as a dictionary.

        Returns:
            Dictionary with class instance attributes.
        """
        return dataclasses.asdict(self)

    def to_json(self):
        """Get class instance attributes as JSON.

        Returns:
            JSON string with class instance attributes.
        """
        return json.dumps(self.to_dict())


@dataclasses.dataclass
class Response(Base):
    """
    Attributes:
       timestamp: String trial date and time (ISO format). Defaults to current date and time.
       name: Response type identifier (e.g. left, right or lever).
       pos_x: Float representing the touch position in the x-axis.
       pos_y: Float representing the touch position in the y-axis.
       dist_x: Float representing the distance travelled while touching the screen in the x-axis.
       dist_y: Float representing the distance travelled while touching the screen in the y-axis.
    """

    timestamp: str
    name: str
    pos_x: float
    pos_y: float
    dist_x: float
    dist_y: float


@dataclasses.dataclass
class Trial(Base):
    """Trial model class.

    Attributes:
        outcome: String descriptive of trial outcome, e.g. "correct", "incorrect", "no_response", "precued".
        iti: Float representing the "silent" time before the stimulus is presented in milliseconds.
        duration: Integer representing the duration of the touch in milliseconds.
        pos_x: Float representing the touch position in the x-axis.
        pos_y: Float representing the touch position in the y-axis.
        dist_x: Float representing the distance travelled while touching the screen in the x-axis.
        dist_y: Float representing the distance travelled while touching the screen in the y-axis.
        timestamp: String trial date and time (ISO format). Defaults to current date and time.
        correction: Boolean indicating whether or not trial is a correction trial. Defaults to False.
        response_time: Integer representing the time between stimulus presentation and response in seconds.
        sdt_type: Signal detection theory outcome classification (i.e. hit/miss/false_alarm/correct_rejection)
    """

    outcome: str
    iti: float
    response: Response
    timestamp: str = datetime.datetime.now().isoformat()
    correction: bool = False
    response_time: int = 0
    stimulus: dict = dataclasses.field(default_factory=dict)
    sdt_type: str = "NA"

    def __repr__(self):
        return "<Trial {}>".format(str(self.timestamp))


@dataclasses.dataclass
class Session(Base):
    """Session model class.

    Attributes:
        animal_id: String representing the animal identifier.
        experimenter_name: String representing the experimenter's name.
        experiment: A string holding the experiment identifier.
        task: An instance of the Task class.
        duration: Integer representing the session duration in minutes.
        complete: Boolean value indicating whether or not a session was completed
        timestamp: A string with the session start date and time (ISO format). Defaults to current date and time.
        notes: String with additional session notes. Defaults to empty string
        device: String hostname of the device running the session. Defaults to the hostname provided by the socket lib.
        trials: A mutable list of session trials; each trial is an instance of the Trial dataclass. Automatically populated using task.trials after class instantiation.
        animal_meta: A dictionary with animal metadata (see Animal class). Automatically populated using animal_id after class instantiation.
        experimenter_meta: A dictionary with experimenter metadata (see Experimenter class). Automatically populated using experimenter_name after class instantiation.
        version: Visiomode version this was generated with.
    """

    animal_id: str
    experimenter_name: str
    experiment: str
    duration: float
    task: None = None
    spec: dict = None
    complete: bool = False
    timestamp: str = datetime.datetime.now().isoformat()
    notes: str = ""
    device: str = socket.gethostname()
    trials: typing.List[Trial] = dataclasses.field(default_factory=list)
    animal_meta: dict = None
    experimenter_meta: dict = None
    version: str = __about__.__version__

    def __post_init__(self):
        self.animal_meta = Animal.get_animal(self.animal_id)
        self.experimenter_meta = Experimenter.get_experimenter(self.experimenter_name)
        self.trials = self.task.trials if self.task else []

    def to_dict(self):
        """Get class instance attributes as a dictionary.

        This method overrides the Base class to cast nested Trial objects under self.trials as dictionaries.

        Returns:
            Dictionary with class instance attributes.
        """
        instance = copy.copy(self)
        instance.trials = [trial.to_dict() for trial in self.trials if self.trials]
        instance.task = self.task.get_identifier() if self.task else None
        return dataclasses.asdict(instance)

    def save(self, path=cfg.data_dir):
        """Save session to json file."""
        session_id = (
            "sub-"
            + self.animal_id
            + "_exp-"
            + self.experiment
            + "_date-"
            + self.timestamp.replace(":", "").replace("-", "").replace(".", "")
        )
        f_path = path + os.sep + session_id + ".json"
        with open(f_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f)

        return session_id

    def __repr__(self):
        return "<Session {}>".format(str(self.timestamp))


@dataclasses.dataclass
class Animal(Base):
    """Animal model class.

    Attributes:
        animal_id: String representing the animal identifier.
        date_of_birth: String representing the animal date of birth (ISO format).
        sex: Character representing the animal's sex (M/F/U/O).
        species: String representing the animal's species. Use the latin name, eg. Mus musculus.
        genotype: String representing the animal's genotype. Defaults to empty string.
        description: String with additional animal notes. Defaults to empty string.
        rfid: String representing the animal's RFID tag. Defaults to empty string.
    """

    animal_id: str
    date_of_birth: str
    sex: str
    species: str
    genotype: str = ""
    description: str = ""
    rfid: str = ""

    def save(self):
        """Append animal to json database file."""
        path = cfg.db_dir + os.sep + "animals.json"

        if os.path.exists(path):
            with open(path, "r") as f:
                animals = json.load(f)
            # If the animal already exists, remove it and append the new one
            animals = [
                animal
                for animal in animals
                if not animal["animal_id"] == self.animal_id
            ]
            animals.append(self.to_dict())
            with open(path, "w") as f:
                json.dump(animals, f)
        else:
            with open(path, "w") as f:
                json.dump([self.to_dict()], f)

        return self.animal_id

    @classmethod
    def get_animal(cls, animal_id):
        """Get an animal from the database based on its ID."""
        path = cfg.db_dir + os.sep + "animals.json"

        if os.path.exists(path):
            with open(path, "r") as f:
                animals = json.load(f)
            for animal in animals:
                if animal["animal_id"] == animal_id:
                    return animal
        return None

    @classmethod
    def get_animals(cls):
        """Get all animals stored in the database.

        Returns:
            List of dictionaries with animal attributes.
        """
        path = cfg.db_dir + os.sep + "animals.json"

        if os.path.exists(path):
            with open(path, "r") as f:
                animals = json.load(f)
            return animals
        return []

    @classmethod
    def delete_animal(cls, animal_id):
        """Delete animal from database."""
        path = cfg.db_dir + os.sep + "animals.json"

        if os.path.exists(path):
            with open(path, "r") as f:
                animals = json.load(f)
            # If the animal exists, remove it
            animals = [
                animal for animal in animals if not animal["animal_id"] == animal_id
            ]
            with open(path, "w") as f:
                json.dump(animals, f)


@dataclasses.dataclass
class Experimenter(Base):
    """Experimenter model class.

    Attributes:
        experimenter_name (str): Name of the experimenter.
        laboratory_name (str): Name of the laboratory the experimenter works in.
        institution_name (str): Name of the institution the experimenter works for.
    """

    experimenter_name: str
    laboratory_name: str
    institution_name: str

    def save(self) -> None:
        """Append experimenter metadata to JSON database file."""
        database_path = f"{cfg.db_dir}{os.sep}experimenters.json"

        if not os.path.exists(database_path):
            experimenters = [self.to_dict()]
        else:
            with open(database_path, "r") as handle:
                experimenters = json.load(handle)

            # If experiment already exists, replace them
            experimenters = [
                experimenter
                for experimenter in experimenters
                if not experimenter["experimenter_name"].lower()
                == self.experimenter_name.lower()
            ]
            experimenters.append(self.to_dict())

        with open(database_path, "w") as handle:
            json.dump(experimenters, handle)

        return self.experimenter_name

    @classmethod
    def get_experimenter(cls, experimenter_name: str) -> typing.Optional[dict]:
        """Get an experimenter's metadata from the database based on their name.

        Returns:
            Dictionary with experimenter attributes if they have a record, None
            otherwise.
        """
        database_path = f"{cfg.db_dir}{os.sep}experimenters.json"

        if os.path.exists(database_path):
            with open(database_path, "r") as handle:
                experimenters = json.load(handle)

            for experimenter in experimenters:
                if (
                    experimenter["experimenter_name"].lower()
                    == experimenter_name.lower()
                ):
                    return experimenter

        return None

    @classmethod
    def get_experimenters(cls) -> list[dict]:
        """Return all experimenters from the database.

        Returns:
            List of dictionaries with experimenter attributes.
        """
        database_path = f"{cfg.db_dir}{os.sep}experimenters.json"

        experimenters = []
        if os.path.exists(database_path):
            with open(database_path, "r") as handle:
                experimenters = json.load(handle)

        return experimenters

    @classmethod
    def delete_experimenter(cls, experimenter_name: str) -> None:
        """Delete experimenter from the database.

        Args:
            experimenter_name (str): Name of the experimenter to delete.
        """
        database_path = f"{cfg.db_dir}{os.sep}experimenters.json"

        if not os.path.exists(database_path):
            return

        with open(database_path, "r") as handle:
            experimenters = json.load(handle)

        try:
            experimenters.pop(
                list(
                    map(operator.itemgetter("experimenter_name"), experimenters)
                ).index(experimenter_name)
            )
        except ValueError:
            logging.error(
                f"Tried removing '{experimenter_name}' from database "
                f"but it was not in it."
            )

        with open(database_path, "w") as handle:
            json.dump(experimenters, handle)
