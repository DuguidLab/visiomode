/*
 * This file is part of visiomode.
 * Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

var session = io.connect('/session');

session.on('connect', function () {
    session.emit('message', 'hello');
    console.log('hi!');
});

session.on('callback', function (msg) {
    console.log(msg);
});