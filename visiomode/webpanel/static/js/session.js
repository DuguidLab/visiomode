/*
 * This file is part of visiomode.
 * Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */
let form = document.getElementById('session-form');

let session_button = document.getElementById('session-control-btn');

let status_icon = document.getElementById('status-icon');
let status_text = document.getElementById('status-text');
let progressBar = document.getElementById("session-progress");

let logList = document.getElementById('log-list');

let session_status;

setTimeout(getStatus, 100)

session_button.onclick = function () {
    if (form.reportValidity() && (session_status !== "active")) {
        // Start session
        let fields = [...form.getElementsByClassName('form-control')];
        let request = fields.reduce((_, x) => ({..._, [x.id]: x.value}), {});
        console.log(JSON.stringify(request))

        $.ajax({
            type: 'POST',
            url: "/api/session",
            data: JSON.stringify({
                type: "start",
                data: request,
            }),
            dataType: "json",
            contentType: "application/json"
        });

        console.log('session start request');

        setStatusWaiting();

        setTimeout(getStatus, 100)
    } else if (session_status === "active") {
        // Stop session
        $.ajax({
            type: "POST",
            url: "/api/session",
            data: JSON.stringify({
                type: "stop"
            }),
            dataType: "json",
            contentType: "application/json"
        })

        console.log('session stop request');

        setStatusWaiting();

        let now = new Date(Date.now()).toISOString();
        let stopTimeEvent = document.createElement('li');
        stopTimeEvent.innerHTML = "Session stopped at " + now;
        logList.prepend(stopTimeEvent);

        setTimeout(getStatus, 200)
    }
    return false;
};


function getStatus() {
    $.get("/api/session", function (data) {
        session_status = data.status;
        if (session_status === "active") {
            let session_data = JSON.parse(data.data);
            setStatusActive();

            console.log(session_data)

            document.getElementById('animal_id').value = session_data.animal_id;
            document.getElementById('experiment').value = session_data.experiment;
            document.getElementById('protocol').value = session_data.protocol;
            document.getElementById('duration').value = session_data.duration;

            logList.innerHTML = "" // Clear contents
            for (let i = session_data.trials.length - 1; i >= 0; i--) {
                let event = document.createElement('li');
                event.innerHTML = "<em>" + session_data.trials[i].timestamp + ": </em>" + session_data.trials[i].outcome;
                logList.appendChild(event);
            }
            logList.append(document.createElement('li').innerHTML = "Session started at " + session_data.timestamp);

            // update progress bar
            totalTimeMs = (parseInt(session_data.duration) * 60000);
            timeLeftMs = totalTimeMs - (Date.now() - Date.parse(session_data.timestamp));
            timeLeftMin = timeLeftMs / 60000;
            progressBarWidth = (1 - (timeLeftMs / totalTimeMs)) * 100;
            console.log(progressBarWidth);
            console.log(progressBar);
            progressBar.style.width = progressBarWidth.toString() + "%";
            progressBar.innerHTML = timeLeftMin.toFixed(1).toString() + " min left";

            if (timeLeftMin <= 0) {
                let now = new Date(Date.now()).toISOString();
                let finishTimeEvent = document.createElement('li');
                finishTimeEvent.innerHTML = "Session stopped at " + now;
                logList.prepend(finishTimeEvent);
            }

        } else if (session_status === "inactive") {
            setStatusInactive();

        } else {
            setStatusWaiting();
        }
    })
}

let status_interval = setInterval(getStatus, 4000);

function setStatusActive() {
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
    session_button.className = "btn btn-success btn-block btn-lg";
    session_button.textContent = "Start";

    status_icon.className = "fas fa-circle text-danger";
    status_text.childNodes[2].nodeValue = " Not Running";

    progressBar.style.width = "0%";
    progressBar.innerHTML = "";


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
