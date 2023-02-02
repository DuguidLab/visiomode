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
        console.log(sessions);

        let table = document.getElementById("sessionsTable");
        sessions.forEach(session => {
            console.log(session.animal_id)
            let row = table.insertRow();
            let date = row.insertCell(0);
            date.innerHTML = session.date;
            let animal_id = row.insertCell(1);
            animal_id.innerHTML = session.animal_id;
            let protocol = row.insertCell(2);
            protocol.innerHTML = session.protocol;
            let downloadButton = row.insertCell(3);
        });
    });
