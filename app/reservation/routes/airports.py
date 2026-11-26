import pymysql
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..database import get_db

bp = Blueprint("airports", __name__, url_prefix="/staff/airports")


AIRPORT_TYPES = ["domestic", "international", "both"]


@bp.route("/new", methods=["GET", "POST"])
def add_airport():
    if session.get("user_role") != "staff":
        flash("Only airline staff can add airports.", "error")
        return redirect(url_for("hello"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        city = request.form.get("city", "").strip()
        country = request.form.get("country", "").strip()
        airport_type = request.form.get("type", "")

        error = None
        if not all([name, city, country, airport_type]):
            error = "Please fill in all fields."
        elif airport_type not in AIRPORT_TYPES:
            error = "Please choose a valid airport type."
        elif len(name) > 100 or len(city) > 100 or len(country) > 100:
            error = "Each field must be 100 characters or fewer."

        if error is None:
            db = get_db()
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO Airport (name, city, country, type) 
                        VALUES (%s, %s, %s, %s)
                        """, 
                        (name, city, country, airport_type)
                    )
                db.commit()
                flash(f"Airport {name} was added.", "success")
                return redirect(url_for("airports.add_airport"))
            except pymysql.err.IntegrityError:
                # An airport with the same name (primary key) already exists.
                db.rollback()
                error = f"Airport {name} already exists."

        flash(error, "error")

    return render_template("airports/new.html", airport_types=AIRPORT_TYPES)
