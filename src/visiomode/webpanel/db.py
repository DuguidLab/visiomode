"""Database connection handling module"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import click
import flask
import flask.cli as fcli
import sqlite3 as sql


def get_db():
    """Fetch a database instance object for the current request.

    Returns:
        Request database object.
    """
    if 'db' not in flask.g:
        flask.g.db = sql.connect(
            flask.current_app.config['DATABASE'],
            detect_types=sql.PARSE_DECLTYPES
        )
        flask.g.db.row_factory = sql.Row

        return flask.g.db


def close_db(e=None):
    """Close an instantiated database connection.

    Args:
        e:
    """
    db = flask.g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Initialise the database.

    This will delete ALL data in the database if it already exists.
    """
    db = get_db()

    with flask.current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
