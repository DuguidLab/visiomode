"""Webapp factory"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import logging
import threading

import flask
import visiomode.config as cfg
import visiomode.protocols as protocols
import visiomode.stimuli as stimuli
import visiomode.webpanel.api as api


def create_app(action_q=None, log_q=None):
    """Flask app factory

    Returns:
        Flask app object
    """
    config = cfg.Config()

    app = flask.Flask(__name__)
    app.config.from_mapping({"SECRET_KEY": config.flask_key, "DEBUG": config.debug})

    # ensure that instance dir exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError as exc:
        logging.warning(
            "Could not create instance directory ({}) - {}".format(
                app.instance_path, str(exc)
            )
        )

    @app.route("/")
    def index():
        """Visiomode Dashboard."""
        return flask.render_template(
            "index.html",
            tasks=protocols.Task.get_children(),
            presentations=protocols.Presentation.get_children(),
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
        return flask.render_template("404.html")

    app.add_url_rule(
        "/api/session",
        view_func=api.SessionAPI.as_view("session_api", action_q, log_q),
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/api/protocol-form/<protocol_id>",
        view_func=api.ProtocolAPI.as_view("protocol_api"),
        methods=["GET"],
    )

    app.add_url_rule(
        "/api/stimulus-form/<stimulus_id>",
        view_func=api.StimulusAPI.as_view("stimulus_api"),
        methods=["GET"],
    )

    app.add_url_rule(
        "/api/device", view_func=api.DeviceAPI.as_view("device_api"), methods=["POST"]
    )

    app.add_url_rule(
        "/api/hostname",
        view_func=api.HostnameAPI.as_view("hostname_api"),
        methods=["GET"],
    )

    app.add_url_rule(
        "/api/history", view_func=api.HistoryAPI.as_view("history_api"), methods=["GET"]
    )

    app.add_url_rule(
        "/api/download/<filetype>/<filename>",
        view_func=api.DownloadAPI.as_view("download_api"),
        methods=["GET"],
    )

    return app


def runserver(action_q, log_q, threaded=False):
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


if __name__ == "__main__":
    runserver()
