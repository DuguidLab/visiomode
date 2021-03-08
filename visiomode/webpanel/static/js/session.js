/*
 * This file is part of visiomode.
 * Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */
let form = document.getElementById('session-form');
let session_button = document.getElementById('session-control-btn');
let status_icon = document.getElementById('status-icon');
let status_text = document.getElementById('status-text');

session_status = "inactive"; // debug

session_button.onclick = function () {
    if (form.reportValidity() && (session_status !== "active")) {
        // Start session
        let fields = [...form.getElementsByClassName('form-control')];
        let request = fields.reduce((_, x) => ({..._, [x.id]: x.value}), {});
        console.log(JSON.stringify(request))

        $.ajax({
            type: 'POST',
            url: "/api/session",
            data: JSON.stringify(request),
            dataType: "json",
            contentType: "application/json"
        });

        console.log('session start request');

        setStatusWaiting();
    } else if (session_status === "active") {
        // Stop session
        console.log('session stop request');

        setStatusWaiting();
    }
    return false;
};


function setStatusActive() {
    console.log("Session is running");

    session_button.className = "btn btn-danger btn-block btn-lg";
    session_button.textContent = "Stop";

    status_icon.className = "fas fa-circle text-success";
    status_text.childNodes[2].nodeValue = " Running";

    // disable input fields
    let fields = form.getElementsByClassName('form-control');
    for (let i = 0; i < fields.length; i++) {
        fields[i].disabled = true;
    }
}


function setStatusInactive() {
    console.log("No active session");

    session_button.className = "btn btn-success btn-block btn-lg";
    session_button.textContent = "Start";

    status_icon.className = "fas fa-circle text-danger";
    status_text.childNodes[2].nodeValue = " Not Running";

    // enable input fields
    let fields = form.getElementsByClassName('form-control');
    for (let i = 0; i < fields.length; i++) {
        fields[i].disabled = false;
    }
}


function setStatusWaiting() {
    session_button.className = "btn btn-light btn-block btn-lg";
    session_button.textContent = "Waiting...";

    status_icon.className = "fas fa-circle text-warning";
    status_text.childNodes[2].nodeValue = " Waiting";

    // enable input fields
    let fields = form.getElementsByClassName('form-control');
    for (let i = 0; i < fields.length; i++) {
        fields[i].disabled = true;
    }
}


/// Dynamic form updates for protocol selection

// load protocol options on select
protocol_selector = document.getElementById('protocol');

protocol_selector.onchange = function () {
    $.get("/api/protocol-form/" + protocol_selector.value).done(function (data) {
        $('#protocol-options').html(data);
    })
}

protocol_selector.onchange();

setStatusInactive();
