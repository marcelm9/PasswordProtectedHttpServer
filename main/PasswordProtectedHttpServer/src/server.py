import os

import flask
from werkzeug.middleware.proxy_fix import ProxyFix

FALLBACK_LOGIN_PATH = os.path.join(os.path.dirname(__file__), "fallback_login.html")


class PasswordProtectedHttpServer:
    config: dict
    trusted_ips: list[str] = []

    def init(config: dict):
        config["root"] = os.path.abspath(config["root"])
        if config["login-filepath"] != "":
            config["login-filepath"] = os.path.abspath(config["login-filepath"])

        PasswordProtectedHttpServer.config = config

    def run():
        app = flask.Flask(os.path.split(PasswordProtectedHttpServer.config["root"])[1])
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

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
            ip = flask.request.remote_addr

            if data.get("password") == PasswordProtectedHttpServer.config["password"]:
                if ip not in PasswordProtectedHttpServer.trusted_ips:
                    PasswordProtectedHttpServer.trusted_ips.append(
                        flask.request.remote_addr
                    )
                    print(f"Added trusted ip: {flask.request.remote_addr}")
                    print(f"All trusted ips: {PasswordProtectedHttpServer.trusted_ips}")
                response = flask.make_response(flask.redirect(flask.url_for("home")))
                return response, 302

            return flask.redirect(flask.url_for("home")), 302

        @app.route("/", defaults=dict(filename=None))
        @app.route("/<path:filename>", methods=["GET"])
        def home(filename):
            ip = flask.request.remote_addr
            if PasswordProtectedHttpServer.config["password"] != "" and (
                ip not in PasswordProtectedHttpServer.trusted_ips
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

            if (
                not PasswordProtectedHttpServer.config["allow-dotfiles"]
                and filename is not None
                and filename.startswith(".")
            ):
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
