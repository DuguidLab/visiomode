#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.


class WrongDataTypeError(Exception):
    def __init__(self, provided_type: str, database_type: str) -> None:
        super().__init__(
            f"Provided data type is not compatible with database type "
            f"('{provided_type}' vs '{database_type}')."
        )
