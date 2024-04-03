/*
 * This file is part of visiomode.
 * Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

let currentSettings = {};

let displaySettingsButton = document.getElementById('display-settings-btn');
let storageSettingsButton = document.getElementById('storage-settings-btn');
let clearCacheButton = document.getElementById('clear-cache-btn');
let deleteAllDataButton = document.getElementById('delete-all-data-btn');

let addAnimalButton = document.getElementById('add-animal-btn');


/// Display & storage settings

function loadSettings() {
    $.get("/api/settings", function (data) {
        currentSettings = data;
        document.getElementById("display-width").value = currentSettings.width;
        document.getElementById("display-height").value = currentSettings.height;
        document.getElementById("display-fps").value = currentSettings.fps;
        document.getElementById("display-fullscreen").value = currentSettings.fullscreen.toString();
        document.getElementById("storage-path").value = currentSettings.data_dir;
    });
}

function updateSettings() {
    console.log(JSON.stringify(currentSettings));
    $.ajax({
        type: 'POST',
        url: "/api/settings",
        data: JSON.stringify({
            type: "update",
            data: currentSettings,
        }),
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            $("#changeDisplaySettings").modal("hide");
        }
    });
}

displaySettingsButton.onclick = function () {
    currentSettings.width = Number(document.getElementById("display-width").value);
    currentSettings.height = Number(document.getElementById("display-height").value);
    currentSettings.fps = Number(document.getElementById("display-fps").value);
    currentSettings.fullscreen = document.getElementById("display-fullscreen").value === "true";

    updateSettings();
}

storageSettingsButton.onclick = function () {
    currentSettings.data_dir = document.getElementById("storage-path").value;

    updateSettings();
}

loadSettings();


/// Animals

function addAnimal() {
    let animalId = document.getElementById("animal-id").value;
    let animalDob = document.getElementById("animal-dob").value;
    let animalSex = document.getElementById("animal-sex").value;
    let animalSpecies = document.getElementById("animal-species").value;
    let animalGenotype = document.getElementById("animal-genotype").value;
    let animalDescription = document.getElementById("animal-description").value;
    let animalRFID = document.getElementById("animal-rfid").value;

    $.ajax({
        type: 'POST',
        url: "/api/animals",
        data: JSON.stringify({
            type: "add",
            data: {
                id: animalId,
                dob: animalDob,
                sex: animalSex,
                species: animalSpecies,
                genotype: animalGenotype,
                description: animalDescription,
                rfid: animalRFID,
            },
        }),
        dataType: "json",
        contentType: "application/json",
        success: function (data) {
            $("#addAnimal").modal("hide");
        }
    });
}

addAnimalButton.onclick = function () {
    addAnimal();
}

function exportAnimals() {
    // Export animals as CSV
    $.get("/api/animals", function (data) {
        animals = data.animals;
        let replacer = (key, value) => value === null ? '' : value
        let header = Object.keys(animals[0])
        let csv = [
            header.join(','), // header row first
            ...animals.map(row => header.map(
                fieldName => JSON.stringify(row[fieldName], replacer)).join(','))
        ].join('\r\n');
        let csvExport = new Blob([csv], {type: "text/csv"});
        let url = window.URL.createObjectURL(csvExport);
        let a = document.createElement('a');
        a.href = url;
        a.download = 'animals.csv';
        a.click();
    });
}
