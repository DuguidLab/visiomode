"""Webapp factory"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Copyright (c) 2024 Olivier Delree <odelree@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import logging
import os
import threading

import flask

import visiomode.config as cfg
from visiomode import stimuli, tasks
from visiomode.webpanel import api


def create_app(action_q=None, log_q=None):
    """Flask app factory

    Returns:
        Flask app object
    """
    config = cfg.Config()

    app = flask.Flask(__name__, instance_path=os.path.abspath(config.instance_dir))
    app.config.from_mapping({"SECRET_KEY": config.flask_key, "DEBUG": config.debug})

    # ensure that instance dir exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as exc:
        logging.warning(f"Could not create instance directory ({app.instance_path}) - {exc!s}")

    @app.route("/")
    def index():
        """Visiomode Dashboard."""
        return flask.render_template(
            "index.html",
            tasks=tasks.Task.get_children(),
            stimuli=stimuli.Stimulus.get_children(),
        )

    @app.route("/history")
    def history():
        """Session history page."""
        return flask.render_template("history.html")

    @app.route("/settings")
    def settings():
        """Settings page."""
        return flask.render_template("settings.html")

    @app.route("/settings-animals")
    def settings_animals():
        """Animals view/edit page."""
        return flask.render_template("settings-animals.html")

    @app.route("/settings-experimenters")
    def settings_experimenters():
        """Experimenters view/edit page."""
        return flask.render_template("settings-experimenters.html")

    @app.route("/help")
    def docs():
        """Help / documentation page."""
        return flask.render_template("help.html")

    @app.route("/about")
    def about():
        """About page."""
        return flask.render_template("about.html")

    @app.errorhandler(404)
    def page_not_found(e):
        """404 page not found redirect."""
        logging.warning(msg=f"Request returned 404 - {e}")
        return flask.render_template("404.html")

    app.add_url_rule(
        "/api/session",
        view_func=api.SessionAPI.as_view("session_api", action_q, log_q),
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/api/task-form/<task_id>",
        view_func=api.TaskAPI.as_view("task_api"),
        methods=["GET"],
    )

    app.add_url_rule(
        "/api/stimulus-form/<stimulus_id>",
        view_func=api.StimulusAPI.as_view("stimulus_api"),
        methods=["GET"],
    )

    app.add_url_rule("/api/device", view_func=api.DeviceAPI.as_view("device_api"), methods=["POST"])

    app.add_url_rule(
        "/api/hostname",
        view_func=api.HostnameAPI.as_view("hostname_api"),
        methods=["GET"],
    )

    app.add_url_rule(
        "/api/history",
        view_func=api.HistoryAPI.as_view("history_api"),
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/api/download/<filetype>/<filename>",
        view_func=api.DownloadAPI.as_view("download_api"),
        methods=["GET"],
    )

    app.add_url_rule(
        "/api/settings",
        view_func=api.SettingsAPI.as_view("settings_api"),
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/api/animals",
        view_func=api.AnimalsAPI.as_view("animals_api"),
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/api/experimenters",
        view_func=api.ExperimentersAPI.as_view("experimenters_api"),
        methods=["GET", "POST"],
    )

    return app


def runserver(action_q, log_q, *, threaded=False):
    """Runs the flask app in an integrated server."""
    app = create_app(action_q, log_q)
    if threaded:
        thread = threading.Thread(
            target=app.run,
            kwargs={"use_reloader": False, "debug": True, "host": "0.0.0.0"},
            daemon=True,
        )
        return thread.start()
    app.run(host="0.0.0.0", debug=True)
