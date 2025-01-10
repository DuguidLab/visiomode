/*
 * This file is part of visiomode.
 * Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

let table = document.getElementById("protocolsTableData");
let updateExperimenterButton = document.getElementById('update-protocol-btn');
let deleteExperimenterButton = document.getElementById('delete-protocol-btn');
let protocols = [];


function loadExperimenters() {
    fetch("/api/protocols")
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            protocols = data.protocols;
            protocols.sort(function (a, b) {
                if (a.protocol_name < b.protocol_name) {
                    return -1;
                } else if (a.protocol_name > b.protocol_name) {
                    return 1;
                }
                return 0;
            });

            let protocolsTableData = document.getElementById("protocolsTableData");
            protocolsTableData.innerHTML = "";
            protocols.forEach(protocol => {
                console.log(protocol.protocol_spec.target)
                let row = protocolsTableData.insertRow();
                let protocol_name = row.insertCell(0);
                protocol_name.innerHTML = protocol.name;
                let task = row.insertCell(1);
                task.innerHTML = protocol.protocol_spec.task;
                let duration = row.insertCell(2);
                duration.innerHTML = protocol.protocol_spec.duration;
                let response_device = row.insertCell(3);
                response_device.innerHTML = protocol.protocol_spec.response_device;
                let stimuli = row.insertCell(4);
                stimuli.innerHTML = [protocol.protocol_spec.target, protocol.protocol_spec.distractor].join(", ");
                let protocol_id = row.insertCell(5);
                protocol_id.innerHTML = protocol.id;
            });
        });
}

table.onclick = function (event) {
    let protocol_id = event.target.parentNode.cells[5].innerHTML;
    let selected_protocol = protocols.find(element => element.id === protocol_id);
    console.log(selected_protocol);
    $("#updateProtocol").modal();
    document.getElementById("protocol-name").value = selected_protocol.protocol_name;
    document.getElementById("laboratory-name").value = selected_protocol.laboratory_name;
    document.getElementById("institution-name").value = selected_protocol.institution_name;
}

task_selector = document.getElementById('task');

task_selector.onchange = function () {
    $.get("/api/task-form/" + task_selector.value).done(function (data) {
        $('#task-options').html(data);
    })
}

task_selector.onchange();

function updateProtocol() {
    let protocolName = document.getElementById("protocol-name").value;
    let laboratoryName = document.getElementById("laboratory-name").value;
    let institutionName = document.getElementById("institution-name").value;

    $.ajax({
        type: 'POST',
        url: "/api/protocols",
        data: JSON.stringify({
            type: "update",
            data: {
                protocol_name: protocolName,
                previous_protocol_name: previousExperimenterName,
                laboratory_name: laboratoryName,
                institution_name: institutionName,
            },
        }),
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.log(data);
            loadExperimenters();
            $("#updateExperimenter").modal("toggle")
        }
    });
}

updateExperimenterButton.onclick = function () {
    updateExperimenter();
}


deleteExperimenterButton.onclick = function () {
    let protocolName = document.getElementById("protocol-name").value;
    $.ajax({
        type: 'POST',
        url: "/api/protocols",
        data: JSON.stringify({
            type: "delete",
            data: {
                protocol_name: protocolName,
            },
        }),
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            console.log(data);
            loadExperimenters();
            $("#updateExperimenter").modal("toggle")
        }
    });
}

loadExperimenters();
