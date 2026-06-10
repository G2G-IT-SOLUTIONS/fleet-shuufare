from app.database import get_session
from app.models import SystemConfig

with next(get_session()) as session:
    configs = session.query(SystemConfig).all()
    updates = {
        "DRIVER_SYNC_LOOKBACK_DAYS": "Delta sync lookback window for driver profiles",
        "LATEST_ORDERS_SYNC_DAYS": "Lookback window for syncing orders for a specific driver",
        "DEEP_SCAN_MAX_DAYS": "Maximum search timeframe for Deep Scan orders lookup",
        "CASH_TRIP_EXPECTED_MARGIN": "Allowed variance in ETB for cash deposits"
    }
    for c in configs:
        if c.key in updates:
            c.description = updates[c.key]
            session.add(c)
    session.commit()
    print("Descriptions updated.")
