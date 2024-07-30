import os
from datetime import datetime, timedelta

import flask
from flask_jwt_extended import JWTManager, create_access_token

FALLBACK_LOGIN_PATH = os.path.join(os.path.dirname(__file__), "fallback_login.html")


class PasswordProtectedHttpServer:
    config: dict

    tokens = {
        # token: expiration
    }

    def init(config: dict):
        config["root"] = os.path.abspath(config["root"])
        if config["login-filepath"] != "":
            config["login-filepath"] = os.path.abspath(config["login-filepath"])

        PasswordProtectedHttpServer.config = config

    def run():
        app = flask.Flask(os.path.split(PasswordProtectedHttpServer.config["root"])[1])
        app.secret_key = PasswordProtectedHttpServer.config["secret-key"]
        JWTManager(app)

        @app.route("/login", methods=["POST"])
        def login():
            mimetype = flask.request.mimetype
            if mimetype == "application/x-www-form-urlencoded":
                form = {k: v for k, v in flask.request.form.items()}
            elif mimetype == "multipart/form-data":
                form = dict(flask.request.form)
            elif mimetype == "application/json":
                form = flask.request.json
            else:
                form = flask.request.data.decode()

            data = form

            if data.get("password") == PasswordProtectedHttpServer.config["password"]:
                access_token = create_access_token(identity=data.get("username"))
                PasswordProtectedHttpServer.tokens[
                    access_token
                ] = datetime.now() + timedelta(
                    minutes=PasswordProtectedHttpServer.config[
                        "token-expiration-in-minutes"
                    ]
                )

                response = flask.make_response(flask.redirect(flask.url_for("home")))
                response.set_cookie("access_token", access_token)

                return response, 302

            return flask.redirect(flask.url_for("home")), 302

        @app.route("/", defaults=dict(filename=None))
        @app.route("/<path:filename>", methods=["GET", "POST"])
        def home(filename):

            token = PasswordProtectedHttpServer.tokens.get(
                flask.request.cookies.get("access_token")
            )

            if PasswordProtectedHttpServer.config["password"] != "" and (
                token is None or datetime.now() > token
            ):

                # if no specific file is requested, return user to home
                if filename is not None:
                    return flask.redirect(flask.url_for("home"))

                # if no login-filepath is set, the fallback login page is returned
                if PasswordProtectedHttpServer.config["login-filepath"] == "":
                    return flask.send_file(FALLBACK_LOGIN_PATH)

                return flask.send_file(
                    PasswordProtectedHttpServer.config["login-filepath"]
                )
            
            if not PasswordProtectedHttpServer.config["allow-dotfiles"] and filename is not None and filename.startswith("."):
                return flask.redirect(flask.url_for("home"))

            filename = (
                filename
                or PasswordProtectedHttpServer.config["index-filepath-from-root"]
            )
            if flask.request.method == "GET":
                return (
                    flask.send_from_directory(
                        PasswordProtectedHttpServer.config["root"], filename
                    ),
                    200,
                )

        app.run(
            host=PasswordProtectedHttpServer.config["host"],
            port=PasswordProtectedHttpServer.config["port"],
        )
