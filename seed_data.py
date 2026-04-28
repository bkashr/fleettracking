"""
Generates mock data that mirrors the Azuga telematics API response structure.
In production this would be replaced by authenticated calls to Guardian's Azuga account.

Azuga API reference: https://www.azuga.com/fleet-api
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta

DB_PATH = "fleet.db"

# Guardian Fire Protection runs a mix of service vans and trucks
VEHICLES = [
    {"vehicle_id": "GFP-001", "vin": "1FTBF2B62FEB12345", "label": "Service Van 1",  "make": "Ford",   "model": "Transit",      "year": 2021, "type": "van"},
    {"vehicle_id": "GFP-002", "vin": "1FTBF2B62FEB23456", "label": "Service Van 2",  "make": "Ford",   "model": "Transit",      "year": 2020, "type": "van"},
    {"vehicle_id": "GFP-003", "vin": "1FTBF2B62FEB34567", "label": "Service Van 3",  "make": "Ford",   "model": "Transit",      "year": 2022, "type": "van"},
    {"vehicle_id": "GFP-004", "vin": "3C6UR5DL4FG112233", "label": "Inspection Truck 1", "make": "Ram", "model": "ProMaster",  "year": 2019, "type": "truck"},
    {"vehicle_id": "GFP-005", "vin": "3C6UR5DL4FG223344", "label": "Inspection Truck 2", "make": "Ram", "model": "ProMaster",  "year": 2021, "type": "truck"},
    {"vehicle_id": "GFP-006", "vin": "1GCWGAFG0F1123456", "label": "Heavy Unit 1",   "make": "Chevy",  "model": "Express 2500", "year": 2018, "type": "truck"},
    {"vehicle_id": "GFP-007", "vin": "1GCWGAFG0F1234567", "label": "Heavy Unit 2",   "make": "Chevy",  "model": "Express 2500", "year": 2020, "type": "truck"},
    {"vehicle_id": "GFP-008", "vin": "1FTBF2B62FEB45678", "label": "Service Van 4",  "make": "Ford",   "model": "Transit",      "year": 2023, "type": "van"},
]

DRIVERS = [
    {"driver_id": "DRV-001", "name": "Mike Torres",    "license": "T1234567", "assigned_vehicle": "GFP-001"},
    {"driver_id": "DRV-002", "name": "Sarah Okafor",   "license": "O7654321", "assigned_vehicle": "GFP-002"},
    {"driver_id": "DRV-003", "name": "James Pruitt",   "license": "P2345678", "assigned_vehicle": "GFP-003"},
    {"driver_id": "DRV-004", "name": "Linda Nguyen",   "license": "N3456789", "assigned_vehicle": "GFP-004"},
    {"driver_id": "DRV-005", "name": "Carlos Rivera",  "license": "R4567890", "assigned_vehicle": "GFP-005"},
    {"driver_id": "DRV-006", "name": "Derek Shaw",     "license": "S5678901", "assigned_vehicle": "GFP-006"},
    {"driver_id": "DRV-007", "name": "Amy Hutchins",   "license": "H6789012", "assigned_vehicle": "GFP-007"},
    {"driver_id": "DRV-008", "name": "Tom Weller",     "license": "W7890123", "assigned_vehicle": "GFP-008"},
]

# DTC = Diagnostic Trouble Codes — the actual codes Azuga surfaces from the OBD port
FAULT_CODES = [
    {"code": "P0300", "description": "Random/Multiple Cylinder Misfire", "severity": "critical"},
    {"code": "P0420", "description": "Catalyst System Efficiency Below Threshold", "severity": "warning"},
    {"code": "P0505", "description": "Idle Control System Malfunction", "severity": "warning"},
    {"code": "P0171", "description": "System Too Lean (Bank 1)", "severity": "warning"},
    {"code": "C0035", "description": "Left Front Wheel Speed Sensor Circuit", "severity": "critical"},
    {"code": "P0700", "description": "Transmission Control System Malfunction", "severity": "critical"},
]


def generate_telematics(vehicle: dict) -> dict:
    """
    Mirrors the shape of an Azuga /vehicles/telematics endpoint response.
    Older vehicles get worse health scores to create realistic dashboard variance.
    """
    age = 2024 - vehicle["year"]
    base_odometer = age * random.randint(18000, 26000)

    # Older/higher-mileage vehicles are more likely to have issues
    fault_count = random.choices([0, 1, 2], weights=[60 - age * 5, 30, 10 + age * 3])[0]
    faults = random.sample(FAULT_CODES, min(fault_count, len(FAULT_CODES)))

    last_service_days_ago = random.randint(10, 400)
    miles_since_service = int(last_service_days_ago * random.uniform(40, 80))

    return {
        "vehicle_id": vehicle["vehicle_id"],
        "vin": vehicle["vin"],
        "label": vehicle["label"],
        "make": vehicle["make"],
        "model": vehicle["model"],
        "year": vehicle["year"],
        "type": vehicle["type"],
        "odometer_miles": base_odometer,
        "fuel_level_pct": random.randint(15, 95),
        "engine_hours": round(base_odometer / random.uniform(18, 22), 1),
        "last_gps_ping": (datetime.now() - timedelta(minutes=random.randint(5, 120))).isoformat(),
        "last_service_date": (datetime.now() - timedelta(days=last_service_days_ago)).date().isoformat(),
        "miles_since_last_service": miles_since_service,
        "oil_life_pct": max(0, 100 - int(miles_since_service / 50)),
        "tire_pressure_ok": random.choices([True, False], weights=[85, 15])[0],
        "fault_codes": faults,
        "active_fault_count": len(faults),
    }


def generate_driver_behavior(driver: dict) -> dict:
    """
    Mirrors Azuga's driver scorecard data.
    Derek Shaw (DRV-006) is seeded as a problem driver for demo purposes.
    """
    is_problem_driver = driver["driver_id"] == "DRV-006"

    harsh_braking     = random.randint(18, 35) if is_problem_driver else random.randint(1, 8)
    harsh_accel       = random.randint(15, 28) if is_problem_driver else random.randint(0, 6)
    speeding_events   = random.randint(20, 40) if is_problem_driver else random.randint(0, 5)
    idle_hours        = round(random.uniform(4.0, 8.0) if is_problem_driver else random.uniform(0.5, 3.0), 1)

    # Azuga scores drivers 0-100; we derive it from the event counts
    score = max(0, 100 - harsh_braking * 1.5 - harsh_accel * 1.2 - speeding_events * 0.8 - idle_hours * 2)

    return {
        "driver_id": driver["driver_id"],
        "name": driver["name"],
        "license": driver["license"],
        "assigned_vehicle": driver["assigned_vehicle"],
        "safety_score": round(score, 1),
        "harsh_braking_events": harsh_braking,
        "harsh_acceleration_events": harsh_accel,
        "speeding_events": speeding_events,
        "idle_hours_this_month": idle_hours,
        "total_miles_this_month": random.randint(800, 2200),
        "recorded_at": datetime.now().isoformat(),
    }


def generate_cost_record(vehicle: dict, telematics: dict) -> dict:
    age = 2024 - vehicle["year"]
    return {
        "vehicle_id": vehicle["vehicle_id"],
        "label": vehicle["label"],
        "fuel_cost_mtd": round(random.uniform(280, 620), 2),
        "maintenance_cost_ytd": round(random.uniform(400, 800) + age * random.uniform(150, 350), 2),
        "repair_cost_ytd": round(len(telematics["fault_codes"]) * random.uniform(200, 800), 2),
        "recorded_at": datetime.now().isoformat(),
    }


def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS vehicles;
        DROP TABLE IF EXISTS driver_behavior;
        DROP TABLE IF EXISTS vehicle_costs;

        CREATE TABLE vehicles (
            vehicle_id          TEXT PRIMARY KEY,
            vin                 TEXT,
            label               TEXT,
            make                TEXT,
            model               TEXT,
            year                INTEGER,
            type                TEXT,
            odometer_miles      INTEGER,
            fuel_level_pct      INTEGER,
            engine_hours        REAL,
            last_gps_ping       TEXT,
            last_service_date   TEXT,
            miles_since_last_service INTEGER,
            oil_life_pct        INTEGER,
            tire_pressure_ok    INTEGER,
            active_fault_count  INTEGER,
            fault_codes_json    TEXT
        );

        CREATE TABLE driver_behavior (
            driver_id                   TEXT PRIMARY KEY,
            name                        TEXT,
            license                     TEXT,
            assigned_vehicle            TEXT,
            safety_score                REAL,
            harsh_braking_events        INTEGER,
            harsh_acceleration_events   INTEGER,
            speeding_events             INTEGER,
            idle_hours_this_month       REAL,
            total_miles_this_month      INTEGER,
            recorded_at                 TEXT
        );

        CREATE TABLE vehicle_costs (
            vehicle_id              TEXT PRIMARY KEY,
            label                   TEXT,
            fuel_cost_mtd           REAL,
            maintenance_cost_ytd    REAL,
            repair_cost_ytd         REAL,
            recorded_at             TEXT
        );
    """)

    for vehicle in VEHICLES:
        t = generate_telematics(vehicle)
        cur.execute("""
            INSERT INTO vehicles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            t["vehicle_id"], t["vin"], t["label"], t["make"], t["model"],
            t["year"], t["type"], t["odometer_miles"], t["fuel_level_pct"],
            t["engine_hours"], t["last_gps_ping"], t["last_service_date"],
            t["miles_since_last_service"], t["oil_life_pct"],
            int(t["tire_pressure_ok"]), t["active_fault_count"],
            json.dumps(t["fault_codes"])
        ))

        cost = generate_cost_record(vehicle, t)
        cur.execute("""
            INSERT INTO vehicle_costs VALUES (?,?,?,?,?,?)
        """, (
            cost["vehicle_id"], cost["label"], cost["fuel_cost_mtd"],
            cost["maintenance_cost_ytd"], cost["repair_cost_ytd"], cost["recorded_at"]
        ))

    for driver in DRIVERS:
        d = generate_driver_behavior(driver)
        cur.execute("""
            INSERT INTO driver_behavior VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            d["driver_id"], d["name"], d["license"], d["assigned_vehicle"],
            d["safety_score"], d["harsh_braking_events"], d["harsh_acceleration_events"],
            d["speeding_events"], d["idle_hours_this_month"],
            d["total_miles_this_month"], d["recorded_at"]
        ))

    conn.commit()
    conn.close()
    print(f"Seeded {len(VEHICLES)} vehicles and {len(DRIVERS)} drivers into {DB_PATH}")


if __name__ == "__main__":
    seed_database()
