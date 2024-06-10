#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import typing

import visiomode.models as models
from visiomode.database.CorruptedDatabaseError import CorruptedDatabaseError
from visiomode.database.Database import Database
from visiomode.database.NoMatchingDatabaseError import NoMatchingDatabaseError
from visiomode.database.WrongDataTypeError import WrongDataTypeError


# Defaults are presented in tuples of:
#    - Database file
#    - Database default uniqueness key
DATABASE_DEFAULTS = {
    models.Animal: ("animals.json", "animal_id"),
    models.Experimenter: ("experimenters.json", "experimenter_name"),
    models.Session: ("sessions.json", "session_id"),
}
DatabaseSupported = typing.Union[
    type[models.Animal], type[models.Experimenter], type[models.Session]
]


_managed_databases = dict()


def get_database(database_item_type: DatabaseSupported) -> Database:
    if database_item_type not in _managed_databases.keys():
        if database_item_type not in DATABASE_DEFAULTS.keys():
            raise NoMatchingDatabaseError(str(database_item_type))

        database_defaults = DATABASE_DEFAULTS[database_item_type]
        database = Database(database_item_type, *database_defaults)
        _managed_databases[database_item_type] = database
    else:
        database = _managed_databases[database_item_type]

    return database
