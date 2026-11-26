
from datetime import date, datetime, timedelta

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


spending_bp = Blueprint(
    "spending",
    __name__,
    url_prefix="/spending"
)


def get_logged_in_customer():
    """Return the currently signed-in customer."""

    user_id = session.get("user_id")

    if not user_id:
        return None

    db = get_db()

    return db.execute(
        """
        SELECT id, email, first_name, role
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()


def subtract_one_year(value):
    """Return the same calendar date one year earlier."""

    try:
        return value.replace(year=value.year - 1)
    except ValueError:
        # Handles February 29 when the previous year is not a leap year.
        return value.replace(
            year=value.year - 1,
            day=28
        )


def month_starts_between(start_date, end_date):
    """Return the first day of every month in the selected range."""

    current = start_date.replace(day=1)
    final = end_date.replace(day=1)

    months = []

    while current <= final:
        months.append(current)

        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return months


def get_spending_data(customer_email, start_date, end_date):
    """Calculate spending totals and monthly breakdown for one customer."""

    db = get_db()

    # The upper boundary is exclusive so the entire end date is included.
    end_exclusive = end_date + timedelta(days=1)

    total_row = db.execute(
        """
        SELECT
            COALESCE(SUM(sold_price), 0) AS total_spending,
            COUNT(*) AS ticket_count
        FROM tickets
        WHERE customer_email = ?
          AND purchased_at IS NOT NULL
          AND datetime(purchased_at) >= datetime(?)
          AND datetime(purchased_at) < datetime(?)
        """,
        (
            customer_email,
            start_date.isoformat(),
            end_exclusive.isoformat()
        )
    ).fetchone()

    monthly_rows = db.execute(
        """
        SELECT
            substr(purchased_at, 1, 7) AS spending_month,
            COALESCE(SUM(sold_price), 0) AS monthly_total,
            COUNT(*) AS ticket_count
        FROM tickets
        WHERE customer_email = ?
          AND purchased_at IS NOT NULL
          AND datetime(purchased_at) >= datetime(?)
          AND datetime(purchased_at) < datetime(?)
        GROUP BY substr(purchased_at, 1, 7)
        ORDER BY spending_month
        """,
        (
            customer_email,
            start_date.isoformat(),
            end_exclusive.isoformat()
        )
    ).fetchall()

    monthly_totals = {
        row["spending_month"]: {
            "total": float(row["monthly_total"]),
            "ticket_count": row["ticket_count"]
        }
        for row in monthly_rows
    }

    monthly_breakdown = []

    for month_start in month_starts_between(start_date, end_date):
        month_key = month_start.strftime("%Y-%m")
        month_data = monthly_totals.get(
            month_key,
            {"total": 0.0, "ticket_count": 0}
        )

        monthly_breakdown.append({
            "month": month_start.strftime("%B %Y"),
            "total": month_data["total"],
            "ticket_count": month_data["ticket_count"]
        })

    return {
        "total": float(total_row["total_spending"]),
        "ticket_count": total_row["ticket_count"],
        "monthly_breakdown": monthly_breakdown
    }


@spending_bp.route("/", methods=["GET"])
def dashboard():
    """Display the customer's spending dashboard."""

    customer = get_logged_in_customer()

    if customer is None:
        flash(
            "Please sign in to view your spending.",
            "error"
        )
        return redirect(url_for("auth.login"))

    if customer["role"] != "customer":
        flash(
            "The spending dashboard is available to customers only.",
            "error"
        )
        return redirect(url_for("home"))

    today = date.today()

    # Default report: previous 12 months through today.
    default_start = subtract_one_year(today)
    default_end = today

    start_value = request.args.get("start_date", "").strip()
    end_value = request.args.get("end_date", "").strip()

    custom_range = bool(start_value or end_value)
    date_error = None

    if custom_range:
        try:
            if not start_value or not end_value:
                raise ValueError(
                    "Please select both a start date and an end date."
                )

            start_date = datetime.strptime(
                start_value,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_value,
                "%Y-%m-%d"
            ).date()

            if start_date > end_date:
                raise ValueError(
                    "The start date cannot be later than the end date."
                )

            if end_date > today:
                raise ValueError(
                    "The end date cannot be in the future."
                )

        except ValueError as error:
            date_error = str(error)

            start_date = default_start
            end_date = default_end

    else:
        start_date = default_start
        end_date = default_end

        # Report for the selected date range.
    report = get_spending_data(
        customer["email"],
        start_date,
        end_date
    )

    # The annual overview always remains the previous 12 months.
    annual_report = get_spending_data(
        customer["email"],
        default_start,
        default_end
    )

    # The six-month overview includes the current month.
    six_month_start = today.replace(day=1)

    for _ in range(5):
        if six_month_start.month == 1:
            six_month_start = date(
                six_month_start.year - 1,
                12,
                1
            )
        else:
            six_month_start = date(
                six_month_start.year,
                six_month_start.month - 1,
                1
            )

    six_month_report = get_spending_data(
        customer["email"],
        six_month_start,
        today
    )

    return render_template(
        "spending/dashboard.html",
        customer=customer,
        report=report,
        annual_report=annual_report,
        six_month_report=six_month_report,
        annual_start=default_start.isoformat(),
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        today=today.isoformat(),
        custom_range=custom_range,
        date_error=date_error
    )

    # The six-month overview includes the current month.
    six_month_start = (
        today.replace(day=1)
    )

    for _ in range(5):
        if six_month_start.month == 1:
            six_month_start = date(
                six_month_start.year - 1,
                12,
                1
            )
        else:
            six_month_start = date(
                six_month_start.year,
                six_month_start.month - 1,
                1
            )

    six_month_end = today

    six_month_report = get_spending_data(
        customer["email"],
        six_month_start,
        six_month_end
    )

    return render_template(
        "spending/dashboard.html",
        customer=customer,
        report=report,
        six_month_report=six_month_report,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        custom_range=custom_range,
        date_error=date_error
    )
