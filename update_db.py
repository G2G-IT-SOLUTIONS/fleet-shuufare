from app.database import get_session
from app.models import SystemConfig

with next(get_session()) as session:
    conf = session.get(SystemConfig, "LATEST_ORDERS_SYNC_DAYS")
    if conf:
        conf.value = "1"
        session.add(conf)
        session.commit()
        print("Updated LATEST_ORDERS_SYNC_DAYS to 1")
    else:
        print("Config not found")
