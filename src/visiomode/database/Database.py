#  This file is part of visiomode.
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import json
import os
import typing

import pydantic

from visiomode.config import Config
from visiomode.database.CorruptedDatabaseError import CorruptedDatabaseError
from visiomode.database.WrongDataTypeError import WrongDataTypeError


class Database:
    _database_entry_type: type[pydantic.BaseModel]
    _database_file: str
    _database_path: str

    _in_memory_contents: typing.Optional[
        dict[str, typing.Union[str, list[dict]]]
    ] = None

    def __init__(
        self,
        database_entry_type: type[pydantic.BaseModel],
        database_file: str,
        default_uniqueness_key: str,
    ) -> None:
        self._database_entry_type = database_entry_type
        self._database_file = database_file

        self._initialise(default_uniqueness_key)

    @property
    def uniqueness_key(self) -> typing.Optional[str]:
        if self._in_memory_contents is not None:
            return self._in_memory_contents["uniqueness_key"]
        return None

    @property
    def entries(self) -> typing.Optional[list[dict]]:
        if self._in_memory_contents is not None:
            return self._in_memory_contents["entries"]
        return None

    def save_entry(self, entry: pydantic.BaseModel) -> None:
        # Check entry data type is compatible with database (i.e. exact type)
        if type(entry) is not self._database_entry_type:
            raise WrongDataTypeError(str(type(entry)), str(self._database_entry_type))

        # Check the entry does have the uniqueness key as an attribute
        entry_unique_value = getattr(entry, self.uniqueness_key, None)
        if entry_unique_value is None:
            raise ValueError(
                f"Invalid entry provided. It does not have a value for uniqueness key"
                f"'{self.uniqueness_key}'."
            )
        serialised_entry = self.serialise_model(entry)

        # Append entry to database or replace matching entry based on uniqueness key
        replaced_entry = False
        for database_index, database_entry in enumerate(self.entries):
            if entry_unique_value == database_entry[self.uniqueness_key]:
                self.entries[database_index] = serialised_entry
                replaced_entry = True
                break

        if not replaced_entry:
            self.entries.append(serialised_entry)

        self.dump_database()

    def get_entry(self, entry_id: str) -> typing.Optional[dict]:
        for database_entry in self.entries:
            if database_entry[self.uniqueness_key] == entry_id:
                print(database_entry)
                return database_entry

        return None

    def get_entries(self) -> list[dict]:
        return self.entries

    def get_filtered_entries(self, filter_key: str, filter_value: str) -> list[dict]:
        filtered_entries = []

        for entry in self.entries:
            if entry.get(filter_key) == filter_value:
                filtered_entries.append(entry)

        return filtered_entries

    def delete_entry(self, entry_id: str) -> None:
        deleted_an_entry = False
        for database_index, database_entry in enumerate(self.entries):
            if database_entry[self.uniqueness_key] == entry_id:
                self.entries.pop(database_index)
                deleted_an_entry = True
                break

        if deleted_an_entry:
            self.dump_database()

    def dump_database(self) -> None:
        with open(self._database_path, "w") as database_handle:
            json.dump(self._in_memory_contents, database_handle)

    def update_uniqueness_key(self, new_key: str) -> None:
        self.validate_database(new_key)
        self._in_memory_contents["uniqueness_key"] = new_key

        self.dump_database()

    def reload_database(self):
        self.dump_database()

        self._initialise(self.uniqueness_key)

    def validate_database(
        self, validation_uniqueness_key: typing.Optional[str] = None
    ) -> None:
        if validation_uniqueness_key is None:
            if self._in_memory_contents.get("uniqueness_key") is None or not isinstance(
                self.uniqueness_key, str
            ):
                raise CorruptedDatabaseError(str(self._database_entry_type))
            validation_uniqueness_key = self.uniqueness_key

        values = []

        database_entries = self._in_memory_contents.get("entries")
        if database_entries is None or not isinstance(database_entries, list):
            raise CorruptedDatabaseError(str(self._database_entry_type))

        for database_entry in database_entries:
            database_entry_unique_value = database_entry.get(validation_uniqueness_key)
            if database_entry_unique_value is None:
                raise KeyError(
                    f"Validation of the database failed with key '{validation_uniqueness_key}'. "
                    f"At least one entry does not have a value for the given key."
                )

            if database_entry_unique_value in values:
                raise KeyError(
                    f"Validation of the database failed with key '{validation_uniqueness_key}'. "
                    f"At least one duplicated entry was found."
                )

            values.append(database_entry_unique_value)

    def _initialise(self, default_uniqueness_key: typing.Optional[str] = None):
        # Retrieve up-to-date path based on current config
        self._database_path = f"{Config().db_dir}{os.sep}{self._database_file}"

        if os.path.exists(self._database_path):
            try:
                self._load_database()
            except json.JSONDecodeError:
                raise CorruptedDatabaseError(str(self._database_entry_type))
            except KeyError as key_error:
                raise Exception(
                    "Initialisation of the database from disk failed."
                ) from key_error
        else:
            if default_uniqueness_key is None:
                raise KeyError(
                    "Cannot initialise database without either a default uniqueness key"
                    " or an already initialised database on disk."
                )
            self._in_memory_contents = {
                "uniqueness_key": default_uniqueness_key,
                "entries": [],
            }
            self.dump_database()

    def _load_database(self) -> None:
        with open(self._database_path, "r") as database_handle:
            self._in_memory_contents = json.load(database_handle)
        self.validate_database()

    @staticmethod
    def serialise_model(model: pydantic.BaseModel) -> dict:
        return json.loads(model.model_dump_json())
