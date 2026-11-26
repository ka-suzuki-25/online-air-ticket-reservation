"""Airline staff use case #16 - Change Status of flights.

Only staff may reach these pages, and a member of staff may only touch
flights operated by the airline they work for. Both rules are checked
against the database on the server, so editing the form in the browser or
sending a handmade POST does not get around them.
"""
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from .auth import staff_required
from .sql import execute, query

bp = Blueprint("staff", __name__, url_prefix="/staff")

ALLOWED_STATUS = ("on time", "delayed", "canceled")


@bp.route("/")
@staff_required
def home():
    return render_template("staff_home.html")


@bp.route("/change-status", methods=("GET", "POST"))
@staff_required
def change_status():
    airline = session["airline_name"]

    if request.method == "POST":
        flight_number = (request.form.get("flight_number") or "").strip()
        dep_datetime = (request.form.get("dep_datetime") or "").strip()
        new_status = (request.form.get("status") or "").strip()

        if new_status not in ALLOWED_STATUS:
            flash("Choose a valid status.", "error")
        else:
            # the airline comes from the session, never from the form, so a
            # member of staff cannot edit another airline's flight
            changed = execute(
                """
                UPDATE Flight
                   SET status = %s
                 WHERE airline_name  = %s
                   AND flight_number = %s
                   AND dep_datetime  = %s
                """,
                (new_status, airline, flight_number, dep_datetime))
            if changed:
                flash("Flight %s departing %s is now %s."
                      % (flight_number, dep_datetime, new_status), "success")
            else:
                flash("No flight of %s matched that flight number and "
                      "departure time." % airline, "error")
        return redirect(url_for("staff.change_status"))

    flights = query(
        """
        SELECT flight_number, dep_datetime, arr_datetime,
               dep_airport, arr_airport, status
          FROM Flight
         WHERE airline_name = %s
         ORDER BY dep_datetime
        """, (airline,))

    return render_template("change_status.html", flights=flights,
                           airline=airline, statuses=ALLOWED_STATUS)
