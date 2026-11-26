"""Use case #1 - View Public Info.

Anyone, logged in or not, can search future flights and check flight status.
"""
from flask import Blueprint, render_template, request

from .flights import current_price, flight_status, search_flights, seats_left

bp = Blueprint("public", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/search")
def search():
    """Search future flights: one way, or round trip (we then also look up
    the matching flights coming back)."""
    trip_type = request.args.get("trip_type", "one_way")
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()
    dep_date = request.args.get("dep_date", "").strip()
    return_date = request.args.get("return_date", "").strip()
    searched = bool(request.args)

    outbound = inbound = []
    if searched:
        outbound = search_flights(source, destination, dep_date)
        if trip_type == "round_trip":
            # the return leg is the same search with source and destination swapped
            inbound = search_flights(destination, source, return_date)

    return render_template(
        "search.html",
        searched=searched, trip_type=trip_type, source=source,
        destination=destination, dep_date=dep_date, return_date=return_date,
        outbound=outbound, inbound=inbound,
        current_price=current_price, seats_left=seats_left,
    )


@bp.route("/status")
def status():
    """Check a flight's status by airline name, flight number and a date."""
    airline_name = request.args.get("airline_name", "").strip()
    flight_number = request.args.get("flight_number", "").strip()
    on_date = request.args.get("on_date", "").strip()
    searched = bool(request.args)

    results = []
    if searched:
        results = flight_status(airline_name, flight_number, on_date)

    return render_template(
        "status.html",
        searched=searched, airline_name=airline_name,
        flight_number=flight_number, on_date=on_date, results=results,
    )
