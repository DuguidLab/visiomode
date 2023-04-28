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
        contentType: "application/json"
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
