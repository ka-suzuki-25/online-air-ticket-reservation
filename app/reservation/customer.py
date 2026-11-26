"""Customer use cases.

  #5  Customer home page
  #6  View My Flights
  #7  Search for flights
  #8  Purchase tickets
  #9  Cancel Trip
"""
from datetime import datetime
from decimal import Decimal

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from .auth import customer_required
from .database import get_db
from .flights import current_price, get_flight, search_flights, seats_left
from .sql import query

bp = Blueprint("customer", __name__, url_prefix="/customer")


# ----------------------------------------------------------------- #5 home
@bp.route("/")
@customer_required
def home():
    """Customer home page: only customer features, plus the next few trips."""
    email = session["username"]
    me = query("SELECT name FROM Customer WHERE email = %s", (email,), one=True)
    upcoming = query(
        """
        SELECT t.ticket_id, t.airline_name, t.flight_number, t.dep_datetime,
               t.sold_price, f.dep_airport, f.arr_airport, f.status
          FROM Ticket t
          JOIN Flight f ON f.airline_name  = t.airline_name
                       AND f.flight_number = t.flight_number
                       AND f.dep_datetime  = t.dep_datetime
         WHERE t.customer_email = %s
           AND t.dep_datetime > NOW()
         ORDER BY t.dep_datetime
         LIMIT 5
        """,
        (email,))
    return render_template("customer_home.html", me=me, upcoming=upcoming)


# ------------------------------------------------------------ #6 my flights
@bp.route("/my-flights")
@customer_required
def my_flights():
    """Tickets the customer bought. Future flights by default; the form can
    widen it to any date range, source or destination."""
    email = session["username"]
    show = request.args.get("show", "future")
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()

    where = ["t.customer_email = %s"]
    args = [email]

    if show == "future":
        where.append("t.dep_datetime > NOW()")
    elif show == "past":
        where.append("t.dep_datetime <= NOW()")
    if date_from:
        where.append("DATE(t.dep_datetime) >= %s")
        args.append(date_from)
    if date_to:
        where.append("DATE(t.dep_datetime) <= %s")
        args.append(date_to)
    if source:
        where.append("(f.dep_airport LIKE %s OR dep.city LIKE %s)")
        args += ["%" + source + "%"] * 2
    if destination:
        where.append("(f.arr_airport LIKE %s OR arr.city LIKE %s)")
        args += ["%" + destination + "%"] * 2

    rows = query(
        """
        SELECT t.ticket_id, t.airline_name, t.flight_number, t.dep_datetime,
               t.sold_price, t.purchase_datetime,
               f.arr_datetime, f.dep_airport, f.arr_airport, f.status,
               dep.city AS dep_city, arr.city AS arr_city,
               (t.dep_datetime > NOW() + INTERVAL 24 HOUR) AS cancellable
          FROM Ticket t
          JOIN Flight  f   ON f.airline_name  = t.airline_name
                          AND f.flight_number = t.flight_number
                          AND f.dep_datetime  = t.dep_datetime
          JOIN Airport dep ON dep.name = f.dep_airport
          JOIN Airport arr ON arr.name = f.arr_airport
         WHERE """ + " AND ".join(where) + """
         ORDER BY t.dep_datetime
        """,
        tuple(args))

    return render_template("my_flights.html", rows=rows, show=show,
                           date_from=date_from, date_to=date_to,
                           source=source, destination=destination)


# --------------------------------------------------------------- #7 search
@bp.route("/search")
@customer_required
def search():
    """Same search as the public page, but each row gets a Purchase link."""
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
            inbound = search_flights(destination, source, return_date)

    return render_template(
        "customer_search.html",
        searched=searched, trip_type=trip_type, source=source,
        destination=destination, dep_date=dep_date, return_date=return_date,
        outbound=outbound, inbound=inbound,
        current_price=current_price, seats_left=seats_left,
    )


# ------------------------------------------------------------- #8 purchase
@bp.route("/purchase", methods=("GET", "POST"))
@customer_required
def purchase():
    """Buy a ticket for one flight.

    Checks, in order: the flight exists, it is in the future, a seat is free,
    and the card details look valid. The price is the base price plus the
    demand surcharge when the flight is at least 60% sold.
    """
    email = session["username"]
    src = request.form if request.method == "POST" else request.args
    airline_name = (src.get("airline_name") or "").strip()
    flight_number = (src.get("flight_number") or "").strip()
    dep_datetime = (src.get("dep_datetime") or "").strip()

    flight = None
    if airline_name and flight_number and dep_datetime:
        flight = get_flight(airline_name, flight_number, dep_datetime)

    if flight is None:
        flash("That flight could not be found.", "error")
        return redirect(url_for("customer.search"))

    price = current_price(flight)

    if request.method == "POST":
        card_type = (request.form.get("card_type") or "").strip()
        card_number = (request.form.get("card_number") or "").strip()
        name_on_card = (request.form.get("name_on_card") or "").strip()
        card_expiration = (request.form.get("card_expiration") or "").strip()

        error = None
        if flight["dep_datetime"] <= datetime.now():
            error = "That flight has already departed."
        elif card_type not in ("credit", "debit"):
            error = "Choose credit or debit."
        elif not card_number.isdigit() or not (12 <= len(card_number) <= 19):
            error = "Card number must be 12 to 19 digits."
        elif not name_on_card:
            error = "Enter the name on the card."
        elif not card_expiration:
            error = "Enter the card expiration date."
        else:
            try:
                if datetime.strptime(card_expiration, "%Y-%m-%d") < datetime.now():
                    error = "That card has expired."
            except ValueError:
                error = "Card expiration date is not valid."

        if error is None:
            error = _buy(email, flight, price, card_type, card_number,
                         name_on_card, card_expiration)

        if error:
            flash(error, "error")
        else:
            flash("Ticket purchased for %s %s departing %s. You paid $%s."
                  % (flight["airline_name"], flight["flight_number"],
                     flight["dep_datetime"], price), "success")
            return redirect(url_for("customer.my_flights"))

    return render_template("purchase.html", flight=flight, price=price,
                           seats_left=seats_left(flight))


def _buy(email, flight, price, card_type, card_number, name_on_card,
         card_expiration):
    """Do the purchase inside one transaction.

    Re-counts the sold seats with the rows locked, so two people buying the
    last seat at the same moment cannot both succeed. Returns an error
    message, or None when the purchase went through.
    """
    conn = get_db()
    key = (flight["airline_name"], flight["flight_number"],
           flight["dep_datetime"])
    try:
        conn.begin()
        with conn.cursor() as cur:
            # lock this flight's tickets and count the sold ones again
            cur.execute(
                """
                SELECT ticket_id, customer_email
                  FROM Ticket
                 WHERE airline_name = %s AND flight_number = %s
                   AND dep_datetime = %s
                 FOR UPDATE
                """, key)
            tickets = cur.fetchall()
            sold = [t for t in tickets if t["customer_email"] is not None]
            free = [t for t in tickets if t["customer_email"] is None]

            if len(sold) >= int(flight["num_seats"]):
                conn.rollback()
                return "Sorry, this flight is now full."

            if any(t["customer_email"] == email for t in sold):
                conn.rollback()
                return "You already hold a ticket for this flight."

            if free:
                # reuse a seat that was never sold, or was cancelled
                cur.execute(
                    """
                    UPDATE Ticket
                       SET customer_email = %s, sold_price = %s,
                           card_type = %s, card_number = %s,
                           name_on_card = %s, card_expiration = %s,
                           purchase_datetime = NOW()
                     WHERE ticket_id = %s
                    """,
                    (email, price, card_type, card_number, name_on_card,
                     card_expiration, free[0]["ticket_id"]))
            else:
                cur.execute("SELECT COALESCE(MAX(ticket_id), 1000) + 1 AS nid "
                            "FROM Ticket")
                new_id = cur.fetchone()["nid"]
                cur.execute(
                    """
                    INSERT INTO Ticket
                        (ticket_id, airline_name, flight_number, dep_datetime,
                         customer_email, sold_price, card_type, card_number,
                         name_on_card, card_expiration, purchase_datetime)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (new_id, flight["airline_name"], flight["flight_number"],
                     flight["dep_datetime"], email, price, card_type,
                     card_number, name_on_card, card_expiration))
        conn.commit()
        return None
    except Exception:
        conn.rollback()
        return "The purchase could not be completed. Please try again."


# --------------------------------------------------------------- #9 cancel
@bp.route("/cancel", methods=("POST",))
@customer_required
def cancel():
    """Give up a ticket, if the flight is more than 24 hours away.

    The ticket row stays, with the customer and payment cleared, so the seat
    goes back on sale for someone else.
    """
    email = session["username"]
    ticket_id = request.form.get("ticket_id", "")

    conn = get_db()
    try:
        conn.begin()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ticket_id, dep_datetime,
                       (dep_datetime > NOW() + INTERVAL 24 HOUR) AS cancellable
                  FROM Ticket
                 WHERE ticket_id = %s AND customer_email = %s
                 FOR UPDATE
                """, (ticket_id, email))
            row = cur.fetchone()

            if row is None:
                conn.rollback()
                flash("That ticket is not one of yours.", "error")
                return redirect(url_for("customer.my_flights"))

            if not row["cancellable"]:
                conn.rollback()
                flash("A ticket can only be cancelled more than 24 hours "
                      "before departure.", "error")
                return redirect(url_for("customer.my_flights"))

            cur.execute(
                """
                UPDATE Ticket
                   SET customer_email = NULL, sold_price = NULL,
                       card_type = NULL, card_number = NULL,
                       name_on_card = NULL, card_expiration = NULL,
                       purchase_datetime = NULL
                 WHERE ticket_id = %s AND customer_email = %s
                """, (ticket_id, email))
        conn.commit()
        flash("Trip cancelled. The seat is available to other customers again.",
              "success")
    except Exception:
        conn.rollback()
        flash("The cancellation could not be completed. Please try again.",
              "error")

    return redirect(url_for("customer.my_flights"))
