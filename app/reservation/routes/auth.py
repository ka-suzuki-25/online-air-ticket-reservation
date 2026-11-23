
import re
import sqlite3

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import generate_password_hash, check_password_hash

from ..database import get_db


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Required-field validation.
        if not all([first_name, last_name, email, password, confirm_password]):
            flash("Please complete all fields.", "error")
            return render_template("auth/register.html")

        # Basic email validation.
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Please enter a valid email address.", "error")
            return render_template("auth/register.html")

        if len(first_name) > 100 or len(last_name) > 100:
            flash("Names must be 100 characters or fewer.", "error")
            return render_template("auth/register.html")

        if len(email) > 254:
            flash("Email address is too long.", "error")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Your password must contain at least 8 characters.", "error")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Your passwords do not match.", "error")
            return render_template("auth/register.html")

        # Hash the password before storing it.
        password_hash = generate_password_hash(password)

        db = get_db()

        try:
            db.execute(
                """
                INSERT INTO users
                (first_name, last_name, email, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    first_name,
                    last_name,
                    email,
                    password_hash,
                    "customer"
                )
            )

            db.commit()

            flash(
                "Your Aurelia Airways account has been created. Please sign in.",
                "success"
            )

            return redirect(url_for("auth.login"))

        except sqlite3.IntegrityError:
            db.rollback()
            flash(
                "An account with this email address already exists.",
                "error"
            )

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return render_template("auth/login.html")

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user is None or not check_password_hash(
            user["password_hash"], password
        ):
            flash("Incorrect email or password.", "error")
            return render_template("auth/login.html")

        # Start a new authenticated session.
        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["first_name"]
        session["user_role"] = user["role"]

        flash(
            f"Welcome back, {user['first_name']}!",
            "success"
        )

        return redirect(url_for("home"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("You have been signed out successfully.", "success")

    return redirect(url_for("home"))
