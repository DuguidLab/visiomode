/*
 * This file is part of visiomode.
 * Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

let table = document.getElementById("experimentersTableData");
let updateExperimenterButton = document.getElementById('update-experimenter-btn');
let deleteExperimenterButton = document.getElementById('delete-experimenter-btn');
let experimenters = [];


function loadExperimenters() {
    fetch("/api/experimenters")
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            experimenters = data.experimenters;
            experimenters.sort(function (a, b) {
                if (a.experimenter_name < b.experimenter_name) {
                    return -1;
                } else if (a.experimenter_name > b.experimenter_name) {
                    return 1;
                }
                return 0;
            });

            let experimentersTableData = document.getElementById("experimentersTableData");
            experimentersTableData.innerHTML = "";
            experimenters.forEach(experimenter => {
                let row = experimentersTableData.insertRow();
                let experimenter_name = row.insertCell(0);
                experimenter_name.innerHTML = experimenter.experimenter_name;
                let laboratory_name = row.insertCell(1);
                laboratory_name.innerHTML = experimenter.laboratory_name;
                let institution_name = row.insertCell(2);
                institution_name.innerHTML = experimenter.institution_name;
            });
        });
}

table.onclick = function (event) {
    let experimenter_name = event.target.parentNode.cells[0].innerHTML;
    let selected_experimenter = experimenters.find(element => element.experimenter_name === experimenter_name);
    console.log(selected_experimenter);
    $("#updateExperimenter").modal();
    document.getElementById("experimenter-name").value = selected_experimenter.experimenter_name;
    document.getElementById("previous-experimenter-name").value = selected_experimenter.experimenter_name;
    document.getElementById("laboratory-name").value = selected_experimenter.laboratory_name;
    document.getElementById("institution-name").value = selected_experimenter.institution_name;
}

function updateExperimenter() {
    let experimenterName = document.getElementById("experimenter-name").value;
    let previousExperimenterName = document.getElementById("previous-experimenter-name").value;
    let laboratoryName = document.getElementById("laboratory-name").value;
    let institutionName = document.getElementById("institution-name").value;

    $.ajax({
        type: 'POST',
        url: "/api/experimenters",
        data: JSON.stringify({
            type: "update",
            data: {
                experimenter_name: experimenterName,
                previous_experimenter_name: previousExperimenterName,
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
    let experimenterName = document.getElementById("experimenter-name").value;
    $.ajax({
        type: 'POST',
        url: "/api/experimenters",
        data: JSON.stringify({
            type: "delete",
            data: {
                experimenter_name: experimenterName,
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
