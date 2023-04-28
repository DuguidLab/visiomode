/*
 * This file is part of visiomode.
 * Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
 * Distributed under the terms of the MIT Licence.
 */

let currentSettings;

function loadSettings() {
    $.get("/api/settings", function (data) {
        console.log(data);
        currentSettings = data;
        document.getElementById("display-width").value = currentSettings.width;
        document.getElementById("display-height").value = currentSettings.height;
        document.getElementById("display-fps").value = currentSettings.fps;
        document.getElementById("display-fullscreen").value = currentSettings.fullscreen.toString();
        document.getElementById("storage-path").value = currentSettings.data_dir;
    });
}

loadSettings();
