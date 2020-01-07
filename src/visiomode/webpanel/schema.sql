/*
 * This file is part of visiomode.
 * Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */
DROP TABLE IF EXISTS session;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS protocol;

CREATE TABLE protocol ( --TODO add protocol experimental parameters
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    animal_id TEXT NOT NULL,
    experiment_ref TEXT,
    notes TEXT,
    FOREIGN KEY (protocol_id) references protocol (id)
);

CREATE TABLE trial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    outcome TEXT,
    iti REAL,
    rt REAL,
    pos_x REAL,
    pos_y REAL,
    duration REAL,
    dist_x REAL,
    dist_y REAL,
    FOREIGN KEY (session_id) references session (id)
);