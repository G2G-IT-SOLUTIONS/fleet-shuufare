from sqlmodel import Session, select
from app.database import engine
from app.models import SystemConfig

def seed_configs():
    default_configs = [
        {"key": "DRIVER_SYNC_LOOKBACK_DAYS", "value": "7", "description": "Delta sync lookback window for driver profiles", "data_type": "int"},
        {"key": "LATEST_ORDERS_SYNC_DAYS", "value": "1", "description": "Lookback window for syncing orders for a specific driver", "data_type": "int"},
        {"key": "DEEP_SCAN_MAX_DAYS", "value": "365", "description": "Maximum search timeframe for Deep Scan orders lookup", "data_type": "int"},
        {"key": "AUTO_SYNC_ENABLED", "value": "true", "description": "Enable automated background order syncing", "data_type": "string"},
        {"key": "AUTO_SYNC_INTERVAL_HOURS", "value": "6", "description": "Interval in hours between automated background runs", "data_type": "int"},
        {"key": "SMS_GATEWAY_PHONE_FORMAT", "value": "canonical", "description": "Phone number format expected by the SMS gateway ('canonical' for +251..., 'international_no_plus' for 251..., 'local_with_zero' for 09..., 'raw_9_digits' for 9...)", "data_type": "string"},
        {"key": "SHIFT_DAY_START", "value": "07:00", "description": "Start time for the Day Shift (Format HH:MM)", "data_type": "string"},
        {"key": "SHIFT_DAY_END", "value": "19:00", "description": "End time for the Day Shift (Format HH:MM)", "data_type": "string"},
        {"key": "SHIFT_NIGHT_START", "value": "19:00", "description": "Start time for the Night Shift (Format HH:MM)", "data_type": "string"},
        {"key": "SHIFT_NIGHT_END", "value": "07:00", "description": "End time for the Night Shift (Format HH:MM)", "data_type": "string"}
    ]

    with Session(engine) as session:
        for conf in default_configs:
            existing = session.get(SystemConfig, conf["key"])
            if not existing:
                session.add(SystemConfig(**conf))
                print(f"Seeded config: {conf['key']}")
        session.commit()
        print("Configuration seeding complete.")

if __name__ == "__main__":
    seed_configs()
