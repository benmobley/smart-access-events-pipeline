import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

BASE_PATH = Path(__file__).resolve().parents[1] / "data" / "raw"

def generate_households(n=1000):
    df = pd.DataFrame({
        "household_id": range(1, n + 1),
        "region": np.random.choice(["US-Midwest", "US-West", "US-East"], size=n),
        "timezone": "America/Chicago",
    })
    (BASE_PATH / "households").mkdir(parents=True, exist_ok=True)
    df.to_csv(BASE_PATH / "households" / "households.csv", index=False)

def generate_devices(n=3000, households=1000):
    df = pd.DataFrame({
        "device_id": range(1, n + 1),
        "household_id": np.random.randint(1, households + 1, size=n),
        "device_type": np.random.choice(["garage_door", "gate"], size=n),
        "model": np.random.choice(["GDO-100", "GDO-200", "GATE-10"], size=n),
        "firmware_version": np.random.choice(["1.0.0", "1.1.0", "2.0.0"], size=n),
        "installed_at": datetime.now().date().isoformat(),
    })
    (BASE_PATH / "devices").mkdir(parents=True, exist_ok=True)
    df.to_csv(BASE_PATH / "devices" / "devices.csv", index=False)

def generate_access_events(devices=3000, days=7, events_per_day=10):
    rows = []
    now = datetime.now()
    event_counter = 1
    
    for device_id in range(1, devices + 1):
        for d in range(days):
            day = now - timedelta(days=d)
            for _ in range(events_per_day):
                ts = day.replace(hour=np.random.randint(0,24), minute=np.random.randint(0,60))
                rows.append({
                    "event_id": event_counter,
                    "device_id": device_id,
                    "user_id": np.random.randint(1, 5000),
                    "event_type": np.random.choice(["open", "close", "command_failed"], p=[0.45,0.45,0.10]),
                    "trigger_source": np.random.choice(["app", "keypad", "schedule"]),
                    "created_at": ts.isoformat(),
                    "lat": 41.8 + np.random.randn() * 0.1,
                    "lon": -87.6 + np.random.randn() * 0.1,
                })
                event_counter += 1
    df = pd.DataFrame(rows)
    (BASE_PATH / "access_events").mkdir(parents=True, exist_ok=True)
    df.to_csv(BASE_PATH / "access_events" / "access_events.csv", index=False)
    
def generate_device_health(devices=3000, days=7):
    rows = []
    now = datetime.now()

    for device_id in range(1, devices + 1):
        for d in range(days):
            day = now - timedelta(days=d)
            # 1–3 health reports per day
            for _ in range(np.random.randint(1, 4)):
                ts = day.replace(hour=np.random.randint(0,24), minute=np.random.randint(0,60))
                rows.append({
                    "device_id": device_id,
                    "reported_at": ts.isoformat(),
                    "battery_pct": np.clip(np.random.normal(80, 15), 0, 100),
                    "signal_strength_dbm": np.random.normal(-65, 10),
                    "is_online": np.random.rand() > 0.05,  # ~95% online
                })

    df = pd.DataFrame(rows)
    (BASE_PATH / "device_health").mkdir(parents=True, exist_ok=True)
    df.to_csv(BASE_PATH / "device_health" / "device_health.csv", index=False)

if __name__ == "__main__":
    generate_households()
    generate_devices()
    generate_access_events()
    generate_device_health()