"""Webapp factory"""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.

import os
import logging
import threading

import flask
import flask_socketio as sock
import visiomode.config as cfg
import visiomode.messaging as messaging
import visiomode.protocols as protocols
import visiomode.stimuli as stimuli
import visiomode.webpanel.session as sess


def create_app():
    """Flask app factory

    Returns:
        Flask app object
    """
    config = cfg.Config()
    rds = messaging.RedisClient()

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

    # Set active session status to inactive
    rds.set_status(messaging.INACTIVE)

    @app.route("/")
    def index():
        """Dashboard page."""
        return flask.render_template("index.html")

    @app.route("/session")
    def session():
        """Session page."""
        return flask.render_template(
            "session.html",
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

    @app.route("/api/protocol-form/<protocol_id>")
    def get_protocol_form(protocol_id):
        protocol = protocols.get_protocol(protocol_id)
        if protocol:
            return flask.render_template(
                protocol.get_form(), stimuli=list(stimuli.Stimulus.get_children()),
            )
        return "No Additional Options"

    @app.route("/api/stimulus-form/<stimulus_id>")
    def get_stimulus_form(stimulus_id):
        idx = flask.request.args.get(
            "idx"
        )  # used to differentiate multiple stimuli on same page
        stimulus = stimuli.get_stimulus(stimulus_id)
        if stimulus and stimulus.form_path:
            return flask.render_template(stimulus.get_form(), idx=idx)
        return "No Additional Options"

    @app.errorhandler(404)
    def page_not_found(e):
        """404 page not found redirect."""
        return flask.render_template("404.html")

    return app


def runserver(threaded=False):
    """Runs the flask app in an integrated server."""
    app = create_app()
    socketio = sock.SocketIO(app)
    socketio.on_namespace(sess.SessionNamespace("/session"))
    if threaded:
        thread = threading.Thread(
            target=socketio.run,
            args=(app,),
            kwargs={"use_reloader": False, "debug": True},
            daemon=True,
        )
        return thread.start()
    socketio.run(app, debug=True)


if __name__ == "__main__":
    runserver()
