"""HTML presentation layer. All state-changing forms require a CSRF token."""

import hmac
import secrets

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from .auth import AuthService, ValidationError
from .db import get_db
from .repository import UserRepository

blueprint = Blueprint("web", __name__)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


@blueprint.app_context_processor
def template_helpers():
    return {"csrf_token": csrf_token}


@blueprint.before_request
def protect_forms():
    if request.method == "POST":
        expected = session.get("csrf_token")
        provided = request.form.get("csrf_token", "")
        if not expected or not hmac.compare_digest(expected.encode(), provided.encode()):
            abort(400, description="Хүсэлтийн баталгаажуулалт буруу байна. Хуудсаа шинэчлээд дахин оролдоно уу.")


@blueprint.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@blueprint.get("/")
def index():
    return render_template("index.html", user=current_user())


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    error = None
    status = 200
    if request.method == "POST":
        try:
            AuthService(get_db()).register(
                request.form.get("full_name"), request.form.get("email"), request.form.get("password")
            )
        except ValidationError as failure:
            error, status = str(failure), failure.status_code
        else:
            flash("Бүртгэл амжилттай үүслээ.", "success")
            return redirect(url_for("web.login"), code=303)
    return render_template("register.html", error=error), status


def current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    user = UserRepository(get_db()).find_by_id(user_id)
    if user is None:
        session.clear()
    return user


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user() is not None:
        return redirect(url_for("web.account"))
    error = None
    status = 200
    if request.method == "POST":
        try:
            user = AuthService(get_db()).login(request.form.get("email"), request.form.get("password"))
        except ValidationError as failure:
            error, status = str(failure), failure.status_code
        else:
            session.clear()
            session.permanent = True
            session["user_id"] = user.id
            return redirect(url_for("web.account"), code=303)
    return render_template("login.html", error=error), status


@blueprint.get("/account")
def account():
    user = current_user()
    if user is None:
        return redirect(url_for("web.login"))
    return render_template("account.html", user=user)


@blueprint.post("/logout")
def logout():
    session.clear()
    flash("Системээс гарлаа.", "success")
    return redirect(url_for("web.login"), code=303)
