import sqlite3

DB_PATH = "fleet.db"


# Connecting the sqlite database
def create_connection(db_path):
    sqlite_connection = sqlite3.connect(db_path)
    # Returns rows as dictionaries instead of tuples — easier to serve as JSON in FastAPI
    sqlite_connection.row_factory = sqlite3.Row
    return sqlite_connection


def get_urgent_vehicles(conn):
    """Vehicles needing immediate attention — faults, no oil life, or tire pressure issues."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vehicle_id, label, year, oil_life_pct, active_fault_count,
               tire_pressure_ok, fault_codes_json
        FROM vehicles
        WHERE active_fault_count > 0
           OR oil_life_pct = 0
           OR tire_pressure_ok = 0
        ORDER BY active_fault_count DESC
    """)
    return [dict(row) for row in cursor.fetchall()]


def get_driver_safety(conn):
    """All drivers ordered by safety score — worst first so issues are at the top."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, assigned_vehicle, safety_score,
               harsh_braking_events, harsh_acceleration_events,
               speeding_events, idle_hours_this_month
        FROM driver_behavior
        ORDER BY safety_score ASC
    """)
    return [dict(row) for row in cursor.fetchall()]


def get_fleet_costs(conn):
    """Cost breakdown per vehicle — fuel, maintenance, and repairs year to date."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT label, fuel_cost_mtd, maintenance_cost_ytd, repair_cost_ytd,
               ROUND(fuel_cost_mtd + maintenance_cost_ytd + repair_cost_ytd, 2) AS total_cost_ytd
        FROM vehicle_costs
        ORDER BY total_cost_ytd DESC
    """)
    return [dict(row) for row in cursor.fetchall()]


def get_fleet_summary(conn):
    """High level numbers for the top of the dashboard."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total_vehicles,
            SUM(CASE WHEN active_fault_count > 0 THEN 1 ELSE 0 END) AS vehicles_with_faults,
            SUM(CASE WHEN oil_life_pct = 0 THEN 1 ELSE 0 END) AS overdue_oil_changes,
            SUM(CASE WHEN tire_pressure_ok = 0 THEN 1 ELSE 0 END) AS tire_pressure_issues
        FROM vehicles
    """)
    return dict(cursor.fetchone())
