
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

from ..database import get_db


reviews_bp = Blueprint(
    "reviews",
    __name__,
    url_prefix="/reviews"
)


def get_logged_in_customer():
    """Return the logged-in customer's database record."""

    user_id = session.get("user_id")

    if not user_id:
        return None

    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, first_name, role
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )
        return cursor.fetchone()


@reviews_bp.route("/", methods=["GET"])
def previous_flights():

    customer = get_logged_in_customer()

    if customer is None:
        flash("Please sign in to view your previous flights.", "error")
        return redirect(url_for("auth.login"))

    if customer["role"] != "customer":
        flash("This page is available to customers only.", "error")
        return redirect(url_for("home"))

    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT
                f.airline_name,
                f.flight_number,
                f.dep_datetime,
                f.dep_airport,
                f.arr_airport,
                f.arr_datetime,
                t.ticket_id,
                r.rating,
                r.comment,
                r.created_at AS review_date

            FROM tickets AS t

            JOIN flights AS f
                ON t.airline_name = f.airline_name
                AND t.flight_number = f.flight_number
                AND t.dep_datetime = f.dep_datetime

            LEFT JOIN reviews AS r
                ON r.customer_email = t.customer_email
                AND r.airline_name = f.airline_name
                AND r.flight_number = f.flight_number
                AND r.dep_datetime = f.dep_datetime

            WHERE t.customer_email = ?
                AND LOWER(f.status) = 'completed'
                AND datetime(f.arr_datetime) <= CURRENT_TIMESTAMP

            ORDER BY datetime(f.arr_datetime) DESC
            """,
            (customer["email"],)
        )
        flights = cursor.fetchall()

    return render_template(
        "reviews/previous_flights.html",
        flights=flights
    )


@reviews_bp.route("/submit", methods=["POST"])
def submit_review():

    customer = get_logged_in_customer()

    if customer is None:
        flash("Please sign in before submitting a review.", "error")
        return redirect(url_for("auth.login"))

    if customer["role"] != "customer":
        flash("Only customers can submit flight reviews.", "error")
        return redirect(url_for("home"))

    airline_name = request.form.get("airline_name", "").strip()
    flight_number = request.form.get("flight_number", "").strip()
    dep_datetime = request.form.get("dep_datetime", "").strip()
    comment = request.form.get("comment", "").strip()

    try:
        rating = int(request.form.get("rating", ""))
    except (ValueError, TypeError):
        flash("Please select a valid rating.", "error")
        return redirect(url_for("reviews.previous_flights"))

    if not 1 <= rating <= 5:
        flash("Rating must be between 1 and 5 stars.", "error")
        return redirect(url_for("reviews.previous_flights"))

    if not airline_name or not flight_number or not dep_datetime:
        flash("Invalid flight information.", "error")
        return redirect(url_for("reviews.previous_flights"))

    if not comment:
        flash("Please enter a comment for your review.", "error")
        return redirect(url_for("reviews.previous_flights"))

    if len(comment) > 2000:
        flash("Your comment cannot exceed 2,000 characters.", "error")
        return redirect(url_for("reviews.previous_flights"))

    db = get_db()

    # Verify that this customer purchased a ticket for this flight
    # and that the flight has completed.
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT f.flight_number

            FROM flights AS f

            JOIN tickets AS t
                ON t.airline_name = f.airline_name
                AND t.flight_number = f.flight_number
                AND t.dep_datetime = f.dep_datetime

            WHERE t.customer_email = ?
                AND f.airline_name = ?
                AND f.flight_number = ?
                AND f.dep_datetime = ?
                AND LOWER(f.status) = 'completed'
                AND datetime(f.arr_datetime) <= CURRENT_TIMESTAMP

            LIMIT 1
            """,
            (
                customer["email"],
                airline_name,
                flight_number,
                dep_datetime
            )
        )
        eligible_flight = cursor.fetchone()

    if eligible_flight is None:
        flash(
            "You can only review flights you purchased and completed.",
            "error"
        )
        return redirect(url_for("reviews.previous_flights"))

    try:
        with db.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO reviews (
                    customer_email,
                    airline_name,
                    flight_number,
                    dep_datetime,
                    rating,
                    comment
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    customer["email"],
                    airline_name,
                    flight_number,
                    dep_datetime,
                    rating,
                    comment
                )
            )

        db.commit()

        flash("Thank you! Your flight review has been submitted.", "success")

    except sqlite3.IntegrityError:
        db.rollback()

        flash(
            "You have already reviewed this flight.",
            "error"
        )

    return redirect(url_for("reviews.previous_flights"))
