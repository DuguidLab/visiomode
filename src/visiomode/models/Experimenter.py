#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import pydantic


class Experimenter(pydantic.BaseModel):
    experimenter_name: str = pydantic.Field(repr=True)
    laboratory_name: str = pydantic.Field(repr=False)
    institution_name: str = pydantic.Field(repr=False)
