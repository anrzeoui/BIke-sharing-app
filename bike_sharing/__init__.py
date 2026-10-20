"""Bike Sharing App: presentation, service and SQLite persistence layers."""

import os
import secrets
from datetime import timedelta
from pathlib import Path

from flask import Flask

from . import db, views


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "bike_sharing.db"),
        SECRET_KEY=os.environ.get("BIKE_SECRET_KEY"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("BIKE_HTTPS") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config is not None:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config["SECRET_KEY"]:
        # Reuse a local key across restarts; do not commit it to version control.
        secret_path = Path(app.instance_path) / "secret_key"
        try:
            descriptor = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(descriptor, "w") as secret_file:
                secret_file.write(secrets.token_hex(32))
        app.config["SECRET_KEY"] = secret_path.read_text().strip()
    db.init_app(app)
    app.register_blueprint(views.blueprint)
    with app.app_context():
        db.init_db()
    return app
