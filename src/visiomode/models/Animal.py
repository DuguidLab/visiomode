#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import typing

import pydantic


class Animal(pydantic.BaseModel):
    animal_id: str = pydantic.Field(repr=True)
    date_of_birth: pydantic.PastDatetime = pydantic.Field(repr=False)
    sex: typing.Literal["U", "M", "F", "O"] = pydantic.Field(repr=False)
    species: typing.Literal[
        "Mus musculus", "Rattus norvegicus", "Other"
    ] = pydantic.Field(repr=False)
    description: str = pydantic.Field(default="", repr=False)
    genotype: str = pydantic.Field(default="", repr=False)
    rfid: str = pydantic.Field(default="", repr=False)
