#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import typing

import pydantic


class Response(pydantic.BaseModel, validate_assignment=True):
    timestamp: pydantic.PastDatetime
    name: typing.Literal["left", "right", "leverpush", "none"]
    pos_x: pydantic.FiniteFloat
    pos_y: pydantic.FiniteFloat
    dist_x: pydantic.FiniteFloat
    dist_y: pydantic.FiniteFloat

    @pydantic.field_serializer("timestamp")
    def serialise_timestamp(self, timestamp: pydantic.PastDatetime) -> str:
        return timestamp.isoformat()
