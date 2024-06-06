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

let currentSessionId;

const canvasContext = document.getElementById("trialsChart");
let trialsChart;
let currentChartSessionId;

table.onclick = async function (event) {
    currentSessionId = event.target.closest("tr").cells[event.target.parentNode.cells.length - 1].innerHTML;
    let session = await fetch(`/api/history?session_id=${currentSessionId}`)
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

    // Avoid unnecessarily redrawing the chart when reopening the same modal
    if (currentSessionId !== currentChartSessionId) {
        trialsChart?.destroy();

        if (session?.trials?.length) {
            trialsChart = createChart(canvasContext, [
                session.trials.filter((obj) => obj.outcome === "correct").length,
                session.trials.filter((obj) => obj.outcome === "incorrect").length,
                session.trials.filter((obj) => obj.outcome === "precued").length,
                session.trials.filter((obj) => obj.outcome === "no_response").length,
            ]);
        } else {
            trialsChart = createChart(canvasContext, []);
        }

        currentChartSessionId = currentSessionId;
    }
}

function createChart(canvas, session_data) {
    return new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["Correct", "Incorrect", "Precued", "No Response"],
            datasets: [{
                label: "# of Trials",
                data: session_data,
                borderWidth: 1
            }]
        },
        options: {
            devicePixelRatio: 3,
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: "right",
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
            }
        },
    });
}

let deleteSessionDataSpan = document.getElementById("deleteSessionDataSpan");
let deleteSessionDataButton = document.getElementById("deleteSessionDataButton");
let buttonAnimation;
let buttonAnimationDuration = 1000;

function generateLoadingButtonKeyFrames() {
    let keyFrames = [];
    for (let i = 0; i <= 100; i++) {
        keyFrames.push({background: `linear-gradient(to right, #bb2d3b 0%, #bb2d3b ${i}%, #DC3545 ${i}%, #DC3545 100%)`});
    }
    return keyFrames;
}

deleteSessionDataSpan.onmouseover = () => {
    // Create the animation if it's the first hover event
    if (!buttonAnimation) {
        buttonAnimation = deleteSessionDataButton.animate(generateLoadingButtonKeyFrames(), {
            duration: buttonAnimationDuration,
        });
        buttonAnimation.onfinish = () => {
            // `onfinish` triggers when the animation gets back to the start
            // if the user stops hovering, so only enable the button if it
            // reached the "forward end"
            if (buttonAnimation.currentTime === buttonAnimationDuration) {
                deleteSessionDataButton.removeAttribute("disabled");
            }
        };
    }
    buttonAnimation.playbackRate = 1;  // Resume animation forward
}
deleteSessionDataSpan.onmouseout = () => {
    deleteSessionDataButton.setAttribute("disabled", "");
    buttonAnimation.playbackRate = -2;  // Reverse animation at twice the speed
}

deleteSessionDataButton.onclick = () => {
    deleteSessionData(currentSessionId);
    // Reset the animation
    buttonAnimation.playbackRate = -1;
    buttonAnimation.finish();
};

function deleteSessionData(sessionId) {
    $.ajax({
        type: "POST",
        url: "/api/history",
        data: JSON.stringify({
            type: "delete",
            data: {sessionId},
        }),
        dataType: "json",
        contentType: "application/json",
        success: function () {
            // Close all the modals
            $('.modal').modal('hide');
            // Remove the row for the deleted session
            $("#sessionsTableData").find("td:contains('" + sessionId + "')").closest("tr").remove();
        }
    });
}
