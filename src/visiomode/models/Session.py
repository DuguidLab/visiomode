#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import datetime
import socket
import typing

import pydantic

import visiomode.__about__ as __about__
import visiomode.database as database
import visiomode.protocols as protocols
import visiomode._models.Animal as Animal
import visiomode._models.Trial as Trial


class Session(pydantic.BaseModel, arbitrary_types_allowed=True):
    session_id: str = pydantic.Field(default=None, repr=True)
    animal_id: str = pydantic.Field(repr=False)
    duration: pydantic.FiniteFloat = pydantic.Field(repr=False)
    experiment: str = pydantic.Field(repr=False)
    protocol: protocols.Protocol = pydantic.Field(repr=False)
    animal_metadata: typing.Optional[dict] = pydantic.Field(default={}, repr=False)
    device: str = pydantic.Field(default_factory=socket.gethostname, repr=False)
    complete: pydantic.StrictBool = pydantic.Field(default=False, repr=False)
    notes: str = pydantic.Field(default="", repr=False)
    spec: typing.Optional[dict] = pydantic.Field(default=None, repr=False)
    timestamp: pydantic.NaiveDatetime = pydantic.Field(
        default_factory=datetime.datetime.now, repr=True
    )
    trials: list[Trial.Trial] = pydantic.Field(default=[], repr=False)
    version: str = pydantic.Field(default=__about__.__version__, repr=False)

    def model_post_init(self, __context: typing.Any) -> None:
        self.session_id = self.generate_session_id()
        # Don't really know why but somehow by this point, Animal has turned from the
        # module into the class (at runtime, according to Pydantic)? Even Pycharm is
        # confused.
        self.animal_metadata = database.get_database(Animal).get_entry(self.animal_id)
        self.trials = self.protocol.trials

    @pydantic.field_serializer("protocol")
    def serialise_protocol(self, protocol: protocols.Protocol) -> str:
        return protocol.get_identifier()

    @pydantic.field_serializer("timestamp")
    def serialise_timestamp(self, timestamp: pydantic.NaiveDatetime) -> str:
        return timestamp.isoformat()

    def generate_session_id(self) -> str:
        timestamp = self.serialise_timestamp(self.timestamp)
        return (
            f"sub-{self.animal_id}_exp-{self.experiment}_date-"
            f"{timestamp.replace(':', '').replace('-', '').replace('.', '')}"
        )
