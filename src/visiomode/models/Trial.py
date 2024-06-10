#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import datetime
import typing

import pydantic

from visiomode._models.Response import Response


class Trial(pydantic.BaseModel):
    timestamp: pydantic.NaiveDatetime = pydantic.Field(
        default_factory=datetime.datetime.now, repr=True
    )
    iti: pydantic.FiniteFloat = pydantic.Field(repr=False)
    outcome: typing.Literal[
        "correct", "incorrect", "precued", "no_response"
    ] = pydantic.Field(repr=False)
    response: typing.Optional[Response] = pydantic.Field(repr=False)
    correction: pydantic.StrictBool = pydantic.Field(default=False, repr=False)
    response_time: pydantic.FiniteFloat = pydantic.Field(default=0.0, repr=False)
    sdt_type: typing.Literal[
        "hit", "miss", "false_alarm", "correct_rejection", "NA"
    ] = pydantic.Field(default="NA", repr=False)
    stimulus: dict = pydantic.Field(default={}, repr=False)

    @pydantic.field_serializer("timestamp")
    def serialise_timestamp(self, timestamp: pydantic.NaiveDatetime) -> str:
        return timestamp.isoformat()
