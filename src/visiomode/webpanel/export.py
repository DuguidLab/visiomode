"""
File parsers for exporting session data.

Each export function takes a `session_path` argument, a string pointing to the
location of a stored session JSON file, and returns a string reference to the
converted file stored in Visiomode's cache directory.
"""

#  This file is part of visiomode.
#  Copyright (c) 2023 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

# Note that `pynwb` is imported inside its own function to save on startup time
import json
import os
from datetime import datetime

import pandas as pd

import visiomode.config as cfg

config = cfg.Config()


def to_nwb(session_path):
    # Delayed import to save on startup time
    import pynwb

    with open(session_path) as f:
        session = json.load(f)

    session_start_time = datetime.fromisoformat(session["timestamp"])

    experimenter_metadata = session["experimenter_meta"]
    if experimenter_metadata:
        nwbfile = pynwb.NWBFile(
            session_description="Visiomode {} behaviour".format(session.get("task")),
            identifier=session_path.split("/")[-1].replace(".json", ""),
            session_start_time=session_start_time,
            experiment_description=session.get("experiment"),
            experimenter=experimenter_metadata.get("experimenter_name"),
            lab=experimenter_metadata.get("laboratory_name"),
            institution=experimenter_metadata.get("institution_name"),
        )
    else:
        nwbfile = pynwb.NWBFile(
            session_description="Visiomode {} behaviour".format(session.get("task")),
            identifier=session_path.split("/")[-1].replace(".json", ""),
            session_start_time=session_start_time,
            experiment_description=session.get("experiment"),
        )

    nwbfile.subject = pynwb.file.Subject(subject_id=session["animal_id"])

    nwbfile.add_trial_column(name="stimulus", description="the visual stimuli during the trial")
    nwbfile.add_trial_column(name="cue_onset", description="when the stimulus came on")
    nwbfile.add_trial_column(name="response", description="trial response type (left, right, lever)")
    nwbfile.add_trial_column(name="response_time", description="response timestamp")
    nwbfile.add_trial_column(name="pos_x", description="response position in x-axis")
    nwbfile.add_trial_column(name="pos_y", description="response position in y-axis")
    nwbfile.add_trial_column(name="dist_x", description="response displacement in x-axis")
    nwbfile.add_trial_column(name="dist_y", description="response displacement in y-axis")
    nwbfile.add_trial_column(name="outcome", description="trial outcome")
    nwbfile.add_trial_column(name="correction", description="whether trial was a correction trial")
    nwbfile.add_trial_column(name="sdt_type", description="signal detection theory classification")

    for trial in _flatten_trials(session):
        nwbfile.add_trial(**trial)

    nwbfile.create_device(
        name=session["device"],
        description="Visiomode acquisition device version {}".format(session.get("version", "<0.5.0")),
        manufacturer="Duguid Lab",
    )

    subject_id = session.get("animal_id")
    session_date = session.get("timestamp").split("T")[0].replace("-", "")
    fname = f"sub-{subject_id}_ses-{session_date}_behavior.nwb"
    outpath = config.cache_dir + os.sep + fname
    with pynwb.NWBHDF5IO(outpath, "w") as io:
        io.write(nwbfile)

    return fname


def to_csv(session_path):
    with open(session_path) as f:
        session = json.load(f)

    df = pd.DataFrame(_flatten_trials(session))

    fname = session_path.split("/")[-1].replace(".json", ".csv")
    outpath = config.cache_dir + os.sep + fname
    df.to_csv(outpath)

    return fname


def _flatten_trials(session):
    session_start_time = datetime.fromisoformat(session["timestamp"])

    for trial in session.get("trials"):
        start_time = (datetime.fromisoformat(trial["timestamp"]) - session_start_time).total_seconds()

        stop_time = start_time + trial["iti"] + float(session["spec"].get("stimulus_duration", 10000)) / 1000
        if trial["response"].get("timestamp"):
            stop_time = (datetime.fromisoformat(trial["response"]["timestamp"]) - session_start_time).total_seconds()

        stimulus = trial["stimulus"].get("common_name") if trial["stimulus"] != "None" else "None"
        stimulus_attributes = trial["stimulus"].get("attributes") if trial["stimulus"] != "None" else "None"
        cue_onset = start_time + trial["iti"]

        response = trial["response"].get("name")
        response_time = trial["response_time"]

        pos_x = trial["response"].get("pos_x", 0)
        pos_y = trial["response"].get("pos_y", 0)
        dist_x = trial["response"].get("dist_x", 0)
        dist_y = trial["response"].get("dist_y", 0)

        sdt_type = trial.get("sdt_type", "unavailable")

        yield {
            "start_time": start_time,
            "stop_time": stop_time,
            "stimulus": stimulus,
            "cue_onset": cue_onset,
            "response": response,
            "response_time": response_time,
            "outcome": trial["outcome"],
            "correction": trial["correction"],
            "pos_x": pos_x,
            "pos_y": pos_y,
            "dist_x": dist_x,
            "dist_y": dist_y,
            "sdt_type": sdt_type,
            "stimulus_attributes": stimulus_attributes,
        }
