/*
 * This file is part of visiomode.
 * Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

var socket = io.connect('/session');

socket.on('connect', function () {
    socket.emit('message', 'hello');
    console.log('hi!');
});

socket.on('callback', function (msg) {
    console.log(msg);
});

var form = document.getElementById('session-form');
var session_button = document.getElementById('session-control-btn');
var status_icon = document.getElementById('status-icon');
var status_text = document.getElementById('status-text');

var session_status = "inactive"; // TODO read from Redis

session_button.onclick = function () {
    if (form.reportValidity() && (session_status === "inactive")) {
        // Start session
        socket.emit('message', 'start!');
        console.log('session start request');
        setStatusActive();
    } else if (session_status === "active") {
        // Stop session
        socket.emit('message', 'stop');
        console.log('session stop request');
        setStatusInactive();
    }
    return false;
};


function setStatusActive () {
    console.log("Session is running");
    session_button.className = "btn btn-danger btn-block btn-lg";
    session_button.textContent = "Stop";
    status_icon.className = "fas fa-circle text-success";
    status_text.childNodes[2].nodeValue = " Running";
    session_status = "active";

    // disable input fields
    let fields = form.getElementsByClassName('form-control');
    for (var i = 0; i < fields.length; i++)
    {
        fields[i].disabled = true;
    }
}


function setStatusInactive () {
    console.log("No active session");
    session_button.className = "btn btn-success btn-block btn-lg";
    session_button.textContent = "Start";
    status_icon.className = "fas fa-circle text-danger";
    status_text.childNodes[2].nodeValue = " Not Running";
    session_status = "inactive";

    // enable input fields
    let fields = form.getElementsByClassName('form-control');
    for (var i = 0; i < fields.length; i++)
    {
        fields[i].disabled = false;
    }
}