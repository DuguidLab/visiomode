/*
 * This file is part of visiomode.
 * Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

let socket = io.connect('/session');

let session_status;

socket.on('connect', function () {
    socket.emit('message', 'hello');
    console.log('connected');
});

socket.on('callback', function (msg) {
    console.log(msg);
});

socket.on('status', function(status) {
    session_status = status;
    if (session_status === 'active') {
        setStatusActive()
    } else if (session_status === 'inactive') {
        setStatusInactive()
    }
});

var form = document.getElementById('session-form');
var session_button = document.getElementById('session-control-btn');
var status_icon = document.getElementById('status-icon');
var status_text = document.getElementById('status-text');


session_button.onclick = function () {
    if (form.reportValidity() && (session_status === "inactive")) {
        // Start session
        let fields = [...form.getElementsByClassName('form-control')];
        let request = fields.reduce((_, x) => ({..._, [x.id]: x.value}), {});

        socket.emit('session_start', request);
        console.log('session start request');

        setStatusWaiting();
    } else if (session_status === "active") {
        // Stop session
        socket.emit('session_stop');
        console.log('session stop request');

        setStatusWaiting();
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


function setStatusWaiting () {
    session_button.className = "btn btn-light btn-block btn-lg";
    session_button.textContent = "Waiting...";

    status_icon.className = "fas fa-circle";
    status_text.childNodes[2].nodeValue = " Waiting";

    session_status = "inactive";

    // enable input fields
    let fields = form.getElementsByClassName('form-control');
    for (var i = 0; i < fields.length; i++)
    {
        fields[i].disabled = true;
    }
}