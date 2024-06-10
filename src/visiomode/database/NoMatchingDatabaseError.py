#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.


class NoMatchingDatabaseError(Exception):
    def __init__(self, provided_type: str) -> None:
        super().__init__(f"Cannot find a database for data type '{provided_type}'.")
