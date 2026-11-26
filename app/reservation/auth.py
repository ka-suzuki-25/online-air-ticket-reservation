"""Login, logout and the session checks used by every protected page.

Session contract used across the whole app:
    session['user_type']    -> 'customer' or 'staff'
    session['username']     -> customer email, or staff username
    session['airline_name'] -> staff only
"""
import functools
import hashlib

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from .sql import query

bp = Blueprint("auth", __name__)


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def customer_required(view):
    """Allow only logged-in customers. Re-checks the database every time, so a
    faked cookie or a deleted account cannot get through."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_type") != "customer":
            flash("Please log in as a customer to use that page.", "error")
            return redirect(url_for("auth.login"))
        row = query("SELECT email FROM Customer WHERE email = %s",
                    (session.get("username"),), one=True)
        if row is None:
            session.clear()
            flash("Please log in again.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def staff_required(view):
    """Allow only logged-in airline staff, and refresh which airline they
    work for straight from the database on every request."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_type") != "staff":
            flash("Please log in as airline staff to use that page.", "error")
            return redirect(url_for("auth.login"))
        row = query("SELECT airline_name FROM Staff WHERE username = %s",
                    (session.get("username"),), one=True)
        if row is None:
            session.clear()
            flash("Please log in again.", "error")
            return redirect(url_for("auth.login"))
        session["airline_name"] = row["airline_name"]
        return view(*args, **kwargs)
    return wrapped


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        user_type = request.form.get("user_type", "")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        row = None
        if user_type == "customer":
            row = query(
                "SELECT email FROM Customer WHERE email = %s AND password = %s",
                (username, md5(password)), one=True)
        elif user_type == "staff":
            row = query(
                "SELECT username, airline_name FROM Staff "
                "WHERE username = %s AND password = %s",
                (username, md5(password)), one=True)

        if row:
            session.clear()
            session["user_type"] = user_type
            if user_type == "customer":
                session["username"] = row["email"]
                return redirect(url_for("customer.home"))
            session["username"] = row["username"]
            session["airline_name"] = row["airline_name"]
            return redirect(url_for("staff.home"))

        flash("Login failed: wrong username or password.", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return render_template("goodbye.html")
