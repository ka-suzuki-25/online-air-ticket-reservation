
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session
)

from ..database import get_db


staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/ratings")
def flight_ratings():

    # Require an authenticated user.
    user_id = session.get("user_id")

    if not user_id:
        flash("Please sign in to access the staff dashboard.", "error")
        return redirect(url_for("auth.login"))

    db = get_db()

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, first_name, role, airline
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )
        user = cursor.fetchone()

    # Verify that the account still exists and has the staff role.
    if user is None or user["role"] != "staff":
        session.clear()
        flash("You are not authorized to access the staff dashboard.", "error")
        return redirect(url_for("home"))

    airline = user["airline"]

    if not airline:
        flash("Your staff account has no airline assigned.", "error")
        return redirect(url_for("home"))

    # Retrieve flights belonging to this staff member's airline.
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                f.airline_name,
                f.flight_number,
                f.dep_datetime,
                f.dep_airport,
                f.arr_airport,
                f.arr_datetime,
                COUNT(r.rating) AS review_count,
                ROUND(AVG(r.rating), 2) AS average_rating
            FROM flights AS f
            LEFT JOIN reviews AS r
                ON r.airline_name = f.airline_name
                AND r.flight_number = f.flight_number
                AND r.dep_datetime = f.dep_datetime
            WHERE LOWER(f.airline_name) = LOWER(?)
            GROUP BY
                f.airline_name,
                f.flight_number,
                f.dep_datetime,
                f.dep_airport,
                f.arr_airport,
                f.arr_datetime
            ORDER BY f.dep_datetime DESC
            """,
            (airline,)
        )
        flights = cursor.fetchall()

    # Retrieve every individual review for each flight.
    flight_details = []

    for flight in flights:
        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    r.rating,
                    r.comment,
                    r.created_at,
                    u.first_name,
                    u.last_name
                FROM reviews AS r
                LEFT JOIN users AS u
                    ON u.email = r.customer_email
                WHERE r.airline_name = ?
                    AND r.flight_number = ?
                    AND r.dep_datetime = ?
                ORDER BY r.created_at DESC
                """,
                (
                    flight["airline_name"],
                    flight["flight_number"],
                    flight["dep_datetime"]
                )
            )
            reviews = cursor.fetchall()

        flight_details.append({
            "flight": flight,
            "reviews": reviews
        })

    return render_template(
        "staff/flight_ratings.html",
        flight_details=flight_details,
        airline=airline,
        staff_name=user["first_name"]
    )
