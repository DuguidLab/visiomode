#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.


class CorruptedDatabaseError(Exception):
    def __init__(self, database_type: str):
        super().__init__(
            f"Parsing of '{database_type}' database failed. "
            f"It is most likely corrupted."
        )
