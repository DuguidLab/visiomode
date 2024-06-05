/*
 * This file is part of visiomode.
 * Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
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
            row.style.cssText = "cursor: pointer;";
            let date = row.insertCell(0);
            date.innerHTML = session.date;
            let animal_id = row.insertCell(1);
            animal_id.innerHTML = session.animal_id;
            let protocol = row.insertCell(2);
            protocol.innerHTML = session.protocol;
            let downloadButton = row.insertCell(3);
            downloadButton.innerHTML = `
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
            `;
            let session_id = row.insertCell(-1);
            session_id.innerHTML = session.session_id;
            row.cells[4].classList.add("d-none");  // Don't display this column
        });
    });

let table = document.getElementById("sessionsTableData");

table.onclick = async function (event) {
    let session_id = event.target.closest("tr").cells[event.target.parentNode.cells.length - 1].innerHTML;
    let session = await fetch(`/api/history?session_id=${session_id}`)
        .then((response) => response.json())
        .then((data) => data.session);

    $("#viewSession").modal();

    document.getElementById("animal-id").value = session?.animal_id ?? "";
    document.getElementById("duration").value = session?.duration ?? "";
    document.getElementById("experiment-id").value = session?.experiment ?? "";
    document.getElementById("experimenter-name").value = session?.experimenter_name ?? "";
    document.getElementById("protocol").value = session?.protocol ?? "";
    document.getElementById("timestamp").value = session?.timestamp ?? "";
    document.getElementById("trial-count").value = session?.trials?.length ?? "";
    document.getElementById("notes").value = session?.notes ?? "";
}
