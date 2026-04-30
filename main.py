from fastapi import FastAPI
from fastapi.responses import FileResponse
from database import DB_PATH, create_connection, get_urgent_vehicles, get_driver_safety, get_fleet_costs, get_fleet_summary

app = FastAPI()

@app.get("/")
def dashboard():
    return FileResponse("templates/dashboard.html")

def get_db():
  conn = create_connection(DB_PATH)
  try:
    yield conn
  finally: 
    conn.close()

@app.get("/api/summary")
def get_fleet():
    conn = create_connection(DB_PATH)
    return get_fleet_summary(conn)

@app.get("/api/urgent")
def get_urgent():
    conn = create_connection(DB_PATH)
    return get_urgent_vehicles(conn)

@app.get("/api/safety")
def get_safety():
    conn = create_connection(DB_PATH)
    return get_driver_safety(conn)

@app.get("/api/costs")
def get_costs():
    conn = create_connection(DB_PATH)
    return get_fleet_costs(conn)
