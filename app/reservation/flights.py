"""Flight lookups shared by the public pages and the customer pages.

Keeping them here means the search box on the public home page and the one
inside the customer area run exactly the same SQL.
"""
from decimal import Decimal

from .sql import query

# If this share of the seats is already sold, the airline adds a surcharge.
DEMAND_THRESHOLD = Decimal("0.60")
DEMAND_SURCHARGE = Decimal("1.25")

# Columns every flight listing shows, plus how many seats are already sold.
_FLIGHT_SELECT = """
    SELECT f.airline_name, f.flight_number, f.dep_datetime, f.arr_datetime,
           f.dep_airport, f.arr_airport, f.status, f.base_price, f.airplane_id,
           dep.city AS dep_city, arr.city AS arr_city,
           p.num_seats,
           (SELECT COUNT(*) FROM Ticket t
             WHERE t.airline_name  = f.airline_name
               AND t.flight_number = f.flight_number
               AND t.dep_datetime  = f.dep_datetime
               AND t.customer_email IS NOT NULL) AS seats_sold
      FROM Flight f
      JOIN Airport  dep ON dep.name = f.dep_airport
      JOIN Airport  arr ON arr.name = f.arr_airport
      JOIN Airplane p   ON p.airline_name = f.airline_name
                       AND p.airplane_id  = f.airplane_id
"""


def search_flights(source="", destination="", dep_date="", future_only=True):
    """Future flights matching a source, a destination and/or a date.

    'source' and 'destination' each match either the airport name or the
    city name, so the user can type JFK or New York.
    """
    where, args = [], []

    if future_only:
        where.append("f.dep_datetime > NOW()")
    if source:
        where.append("(f.dep_airport LIKE %s OR dep.city LIKE %s)")
        args += ["%" + source + "%"] * 2
    if destination:
        where.append("(f.arr_airport LIKE %s OR arr.city LIKE %s)")
        args += ["%" + destination + "%"] * 2
    if dep_date:
        where.append("DATE(f.dep_datetime) = %s")
        args.append(dep_date)

    sql = _FLIGHT_SELECT
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY f.dep_datetime"
    return query(sql, tuple(args))


def flight_status(airline_name="", flight_number="", on_date=""):
    """Status of flights, matched on airline, flight number and a date that
    may be either the departure date or the arrival date."""
    where, args = [], []

    if airline_name:
        where.append("f.airline_name LIKE %s")
        args.append("%" + airline_name + "%")
    if flight_number:
        where.append("f.flight_number LIKE %s")
        args.append("%" + flight_number + "%")
    if on_date:
        where.append("(DATE(f.dep_datetime) = %s OR DATE(f.arr_datetime) = %s)")
        args += [on_date, on_date]

    sql = _FLIGHT_SELECT
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY f.dep_datetime"
    return query(sql, tuple(args))


def get_flight(airline_name, flight_number, dep_datetime):
    """One flight, with its seat count and how many seats are sold."""
    sql = _FLIGHT_SELECT + """
        WHERE f.airline_name  = %s
          AND f.flight_number = %s
          AND f.dep_datetime  = %s
    """
    return query(sql, (airline_name, flight_number, dep_datetime), one=True)


def current_price(flight):
    """Base price, plus 25% once 60% of the seats are sold."""
    base = Decimal(flight["base_price"])
    seats = int(flight["num_seats"] or 0)
    sold = int(flight["seats_sold"] or 0)
    if seats > 0 and Decimal(sold) / Decimal(seats) >= DEMAND_THRESHOLD:
        return (base * DEMAND_SURCHARGE).quantize(Decimal("0.01"))
    return base.quantize(Decimal("0.01"))


def seats_left(flight):
    return int(flight["num_seats"] or 0) - int(flight["seats_sold"] or 0)
