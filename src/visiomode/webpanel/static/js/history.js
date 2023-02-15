/*
 * This file is part of visiomode.
 * Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

fetch("/api/history")
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        let sessions = data.sessions;
        sessions.sort((b, a) => new Date(a.date).getTime() - new Date(b.date).getTime());

        let sessionsTableData = document.getElementById("sessionsTableData");
        sessions.forEach(session => {
            console.log(session.animal_id)
            let row = sessionsTableData.insertRow();
            let date = row.insertCell(0);
            date.innerHTML = session.date;
            let animal_id = row.insertCell(1);
            animal_id.innerHTML = session.animal_id;
            let protocol = row.insertCell(2);
            protocol.innerHTML = session.protocol;
            let downloadButton = row.insertCell(3);
            btn = document.createElement('input');
            downloadButton.innerHTML = `
            <div class="dropdown">
                <button
                    class="btn btn-primary btn-sm dropdown-toggle"
                    type="button" id="dropdownMenuButton" data-toggle="dropdown"
                    aria-haspopup="true" aria-expanded="false">
                Download
                </button>
                <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                    <a class="dropdown-item" href="/api/download/json/${session.fname}">JSON</a>
                    <a class="dropdown-item" href="/api/download/csv/${session.fname}">CSV</a>
                    <a class="dropdown-item" href="/api/download/nwb/${session.fname}">NWB</a>
                </div>
            </div>
            `;
        });
    });
