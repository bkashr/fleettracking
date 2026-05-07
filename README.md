# Fleet Health Dashboard

A fleet health dashboard that simulates what you'd build using data from the Azuga telematics API and BBL Fleet. 

## What it does

- Surfaces vehicles needing maintenance (fault codes, oil changes, tire pressure)
- Ranks drivers by safety score using Azuga telematics data (harsh braking, speeding, idle time)
- Breaks down fuel and maintenance costs per vehicle
- Filter vehicles by issue type and search drivers by name

## Data sources

| Data | Real source | In this demo |
|------|-------------|--------------|
| Vehicle telematics, fault codes, driver behavior | Azuga API | Mock data mirroring Azuga's response structure |
| Fuel and maintenance costs | BBL Fleet | Mock data in `vehicle_costs` table |

In a real deployment, `seed_data.py` would be replaced by authenticated calls to Guardian's Azuga account.

## Setup

**Requirements:** Python 3.9+

```bash
git clone https://github.com/bkashr/fleettracking
cd fleettracking
pip install -r requirements.txt
python seed_data.py
python -m uvicorn main:app --reload
```

Then open `http://localhost:8000` in your browser.

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/summary` | Fleet-wide counts for the summary cards |
| `GET /api/urgent` | Vehicles with active issues |
| `GET /api/safety` | All drivers ranked by safety score |
| `GET /api/costs` | Cost breakdown per vehicle |
| `GET /api/status?status=faults` | Filter vehicles by issue type (`faults`, `oil`, `tires`) |
| `GET /api/drivers/search?name=derek` | Search drivers by name |

Full interactive API docs available at `http://localhost:8000/docs`
