"""Database connection handling module"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import flask_sqlalchemy as sql


db = sql.SQLAlchemy()


def init_app(app):
    """Initialises application for use with SQLAlchemy.

    Must be called when application object is created.

    Args:
        app: Flask `app` object.
    """
    db.init_app(app)


def init_db():
    """Creates all database tables."""
    db.drop_all()
    db.create_all()


class Session(db.Model):
    """Session model class.

    Attributes:
        id: Auto-incrementing integer unique identifier.
        timestamp: Session date and time (ISO format).
        animal_id: String representing the animal identifier.
        length: Integer representing the session duration in minutes.
        experiment_ref: String representing the experiment identifier.
        notes: Additional notes.
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    animal_id = db.Column(db.String(100), nullable=False)
    length = db.Column(db.Integer, nullable=False)
    experiment_ref = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return "<Session {}>".format(str(self.timestamp))


class Trial(db.Model):
    """Trial model class.

    Attributes:
        id: Auto-incrementing integer unique identifier.
        timestamp: Trial date and time (ISO format).
        outcome: String descriptive of trial outcome, e.g. "hit", "miss", "pre-cued".
        iti: Integer representing the "silent" time before the stimulus is presented in milliseconds.
        reaction_time: Integer representing the time between stimulus presentation and response in milliseconds.
        pos_x: Float representing the touch position in the x-axis.
        pos_y: Float representing the touch position in the y-axis.
        duration: Integer representing the duration of the touch in milliseconds.
        dist_x: Float representing the distance travelled while touching the screen in the x-axis.
        dist_y: Float representing the distance travelled while touching the screen in the y-axis.
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    outcome = db.Column(db.String(80))
    iti = db.Column(db.Integer)  # unit: milliseconds
    reaction_time = db.Column(db.Integer)  # unit: milliseconds
    pos_x = db.Column(db.Float)
    pos_y = db.Column(db.Float)
    duration = db.Column(db.Integer)  # unit: milliseconds
    dist_x = db.Column(db.Float)
    dist_y = db.Column(db.Float)

    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    session = db.relationship('Session', backref=db.backref('trials', lazy=True))

    def __repr__(self):
        return "<Trial {} for Session {}>".format(str(self.timestamp), str(self.session_id))
